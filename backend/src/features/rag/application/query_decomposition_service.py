
import logging
from typing import List
import json
import re
from src.features.rag.domain.interfaces import ILLMClient, Message

logger = logging.getLogger(__name__)

class QueryDecompositionService:
    """
    Service for decomposing complex user queries into simpler sub-queries
    to improve retrieval coverage (Multi-hop / Multi-step).
    """

    def __init__(self, llm_client: ILLMClient):
        self.llm_client = llm_client

    async def decompose_query(self, query: str) -> List[str]:
        """
        Decompose a complex query into sub-queries.
        Returns a list of sub-queries. If decomposition fails or isn't needed,
        returns the original query as a single-item list.
        """
        if len(query.split()) < 4:
            # Too short to decompose
            return [query]

        prompt = self._build_decomposition_prompt(query)

        try:
            response = await self.llm_client.generate(
                messages=[Message(role="user", content=prompt)],
                model="meta-llama/llama-3.3-70b-instruct:free", # Fast model
                temperature=0.3, # Low temp for deterministic logic
                max_tokens=256
            )

            sub_queries = self._parse_response(response.content)

            if not sub_queries:
                return [query]

            logger.info(f"Decomposed '{query}' into {len(sub_queries)} sub-queries: {sub_queries}")
            return sub_queries

        except Exception as e:
            logger.error(f"Decomposition failed: {e}")
            return [query]

    def _build_decomposition_prompt(self, query: str) -> str:
        return f"""
You are an expert research assistant. specialized in breaking down complex questions.
Your task is to decompose the USER QUERY into 2-3 distinct, simple sub-queries that, when answered, will allow you to answer the original query.

USER QUERY: "{query}"

Rules:
1. Return ONLY a valid JSON list of strings.
2. Do not explain your reasoning.
3. If the query is simple and needs no decomposition, return a list containing only the original query.
4. Each sub-query should be self-contained.

Example Input: "Compare the retry logic in the Chat Service vs the Document Service"
Example Output: ["What is the retry logic in the Chat Service?", "What is the retry logic in the Document Service?"]

JSON Output:
"""

    def _parse_response(self, text: str) -> List[str]:
        try:
            # Try to find JSON list in text
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                json_str = match.group(0)
                queries = json.loads(json_str)
                if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
                    return queries
            return []
        except Exception:
            # Fallback: line splitting if JSON fails
            lines = [line.strip().lstrip('- ').strip('"') for line in text.split('\n') if '?' in line]
            return lines if lines else []
