"""
AI-powered transaction explainer.
Converts risk factors into plain-English explanations.
Supports multiple LLM providers via the LLM_PROVIDER setting.
"""
import httpx
from typing import Dict, List, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.config import get_settings


class TransactionExplainer:
    """
    Generates plain-English explanations for risky transactions.
    
    Provider-agnostic:
    - LLM_PROVIDER=ollama → uses local Ollama at localhost:11434
    - LLM_PROVIDER=openai → uses OpenAI API (future)
    """

    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.llm_provider
        self.model = self.settings.llm_model
        self.ollama_url = self.settings.ollama_url
        
        logger.info(
            f"🧠 Explainer initialized "
            f"(provider={self.provider}, model={self.model})"
        )

    def _build_prompt(self, tx: Dict, factors: List[Dict]) -> str:
        """
        Build a structured prompt from transaction data + risk factors.
        
        Design principles:
        - Clear role ("blockchain security analyst")
        - Clear audience ("non-technical user")
        - Concise output (2-3 sentences)
        - Concrete data (specific amounts, addresses)
        """
        # Convert wei to ETH
        value_eth = tx['value'] / 10**18
        usd_approx = value_eth * 2500  # Rough ETH price estimate
        
        # Format factors into readable bullets
        factor_lines = []
        for f in factors:
            factor_lines.append(
                f"- {f.get('factor', 'unknown')}: "
                f"{f.get('reason', 'no reason')} "
                f"(+{f.get('points', 0)} points)"
            )
        factors_text = "\n".join(factor_lines) if factor_lines else "- No specific factors"
        
        prompt = f"""You are a blockchain security analyst. Explain to a non-technical user why this Ethereum transaction was flagged as risky. Use exactly 2-3 sentences.

Transaction data:
- Amount: {value_eth:.4f} ETH (approximately ${usd_approx:,.0f} USD)
- From address: {tx.get('from_address', 'unknown')[:10]}...
- To address: {tx.get('to_address', 'unknown')[:10]}...
- Block number: {tx.get('block_number', 0)}
- Risk score: {tx.get('risk_score', 0)}/100

Detected risk factors:
{factors_text}

Write a clear, specific explanation that covers:
1. Why the transaction was flagged
2. What the underlying risk is
3. What the user should do

Avoid technical jargon. Be direct and factual. Do not say "I" or mention that you are an AI."""
        
        return prompt

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5)
    )
    async def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama's /api/generate endpoint.
        This runs the LLM locally on your Mac.
        """
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,      # Lower = more deterministic
                "num_predict": 200,      # Max tokens in response
                "top_p": 0.9,
            }
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    async def explain(self, tx: Dict, factors: List[Dict]) -> Optional[str]:
        """
        Generate a plain-English explanation for a transaction.
        Returns None if generation fails.
        """
        try:
            prompt = self._build_prompt(tx, factors)
            
            if self.provider == "ollama":
                explanation = await self._call_ollama(prompt)
            else:
                logger.warning(f"Provider '{self.provider}' not implemented, skipping")
                return None
            
            if not explanation:
                logger.warning(f"Empty explanation for {tx.get('hash', 'unknown')[:15]}")
                return None
            
            return explanation
        
        except Exception as e:
            logger.error(f"Failed to explain {tx.get('hash', 'unknown')[:15]}: {e}")
            return None


# Singleton
_explainer: Optional[TransactionExplainer] = None


def get_explainer() -> TransactionExplainer:
    """Get or create the global explainer instance."""
    global _explainer
    if _explainer is None:
        _explainer = TransactionExplainer()
    return _explainer