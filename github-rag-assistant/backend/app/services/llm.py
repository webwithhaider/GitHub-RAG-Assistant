"""LLM call wrapper. Provider is chosen via LLM_PROVIDER in settings."""
from app.config import get_settings
from app.models.schemas import Citation
from app.services.prompts import SYSTEM_PROMPT, build_user_prompt

settings = get_settings()


def _call_groq(system: str, user: str) -> str:
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.1,
    )
    return resp.choices[0].message.content


def _call_openai(system: str, user: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.1,
    )
    return resp.choices[0].message.content


def generate_answer(question: str, chunks: list[dict]):
    user_prompt = build_user_prompt(question, chunks)

    if settings.LLM_PROVIDER == "groq":
        answer = _call_groq(SYSTEM_PROMPT, user_prompt)
    elif settings.LLM_PROVIDER == "openai":
        answer = _call_openai(SYSTEM_PROMPT, user_prompt)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {settings.LLM_PROVIDER}")

    citations = [
        Citation(file=c["file"], start_line=c["start_line"], end_line=c["end_line"])
        for c in chunks
    ]
    return answer, citations
