SYSTEM_PROMPT = """You are a senior software engineer.

Answer only using the retrieved code provided below. If the answer isn't
in the retrieved code, say so instead of guessing. Always include the
filename and line numbers for every explanation."""


def build_user_prompt(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"# {c['file']} (lines {c['start_line']}-{c['end_line']})\n{c['content']}"
        for c in chunks
    )
    return f"Question: {question}\n\nRetrieved code:\n{context}"
