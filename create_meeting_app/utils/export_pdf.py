import os
from django.template.loader import render_to_string
from weasyprint import HTML
from create_meeting_app.utils.match_clip_embeddings import match_summary_to_screenshots
from create_meeting_app.models import Meeting

def export_meeting_summary_pdf(meeting_id):
    meeting = Meeting.objects.get(pk=meeting_id)
    transcript = meeting.transcripts.order_by('created').first()

    if not transcript or not transcript.summary:
        raise ValueError("No summary available to export.")

    summary_points = [l.strip() for l in transcript.summary.split('\n') if l.strip()]
    screenshots = meeting.screenshots.order_by('created')
    screenshot_paths = [s.image_path for s in screenshots]

    matches = match_summary_to_screenshots(summary_points, screenshot_paths)

    # Convert relative paths to absolute file URLs for WeasyPrint
    pdf_data = []
    for point in summary_points:
        screenshot_path = matches.get(point)
        if screenshot_path:
            abs_path = os.path.abspath(screenshot_path)
            file_url = f"file://{abs_path}"
        else:
            file_url = None
        pdf_data.append({'point': point, 'screenshot': file_url})

    html = render_to_string('pdf_templates/meeting_summary.html', {
        'meeting': meeting,
        'pdf_data': pdf_data,
    })

    out_dir = os.path.join('media', 'summaries')
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, f"meeting_{meeting_id}.pdf")
    HTML(string=html).write_pdf(out_path)
    return out_path
