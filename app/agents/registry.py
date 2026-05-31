from app.agents.base import BaseAgent, DefaultAgent
from app.agents.build import BuildAgent
from app.agents.medical import MedicalAgent
from app.agents.trading import TradingAgent


class AgentRegistry:
    def __init__(self) -> None:
        self.default_agent = DefaultAgent()
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.domain] = agent

    def get(self, domain: str) -> BaseAgent:
        return self._agents.get(domain, self.default_agent)

    def resolve(self, prompt: str, domain: str) -> BaseAgent:
        agent = self.get(domain)
        if agent.should_handle(prompt):
            return agent

        return self.default_agent


def create_default_agent_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register(TradingAgent())
    registry.register(MedicalAgent())
    registry.register(BuildAgent())
    return registry
