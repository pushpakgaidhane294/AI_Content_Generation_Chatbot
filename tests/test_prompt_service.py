import pytest
from app.services.prompt_service import PromptService
from app.schemas import ContentType, ToneType, AudienceType, LengthType


def test_build_email_prompt_structure():
    """Verify email prompt includes necessary executive email structural constraints."""
    user_prompt = "Requesting sick leave for tomorrow due to fever."
    prompt = PromptService.build_email_prompt(
        user_prompt=user_prompt,
        tone="Professional",
        audience="Professional",
        length="Short"
    )

    assert "Role:" in prompt
    assert "Task:" in prompt
    assert "Content Type:\nEMAIL" in prompt
    assert "Subject:" in prompt
    assert "Requirements:" in prompt
    assert "Do NOT invent real personal details" in prompt
    assert user_prompt in prompt


def test_build_report_prompt_structure():
    """Verify report prompt enforces markdown report sections."""
    user_prompt = "Market analysis of renewable energy adoption in 2026."
    prompt = PromptService.build_report_prompt(
        user_prompt=user_prompt,
        tone="Academic",
        audience="Professional",
        length="Detailed"
    )

    assert "Role:" in prompt
    assert "REPORT" in prompt
    assert "Executive Summary" in prompt
    assert "Objective & Scope" in prompt
    assert "Conclusion & Recommendations" in prompt
    assert user_prompt in prompt


def test_build_technical_prompt_beginner():
    """Verify technical prompt adapts for beginners with analogies and simple definition."""
    user_prompt = "Explain quantum computing."
    prompt = PromptService.build_technical_prompt(
        user_prompt=user_prompt,
        tone="Simple",
        audience="Beginner",
        length="Medium"
    )

    assert "TECHNICAL EXPLANATION" in prompt
    assert "Simple Definition" in prompt
    assert "How It Works" in prompt
    assert "Practical Example" in prompt
    assert "Key Advantages" in prompt
    assert "analogies" in prompt.lower()


def test_build_technical_prompt_expert():
    """Verify technical prompt adapts for technical experts with architecture and trade-offs."""
    user_prompt = "Explain distributed consensus algorithms (Raft/Paxos)."
    prompt = PromptService.build_technical_prompt(
        user_prompt=user_prompt,
        tone="Formal",
        audience="Technical Expert",
        length="Detailed"
    )

    assert "TECHNICAL EXPLANATION" in prompt
    assert "Architectural Overview" in prompt
    assert "Trade-offs" in prompt or "trade-offs" in prompt
    assert "Implementation" in prompt


def test_build_general_prompt():
    """Verify general prompt enforces tone, audience, and length constraints."""
    user_prompt = "Give three productivity habits for software engineers."
    prompt = PromptService.build_general_prompt(
        user_prompt=user_prompt,
        tone="Friendly",
        audience="Student",
        length="Short"
    )

    assert "GENERAL CONTENT" in prompt
    assert "Friendly" in prompt
    assert "Student" in prompt
    assert "Short" in prompt
    assert user_prompt in prompt


def test_prompt_service_routing():
    """Verify PromptService.build_prompt properly routes between types."""
    email_p = PromptService.build_prompt("write email", ContentType.EMAIL)
    assert "EMAIL" in email_p
    assert "Subject:" in email_p

    report_p = PromptService.build_prompt("write report", ContentType.REPORT)
    assert "REPORT" in report_p
    assert "Executive Summary" in report_p

    tech_p = PromptService.build_prompt("write explanation", ContentType.TECHNICAL_EXPLANATION)
    assert "TECHNICAL EXPLANATION" in tech_p


def test_transformation_prompts():
    """Verify transform prompt builders generate appropriate contextual modification instructions."""
    prev = "Here is an initial draft of the email."
    
    improve_p = PromptService.build_improve_prompt(
        previous_response=prev,
        content_type="EMAIL",
        tone="Professional",
        audience="Professional",
        length="Medium"
    )
    assert "editorial consultant" in improve_p
    assert prev in improve_p

    shorten_p = PromptService.build_shorten_prompt(
        previous_response=prev,
        content_type="EMAIL",
        tone="Professional",
        audience="Professional"
    )
    assert "Condense" in shorten_p or "condense" in shorten_p
    assert prev in shorten_p

    expand_p = PromptService.build_expand_prompt(
        previous_response=prev,
        content_type="EMAIL",
        tone="Professional",
        audience="Professional"
    )
    assert "expand" in expand_p.lower()
    assert prev in expand_p
