"""
Prompt Engineering Service.
Constructs structured, persona-driven prompts with Role, Task, Context,
Audience conditioning, Tone control, Length specifications, Requirements,
and strict Output Formatting.
"""

from app.schemas import ContentType, ToneType, AudienceType, LengthType
from app.prompts.email import build_email_prompt
from app.prompts.report import build_report_prompt
from app.prompts.technical import build_technical_prompt
from app.prompts.general import build_general_prompt


class PromptService:
    """
    Centralized service for building engineered prompts.
    Enforces prompt engineering best practices without exposing raw user queries.
    """

    @staticmethod
    def build_prompt(
        user_prompt: str,
        content_type: str | ContentType,
        tone: str | ToneType = ToneType.PROFESSIONAL,
        audience: str | AudienceType = AudienceType.GENERAL_AUDIENCE,
        length: str | LengthType = LengthType.MEDIUM,
    ) -> str:
        """
        Routes generation requests to specialized prompt construction functions
        based on the designated ContentType.
        """
        # Convert enums to string values
        ct_val = content_type.value if hasattr(content_type, "value") else str(content_type)
        t_val = tone.value if hasattr(tone, "value") else str(tone)
        a_val = audience.value if hasattr(audience, "value") else str(audience)
        l_val = length.value if hasattr(length, "value") else str(length)

        ct_upper = ct_val.strip().upper()

        if ct_upper == ContentType.EMAIL.value:
            return PromptService.build_email_prompt(user_prompt, t_val, a_val, l_val)
        elif ct_upper == ContentType.REPORT.value:
            return PromptService.build_report_prompt(user_prompt, t_val, a_val, l_val)
        elif ct_upper == ContentType.TECHNICAL_EXPLANATION.value:
            return PromptService.build_technical_prompt(user_prompt, t_val, a_val, l_val)
        else:
            return PromptService.build_general_prompt(user_prompt, t_val, a_val, l_val)

    @staticmethod
    def build_email_prompt(user_prompt: str, tone: str, audience: str, length: str) -> str:
        return build_email_prompt(user_prompt, tone, audience, length)

    @staticmethod
    def build_report_prompt(user_prompt: str, tone: str, audience: str, length: str) -> str:
        return build_report_prompt(user_prompt, tone, audience, length)

    @staticmethod
    def build_technical_prompt(user_prompt: str, tone: str, audience: str, length: str) -> str:
        return build_technical_prompt(user_prompt, tone, audience, length)

    @staticmethod
    def build_general_prompt(user_prompt: str, tone: str, audience: str, length: str) -> str:
        return build_general_prompt(user_prompt, tone, audience, length)

    @staticmethod
    def build_regenerate_prompt(
        user_prompt: str,
        content_type: str,
        tone: str,
        audience: str,
        length: str,
        previous_response: str | None = None
    ) -> str:
        """
        Engineered prompt to produce a fresh, alternative variation of the content
        while respecting original constraints.
        """
        base_prompt = PromptService.build_prompt(user_prompt, content_type, tone, audience, length)
        context_block = ""
        if previous_response:
            context_block = f"""
Previous Version for Reference:
\"\"\"
{previous_response}
\"\"\"
Instruction: Generate a fresh, alternative iteration with novel phrasing and varied sentence flow while strictly preserving the intent, tone ({tone}), and format requirements."""

        return f"""{base_prompt}
{context_block}
"""

    @staticmethod
    def build_improve_prompt(
        previous_response: str,
        content_type: str,
        tone: str,
        audience: str,
        length: str,
        user_prompt: str = ""
    ) -> str:
        """
        Engineered prompt to refine, polish, and enhance clarity and impact.
        """
        return f"""Role:
You are an expert editorial consultant, communication strategist, and text optimizer.

Task:
Elevate and polish the draft content below. Enhance vocabulary, flow, clarity, and persuasiveness while preserving its underlying meaning and format.

Content Type:
{content_type}

Target Audience:
{audience}

Desired Tone:
{tone}

Target Length:
{length}

Original User Request (Context):
{user_prompt if user_prompt else "Enhance the provided content."}

Draft Content to Improve:
\"\"\"
{previous_response}
\"\"\"

Refinement Requirements:
1. Preserve all vital factual information, placeholders, and primary objectives.
2. Sharpen sentence structure, eliminate redundancy, and improve readability.
3. Match the required tone ({tone}) and audience vocabulary ({audience}) seamlessly.
4. Maintain proper Markdown layout and formatting.
5. Do not include meta-commentary (e.g., do not say 'Here is the improved version:'). Return the polished content directly.
"""

    @staticmethod
    def build_shorten_prompt(
        previous_response: str,
        content_type: str,
        tone: str,
        audience: str,
        user_prompt: str = ""
    ) -> str:
        """
        Engineered prompt to condense content into high-impact brevity.
        """
        return f"""Role:
You are an executive editor specializing in conciseness, precision editing, and distillation.

Task:
Condense and shorten the content below into a punchy, succinct version while retaining all critical core messages and structural integrity.

Content Type:
{content_type}

Target Audience:
{audience}

Desired Tone:
{tone}

Original User Request (Context):
{user_prompt if user_prompt else "Condense the provided content."}

Original Content:
\"\"\"
{previous_response}
\"\"\"

Condensation Requirements:
1. Drastically reduce word count by eliminating fluff, filler, and secondary details.
2. Retain all primary takeaways, necessary structural elements (e.g. subject line or key headers), and placeholders.
3. Ensure every remaining sentence is crisp, clear, and impactful.
4. Maintain the requested tone ({tone}).
5. Return ONLY the condensed content directly with no conversational preambles.
"""

    @staticmethod
    def build_expand_prompt(
        previous_response: str,
        content_type: str,
        tone: str,
        audience: str,
        user_prompt: str = ""
    ) -> str:
        """
        Engineered prompt to enrich content with comprehensive details, analysis, and examples.
        """
        return f"""Role:
You are an authoritative subject-matter specialist and in-depth content architect.

Task:
Substantially expand and enrich the content below by introducing comprehensive insights, detailed context, illustrative examples, and thorough elaboration.

Content Type:
{content_type}

Target Audience:
{audience}

Desired Tone:
{tone}

Original User Request (Context):
{user_prompt if user_prompt else "Expand the provided content."}

Current Content:
\"\"\"
{previous_response}
\"\"\"

Expansion Requirements:
1. Deepen each section with meaningful analytical points, concrete examples, or explanatory nuance.
2. Maintain strong coherence, logical transitions, and cohesive narrative flow.
3. Follow the target audience level ({audience}) and tone ({tone}).
4. Retain all structural sections appropriate for {content_type}.
5. Do not invent personal data.
6. Return ONLY the expanded content formatted in clean Markdown without meta-commentary.
"""
