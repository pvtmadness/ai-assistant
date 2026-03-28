from app.config.settings import settings


def main() -> None:
    print("AI Assistant starting...")
    print(f"Fast model: {settings.fast_model}")
    print(f"Reasoning model: {settings.reasoning_model}")
    print(f"Vector DB path: {settings.vector_db_path}")


if __name__ == "__main__":
    main()