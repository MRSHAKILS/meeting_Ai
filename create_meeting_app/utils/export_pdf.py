# create_meeting_app/utils/export_pdf.py

import os
from django.template.loader import render_to_string
from weasyprint import HTML
from create_meeting_app.utils.match_screenshots import match_screenshots
from create_meeting_app.models import Meeting

def export_meeting_summary_pdf(meeting_id):
    meeting = Meeting.objects.get(pk=meeting_id)
    trans   = meeting.transcripts.order_by('created').first()

    # 1) No transcript or no summary?
    if not trans or not trans.summary:
        raise ValueError("No summary available to export.")

    # 2) Split into non-empty lines
    lines = [l.strip() for l in trans.summary.split('\n') if l.strip()]
    if not lines:
        raise ValueError("Summary is empty.")

    # 3) Attempt to match screenshots; if none, fallback to empty list
    try:
        matches = match_screenshots(trans, lines)
    except ValueError:
        matches = []

    # 4) Render PDF HTML
    html = render_to_string('pdf_templates/meeting_summary.html', {
        'meeting': meeting,
        'matches': matches,
    })

    # 5) Ensure output directory exists
    out_dir = os.path.join('media', 'summaries')
    os.makedirs(out_dir, exist_ok=True)

    # 6) Write out PDF
    out_path = os.path.join(out_dir, f"meeting_{meeting_id}.pdf")
    HTML(string=html).write_pdf(out_path)
    return out_path
