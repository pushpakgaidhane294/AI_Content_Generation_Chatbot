"""
Prompt template for Structured Report generation.
"""

def build_report_prompt(user_prompt: str, tone: str, audience: str, length: str) -> str:
    """
    Constructs a structured prompt for business and academic report generation.
    """
    output_format = """# [Report Title]

## 1. Executive Summary / Introduction
[Brief contextual overview and background]

## 2. Objective & Scope
[Clear statement of the report's goals and scope of evaluation]

## 3. Main Findings & Discussion
[Key observations, structured subheadings, or data points where applicable]

## 4. Strategic Analysis / Impact
[Analytical assessment, challenges, and core insights]

## 5. Conclusion & Recommendations
[Actionable takeaways, conclusions, and strategic recommendations]"""

    prompt = f"""Role:
You are a senior analyst and technical report specialist capable of synthesizing complex concepts into clear, actionable, and structured reports.

Task:
Generate an organized, well-formatted, and comprehensive report addressing the user's topic.

Content Type:
REPORT

Audience:
{audience}

Tone:
{tone}

Length:
{length} (Adjust section depth, analytical detail, and paragraph count to match this setting)

User Request:
{user_prompt}

Requirements:
1. Deliver a structured report formatted in clean Markdown with clear headings and logical section progression.
2. Standard sections should include: Title, Executive Summary / Introduction, Objective & Scope, Main Findings / Content, Analysis / Discussion, and Conclusion & Recommendations.
3. Adapt the sub-sections flexibly to fit the specific domain of the user's topic.
4. Align depth, vocabulary, and analytical rigor with the audience ({audience}) and tone ({tone}).
5. Strictly obey the length specification ({length}).
6. Do not fabricate unverified personal data.

Output Format:
{output_format}
"""
    return prompt.strip()
