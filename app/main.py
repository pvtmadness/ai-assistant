from app.llm.service import LLMService
from app.agents.router import route_request


def main():
    service = LLMService()

    while True:
        prompt = input("Enter a prompt: ")

        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        decision = route_request(prompt)
        result = service.ask(decision["prompt"], model=decision["model"])

        print(f"\n[Result]\n{result}\n")


if __name__ == "__main__":
    main()