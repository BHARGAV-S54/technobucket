from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
from django.utils import timezone


def generate_inquiry_pdf(inquiry):
    """Generate PDF document for ContactInquiry"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center
    )

    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.blue
    )

    content = []

    # Title
    content.append(Paragraph("Service Inquiry Details", title_style))
    content.append(Spacer(1, 20))

    # Basic Information
    content.append(Paragraph("Basic Information", section_style))

    data = [
        ["Field", "Value"],
        ["Name", inquiry.name],
        ["Email", inquiry.email],
        ["Service", inquiry.service_name or "General Inquiry"],
        ["Status", inquiry.get_status_display()],
        ["Submitted Date", inquiry.created_at.strftime("%B %d, %Y at %I:%M %p")],
    ]

    if inquiry.ip_address:
        data.append(["IP Address", inquiry.ip_address])

    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    content.append(table)
    content.append(Spacer(1, 20))

    # Message Content
    content.append(Paragraph("Message Details", section_style))

    # Parse the message content
    message_lines = inquiry.message.split('\n')
    formatted_message = []

    for line in message_lines:
        if ':' in line and len(line.split(':', 1)) == 2:
            field, value = line.split(':', 1)
            formatted_message.append(f"<b>{field.strip()}:</b> {value.strip()}")
        else:
            formatted_message.append(line)

    message_text = '<br/>'.join(formatted_message)
    content.append(Paragraph(message_text, styles['Normal']))

    # Footer
    content.append(Spacer(1, 30))
    content.append(Paragraph(f"Generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Italic']))

    doc.build(content)
    buffer.seek(0)
    return buffer


def generate_portfolio_order_pdf(order):
    """Generate PDF document for PortfolioOrder"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center
    )

    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.blue
    )

    content = []

    # Title
    content.append(Paragraph("Portfolio Order Details", title_style))
    content.append(Spacer(1, 20))

    # Basic Information
    content.append(Paragraph("Customer Information", section_style))

    data = [
        ["Field", "Value"],
        ["Order ID", f"#{order.id:05d}"],
        ["Full Name", order.full_name],
        ["Email", order.email],
        ["Phone", order.phone or "Not provided"],
        ["Status", order.get_status_display()],
        ["Payment Status", order.get_payment_status_display()],
        ["Amount Paid", f"₹{order.amount_paid}"],
        ["Order Date", order.created_at.strftime("%B %d, %Y at %I:%M %p")],
    ]

    if order.completed_at:
        data.append(["Completed Date", order.completed_at.strftime("%B %d, %Y at %I:%M %p")])

    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    content.append(table)
    content.append(Spacer(1, 20))

    # Profile Links
    content.append(Paragraph("Profile Links", section_style))

    links_data = [
        ["Platform", "URL"],
        ["GitHub", order.github_profile],
        ["LeetCode", order.leetcode_profile],
        ["LinkedIn", order.linkedin_profile],
    ]

    links_table = Table(links_data, colWidths=[2*inch, 4*inch])
    links_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    content.append(links_table)
    content.append(Spacer(1, 20))

    # Skills
    if order.skills:
        content.append(Paragraph("Skills", section_style))
        skills_text = ", ".join(order.skills)
        content.append(Paragraph(skills_text, styles['Normal']))
        content.append(Spacer(1, 20))

    # Project Links
    if order.project_links:
        content.append(Paragraph("Project Links", section_style))
        for i, link in enumerate(order.project_links, 1):
            content.append(Paragraph(f"Project {i}: {link}", styles['Normal']))
        content.append(Spacer(1, 20))

    # Extra Information
    if order.extra_information:
        content.append(Paragraph("Additional Information", section_style))
        content.append(Paragraph(order.extra_information, styles['Normal']))
        content.append(Spacer(1, 20))

    # Footer
    content.append(Spacer(1, 30))
    content.append(Paragraph(f"Generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Italic']))

    doc.build(content)
    buffer.seek(0)
    return buffer