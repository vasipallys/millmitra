from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
import google.generativeai as genai

class RiceMillAIOrchestrator:
    def __init__(self):
        self.agents = {
            'operations': OperationsAgent(),
            'financial': FinancialAgent(),
            'compliance': ComplianceAgent(),
            'customer': CustomerAgent()
        }
        self.memory = ConversationBufferMemory()
        
    async def process_query(self, query: str, context: dict):
        # Route query to appropriate agent
        agent_type = self._classify_query(query)
        agent = self.agents[agent_type]
        
        response = await agent.process(query, context)
        return self._format_response(response)