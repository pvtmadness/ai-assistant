from pathlib import Path
from datetime import datetime


class ConversationLogger:
    def __init__(self, log_path: str = "logs/conversations.log") -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, prompt: str, response: str) -> None:
        timestamp = datetime.now().isoformat(timespec="seconds")

        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(f"[{timestamp}]\n")
            f.write(f"PROMPT: {prompt}\n")
            f.write(f"RESPONSE: {response}\n")
            f.write("-" * 60 + "\n")
            
    def get_recent(self, limit: int = 5) -> str:
        if not self.log_path.exists():
            return ""

        with self.log_path.open("r", encoding="utf-8") as f:
            content = f.read()

        entries = content.strip().split("-" * 60)
        recent_entries = entries[-limit:]

        cleaned = []
        for entry in recent_entries:
            lines = entry.strip().splitlines()
            for line in lines:
                if line.startswith("PROMPT:") or line.startswith("RESPONSE:"):
                    cleaned.append(line)

        return "\n".join(cleaned)        