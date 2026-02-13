import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from src.features.rag.domain.interfaces import ILLMClient
from src.config import settings

logger = logging.getLogger(__name__)

class RouteSelection(BaseModel):
    index_name: str
    reason: str
    confidence: float

class QueryRouter:
    """
    Routes user queries to specific specialized indices based on intent.
    """

    ROUTES = {
        "technical_docs": "General technical documentation, architectural overviews, and concepts.",
        "codebase": "Source code specific questions, file paths, class definitions, and implementation details.",
        "incident_reports": "Information about bugs, issues, root cause analyses (RCA), and incident logs.",
        "general": "Broad knowledge queries or topics not covered by specialized indices."
    }

    def __init__(self, llm_client: ILLMClient):
        self.llm_client = llm_client

    async def route_query(self, query: str) -> RouteSelection:
        """
        Uses LLM to determine the best index for the query.
        """
        prompt = self._build_router_prompt(query)

        try:
            # We use a structured prompt to get a JSON-like response
            response = await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt="You are a query router for a RAG system. Your job is to classify the user query into one of the specialized indices."
            )

            # Simple parsing (could be improved with instructor or JSON mode)
            selection = self._parse_llm_response(response.answer)
            logger.info(f"Query routed to '{selection.index_name}' (conf: {selection.confidence})")
            return selection

        except Exception as e:
            logger.error(f"Routing failed: {e}. Defaulting to 'technical_docs'")
            return RouteSelection(
                index_name="technical_docs",
                reason="Fallback due to routing error",
                confidence=0.0
            )

    def _build_router_prompt(self, query: str) -> str:
        routes_desc = "\n".join([f"- {name}: {desc}" for name, desc in self.ROUTES.items()])
        return f"""
Analyze the following user query and decide which specialized index is most relevant.

Available Indices:
{routes_desc}

User Query: "{query}"

Respond ONLY with a JSON object in this format:
{{
  "index_name": "name_of_index",
  "reason": "brief explanation",
  "confidence": 0.0-1.0
}}
"""

    def _parse_llm_response(self, text: str) -> RouteSelection:
        import json
        import re

        # Try to find JSON in the response
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                # Validate index name
                if data.get("index_name") not in self.ROUTES:
                    data["index_name"] = "technical_docs"
                return RouteSelection(**data)
        except Exception as e:
            logger.warning(f"Failed to parse router response: {e}")

        return RouteSelection(
            index_name="technical_docs",
            reason="Could not parse LLM selection",
            confidence=0.0
        )
