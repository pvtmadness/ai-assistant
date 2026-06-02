# app/agents/router.py

def classify_task(user_input: str) -> str:
    """
    Simple heuristic classifier.
    Returns: 'simple' or 'complex'
    """

    keywords_complex = [
        "analyze", "compare", "evaluate", "strategy",
        "why", "how", "implication", "model",
        "system", "improve", "optimize", "build",
        "framework", "architecture"
    ]

    for word in keywords_complex:
        if word in user_input.lower():
            return "complex"

    if len(user_input.split()) > 20:
        return "complex"

    return "simple"


def build_executive_prompt(user_input: str) -> str:
    """
    Enforces executive brief style
    """

    return f"""
You are an executive-level assistant.

Provide a concise, structured executive brief.

Rules:
- Lead with conclusions
- Be clear and direct
- Minimize verbosity
- No rambling
- No unnecessary explanation

User request:
{user_input}
"""


def route_request(user_input: str) -> dict:
    """
    Returns routing decision
    """

    task_type = classify_task(user_input)

    if task_type == "simple":
        model = "mistral"
    else:
        model = "qwen3:14b"

    prompt = user_input

    return {
        "model": model,
        "prompt": prompt,
        "task_type": task_type
    }  