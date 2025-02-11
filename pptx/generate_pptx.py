from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# Create a presentation object
prs = Presentation()

# Define a consistent theme
def add_title(slide, title_text, font_size=44):
    title = slide.shapes.title
    title.text = title_text
    title.text_frame.paragraphs[0].font.size = Pt(font_size)
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

def add_content(slide, content_text, font_size=24):
    content = slide.placeholders[1]
    content.text = content_text
    content.text_frame.paragraphs[0].font.size = Pt(font_size)
    content.text_frame.paragraphs[0].font.color.rgb = RGBColor(0x00, 0x00, 0x00)

# Slide 1: Title Slide
slide_1 = prs.slides.add_slide(prs.slide_layouts[0])
add_title(slide_1, "Web Application Firewall in Python")
subtitle = slide_1.placeholders[1]
subtitle.text = "Securing Web Applications with Custom WAF\nYour Name\nDate"
subtitle.text_frame.paragraphs[0].font.size = Pt(32)
subtitle.text_frame.paragraphs[0].font.color.rgb = RGBColor(0x00, 0x00, 0x00)
subtitle.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

# Slide 2: Introduction
slide_2 = prs.slides.add_slide(prs.slide_layouts[1])
add_title(slide_2, "Introduction", font_size=36)
content_text = (
    "A Web Application Firewall (WAF) is a security system designed to "
    "protect web applications by filtering and monitoring HTTP traffic "
    "between a web application and the Internet. It helps prevent attacks "
    "such as SQL injection, cross-site scripting (XSS), and other OWASP Top Ten vulnerabilities.\n\n"
    "Importance of WAF:\n"
    "- Protects sensitive data\n"
    "- Mitigates security risks\n"
    "- Enhances application security"
)
add_content(slide_2, content_text)

# Slide 3: Objectives
slide_3 = prs.slides.add_slide(prs.slide_layouts[1])
add_title(slide_3, "Objectives", font_size=36)
content_text = (
    "The main objectives of our WAF project are:\n"
    "• Prevent SQL Injection\n"
    "• Prevent XSS Attacks\n"
    "• Prevent SSRF and SSTI\n"
    "• Implement Rate Limiting\n"
    "• Detect and Block Bots\n"
    "• Address Other OWASP Top Ten Protections"
)
add_content(slide_3, content_text)

# Slide 4: Architecture
slide_4 = prs.slides.add_slide(prs.slide_layouts[1])
add_title(slide_4, "Architecture", font_size=36)
content_text = (
    "The WAF architecture is designed to inspect and filter incoming HTTP requests "
    "before they reach the backend server. It includes modules for detecting and blocking "
    "various types of attacks.\n\n"
    "Architecture Overview:\n"
    "- HTTP Request Flow: Client -> WAF -> Backend Server\n"
    "- Detection Modules: SQL Injection, XSS, SSRF, SSTI, etc.\n"
    "- Response Handling: Block malicious requests, forward legitimate requests"
)
add_content(slide_4, content_text)

# Slide 5: Modules
slide_5 = prs.slides.add_slide(prs.slide_layouts[1])
add_title(slide_5, "Modules", font_size=36)
content_text = (
    "Our WAF consists of several detection modules:\n"
    "• SQL Injection Detection\n"
    "• XSS Detection\n"
    "• SSRF Detection\n"
    "• SSTI Detection\n"
    "• Rate Limiting\n"
    "• Anti-Bot Detection\n"
    "• Path Traversal Detection\n"
    "• XXE Detection\n"
    "• OS Command Injection Detection\n"
    "• CRLF Injection Detection"
)
add_content(slide_5, content_text)

# Slide 6: Detailed Implementation
slide_6 = prs.slides.add_slide(prs.slide_layouts[1])
add_title(slide_6, "Detailed Implementation", font_size=36)
content_text = (
    "Here is a brief overview of the implementation details for each module:\n\n"
    "• SQL Injection Detection: Uses regex patterns to detect SQL keywords in requests.\n"
    "• XSS Detection: Scans for common XSS payloads in request parameters and bodies.\n"
    "• SSRF Detection: Blocks requests to internal addresses.\n"
    "• SSTI Detection: Inspects templates for server-side template injection patterns.\n"
    "• Rate Limiting: Limits the number of requests per minute per IP address.\n"
    "• Anti-Bot Detection: Blocks requests from known bot user-agents and excessive request rates."
)
add_content(slide_6, content_text)

# Slide 7: Advanced Features
slide_7 = prs.slides.add_slide(prs.slide_layouts[1])
add_title(slide_7, "Advanced Features", font_size=36)
content_text = (
    "In addition to the basic detection modules, our WAF includes several advanced features:\n\n"
    "• Multiple Log Files: Separate logs for informational, warning, and error messages.\n"
    "• Beautiful Error Page: Renders an HTML error page when a malicious request is detected."
)
add_content(slide_7, content_text)

# Slide 8: Demo
slide_8 = prs.slides.add_slide(prs.slide_layouts[1])
add_title(slide_8, "Demo", font_size=36)
content_text = (
    "Running the WAF:\n"
    "1. Start the WAF using the command: `python waf.py`\n"
    "2. Configure the backend server address in the WAF script.\n\n"
    "Example of blocking a malicious request:\n"
    "• A request containing an SQL injection attempt will be blocked and the user will see the error page."
)
add_content(slide_8, content_text)

# Slide 9: Conclusion
slide_9 = prs.slides.add_slide(prs.slide_layouts[1])
add_title(slide_9, "Conclusion", font_size=36)
content_text = (
    "In conclusion, our Web Application Firewall provides robust protection against "
    "a variety of web application attacks, ensuring the security and integrity of web applications.\n\n"
    "Future improvements:\n"
    "• Adding support for more attack vectors.\n"
    "• Enhancing detection algorithms.\n"
    "• Integrating with existing security tools."
)
add_content(slide_9, content_text)

# Slide 10: Questions
slide_10 = prs.slides.add_slide(prs.slide_layouts[1])
add_title(slide_10, "Questions", font_size=36)
content_text = "Thank you for your attention.\nAny questions?"
add_content(slide_10, content_text)

# Save the presentation
prs.save('WAF_Presentation.pptx')
