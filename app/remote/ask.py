import sys


def main() -> int:
    if len(sys.argv) < 2:
        print(
            'Usage: python -m app.remote.ask "your prompt here"',
            file=sys.stderr,
        )
        return 2

    prompt = " ".join(sys.argv[1:]).strip()
    if not prompt:
        print(
            'Usage: python -m app.remote.ask "your prompt here"',
            file=sys.stderr,
        )
        return 2

    from app.agents.router import route_request
    from app.llm.service import LLMService

    service = LLMService()
    decision = route_request(prompt)
    result = service.ask(decision["prompt"], model=decision["model"])

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
