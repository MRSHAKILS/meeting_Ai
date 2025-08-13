from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from .models import Meeting
from .forms import CreateMeetingForm, JoinMeetingForm
import requests
from django.conf import settings
from django.http   import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from google.cloud import translate_v2 as translate
from create_meeting_app.utils.tts import generate_tts_and_save
from bs4 import BeautifulSoup

from .models import Transcript


def dashboard(request):
    meetings = Meeting.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'meetings': meetings})

def create_meeting(request):
    if request.method == 'POST':
        form = CreateMeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.user = request.user
            meeting.save()
            messages.success(request, 'Meeting created successfully!')
            return redirect('dashboard')
        messages.error(request, 'Error creating meeting. Please check the form.')
    return redirect('dashboard')

def join_meeting(request):
    if request.method == 'POST':
        form = JoinMeetingForm(request.POST)
        if form.is_valid():
            meeting = get_object_or_404(Meeting, pk=form.cleaned_data['meeting_id'], user=request.user)
            meeting.meeting_link = form.cleaned_data['meeting_link']
            meeting.join_time = form.cleaned_data['join_time']
            meeting.joined = False  # reset so scheduler will pick it up
            meeting.save()
            messages.success(request, 'Meeting details saved! Bot will join on time.')
            return redirect('meeting_page', meeting_id=meeting.pk)
        messages.error(request, 'Error saving meeting details.')
    return redirect('dashboard')

def meeting_page(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)

    segments = []
    for transcript in meeting.transcripts.order_by('created'):
        # Each transcript.text has multi speaker segments separated by double newlines
        blocks = transcript.text.split('\n\n')
        for block in blocks:
            if ': ' in block:
                speaker, text = block.split(': ', 1)
            else:
                speaker, text = None, block
            segments.append({
                'speaker': speaker,
                'text': text,
                'created': transcript.created,
            })

    screenshots = meeting.screenshots.order_by('created')

    return render(request, 'meeting_detail.html', {
        'meeting': meeting,
        'segments': segments,
        'screenshots': screenshots,
    })

@require_POST
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, user=request.user)
    meeting.delete()
    return JsonResponse({'status': 'success'})

@csrf_exempt
def transcribe_meeting_view(request, meeting_id):
    if request.method == 'POST':
        call_command('transcribe_meeting', str(meeting_id))
        return redirect('meeting_page', meeting_id=meeting_id)
    return HttpResponse("Invalid request", status=400)

@login_required
@require_POST
def summarize_transcript(request, transcript_id):
    t = get_object_or_404(
        Transcript,
        pk=transcript_id,
        meeting__user=request.user
    )

    # 1. Translate to English if needed
    translated_text = t.translated_text
    if not translated_text:
        client = translate.Client()
        result = client.translate(
            t.text,
            source_language="bn",  # assuming Bangla input
            target_language="en",
            format_="text"
        )
        translated_text = result["translatedText"]
        t.translated_text = translated_text
        t.save(update_fields=["translated_text"])

    # 2. Build the summarization prompt with ENGLISH
    prompt = f"""
You are a highly intelligent AI assistant designed to take unstructured meeting transcripts and produce clear, detailed, and professional summaries.

Your summary must be helpful to someone who didn’t attend the meeting.

Please generate a structured summary **in valid HTML format** using the following structure and tags:

<h3>📝 Topics Discussed</h3>
<ul>
  <li>...</li>
  <li>...</li>
</ul>

<h3>✅ Decisions Made</h3>
<ul>
  <li>...</li>
</ul>

<h3>📌 Action Items</h3>
<ul>
  <li>...</li>
</ul>

<h3>⏳ Deadlines / Next Steps</h3>
<ul>
  <li>...</li>
</ul>

<h3>🧠 Overall Summary</h3>
<p>...</p>

Make sure:
- The HTML is clean and well-formed.
- Don’t use Markdown.
- Use <ul> and <li> tags for lists.
- No <style> tags or inline CSS.

Transcript:
{translated_text}
""".strip()



    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       "llama3-8b-8192",  # or "mixtral-8x7b-32768"
                "messages":    [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens":  256,
            },
            timeout=30,
        )
        resp.raise_for_status()
        summary = resp.json()["choices"][0]["message"]["content"].strip()

        # 3. Save and return the summary
        t.summary = summary
        t.save(update_fields=["summary"])       
        # 4. Generate summary TTS (strip HTML for clean reading)
        plain_summary = BeautifulSoup(t.summary, "html.parser").get_text(separator="\n")
        generate_tts_and_save(
            plain_summary,  # use plain text for TTS
            lang='en',      # 'bn' if Bangla, 'en' if English TTS
            file_field=t.summary_audio,
            instance=t,
            filename=f"summary_{t.id}.mp3"
        )

        t.save(update_fields=["summary_audio"])

        # 5. Return JSON with audio URL
        return JsonResponse({
            "success": True,
            "summary": summary,
            "summary_audio_url": t.summary_audio.url
        })

    except requests.exceptions.HTTPError:
        error_text = resp.text
        print("Groq API error:", resp.status_code, error_text)
        return JsonResponse({"success": False, "error": error_text}, status=500)
    


from create_meeting_app.utils.export_pdf import export_meeting_summary_pdf
from django.http import FileResponse, Http404, HttpResponseBadRequest

@login_required
def download_summary_pdf(request, meeting_id):
    try:
        path = export_meeting_summary_pdf(meeting_id)
        return FileResponse(open(path, 'rb'),
                            as_attachment=True,
                            filename=f"meeting_{meeting_id}.pdf")
    except ValueError as e:
        return HttpResponseBadRequest(f"Cannot generate PDF: {e}")
    except Meeting.DoesNotExist:
        raise Http404("Meeting not found.")
    except FileNotFoundError:
        raise Http404("PDF file not found.")
    except Exception as e:
        return HttpResponseBadRequest(f"Unexpected error: {e}")

