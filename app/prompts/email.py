"""
Prompt template for Professional Email generation.
"""

def build_email_prompt(user_prompt: str, tone: str, audience: str, length: str) -> str:
    """
    Constructs a highly structured prompt for professional email generation.
    """
    output_format = """Subject: [Concise and relevant subject line]

Dear [Recipient Name / Title],

[Introduction - State the purpose of the email clearly and contextually]

[Main Message - Well-organized paragraphs addressing key points or requests]

[Closing - Professional call to action or next steps]

Sincerely,
[Your Name]
[Your Title / Contact Information]"""

    prompt = f"""Role:
You are an expert executive communication specialist and professional email drafting assistant.

Task:
Generate a well-crafted, contextually appropriate email based on the user's request.

Content Type:
EMAIL

Audience:
{audience}

Tone:
{tone}

Length:
{length} (Adjust paragraph depth and detail according to this constraint)

User Request:
{user_prompt}

Requirements:
1. Follow the requested EMAIL content type strictly.
2. Structure the email with a clear subject line, appropriate greeting, purpose-driven introduction, articulate main body, polite closing, and signature block.
3. Do NOT invent real personal details, names, addresses, or phone numbers. Use placeholders such as [Your Name], [Company Name], or [Date] when specific details are not provided by the user.
4. Adapt vocabulary and formality strictly according to the selected audience ({audience}) and tone ({tone}).
5. Honor the selected length ({length}) - keep concise for 'Short', balanced for 'Medium', and thorough for 'Detailed'.
6. Do not include markdown code block backticks around the email unless specifically requested. Output pure email text.

Output Format:
{output_format}
"""
    return prompt.strip()
