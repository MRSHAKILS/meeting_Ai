import os
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
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

    # Create PDF using ReportLab
    out_dir = os.path.join('media', 'summaries')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"meeting_{meeting_id}.pdf")

    # Create the PDF document
    doc = SimpleDocTemplate(out_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#2E86AB')
    )
    story.append(Paragraph(f"Meeting Summary - {meeting.name}", title_style))
    story.append(Spacer(1, 12))

    # Meeting details
    story.append(Paragraph(f"<b>Date:</b> {meeting.date_created.strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Paragraph(f"<b>Duration:</b> {meeting.duration or 'N/A'}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Summary points
    story.append(Paragraph("Summary Points:", styles['Heading2']))
    story.append(Spacer(1, 12))

    for i, point in enumerate(summary_points, 1):
        # Add summary point
        story.append(Paragraph(f"{i}. {point}", styles['Normal']))
        story.append(Spacer(1, 8))

        # Add screenshot if available
        screenshot_path = matches.get(point)
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                # Resize image to fit page
                img = Image(screenshot_path, width=4*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 12))
            except Exception as e:
                print(f"Could not add screenshot: {e}")

    # Build PDF
    doc.build(story)
    return out_path
