"""
Prompt template for Technical Explanation generation with audience-adaptive structure.
"""

def build_technical_prompt(user_prompt: str, tone: str, audience: str, length: str) -> str:
    """
    Constructs an audience-calibrated prompt for technical explanations.
    """
    is_beginner = audience.lower() in ["beginner", "student", "general audience"]

    if is_beginner:
        output_format = """# [Topic Name]: Technical Overview

## 1. Simple Definition
[Clear, jargon-free explanation with an intuitive real-world analogy]

## 2. How It Works
[Step-by-step conceptual workflow explained in accessible terms]

## 3. Practical Example
[Concrete walkthrough of how this is used in practice]

## 4. Key Advantages
[Bullet points highlighting core benefits]

## 5. Limitations & Challenges
[Points discussing drawbacks or things to watch out for]

## 6. Summary / Key Takeaways
[Concise recap of the most essential points]"""
        guidance = """- Target beginner/student level: Use intuitive analogies, define any necessary technical terms gently, and avoid unnecessary jargon.
- Emphasize foundational mechanics, practical examples, and high-level clarity."""
    else:
        output_format = """# [Topic Name]: Technical Architecture & Analysis

## 1. Architectural Overview & Fundamentals
[Precise technical definition, specifications, and underlying paradigm]

## 2. Internal Mechanics & Implementation
[Deep-dive into components, data flow, protocols, or algorithmic logic]

## 3. Practical Code / Implementation Concept
[Concrete code snippet, configuration, or structural pseudocode demonstrating usage]

## 4. Performance & Architectural Trade-offs
[Critical analysis of latency, complexity, scalability, and edge cases]

## 5. Best Practices & Production Guidelines
[Industry-standard deployment or development practices]"""
        guidance = """- Target professional/technical expert level: Leverage formal domain terminology, discuss architectural trade-offs, and detail implementation concerns.
- Include precise algorithmic/system principles and code/config examples where appropriate."""

    prompt = f"""Role:
You are a distinguished computer science educator, software architect, and technical communicator.

Task:
Provide a lucid, accurate, and audience-tailored technical explanation of the requested topic.

Content Type:
TECHNICAL EXPLANATION

Audience:
{audience}

Tone:
{tone}

Length:
{length} (Scale detail, depth of examples, and explanation thoroughness based on this setting)

User Request:
{user_prompt}

Audience Guidance:
{guidance}

Requirements:
1. Adhere strictly to the requested audience ({audience}) and tone ({tone}).
2. Format cleanly using Markdown with distinct headings and bullet points.
3. Ensure accuracy and avoid hallucinated facts or invalid syntax.
4. Scale depth appropriately to the length constraint ({length}).

Output Format:
{output_format}
"""
    return prompt.strip()
