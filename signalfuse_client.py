"""
signalfuse_client.py — SignalFuse API wrapper
Fused trading intelligence: sentiment + macro regime + market structure.
Docs: https://signalfuse.co
"""
import requests


class SignalFuseClient:
    BASE_URL = "https://api.signalfuse.co"

    def __init__(self, credit_token: str = None):
        """
        credit_token: Pre-paid credit token from /v1/credits/trial or /v1/credits/buy.
        Leave None to use x402 pay-per-call (requires x402-compatible HTTP client).
        """
        self.session = requests.Session()
        if credit_token:
            self.session.headers["X-Credit-Token"] = credit_token

    def get_signal(self, symbol: str) -> dict:
        """
        Fetch fused directional signal for a symbol.

        Returns:
          {
            "symbol": str,
            "signal": str,              # long / short / neutral
            "signal_strength": int,     # 0-100
            "confidence": float,        # 0.0-1.0
            "regime": str,              # risk_on / risk_off / neutral
            "components": {
              "social": {"score": float, "label": str},
              "macro": {"score": float, "label": str},
              "market": {"score": float, "label": str},
            },
            "updated_at": str
          }
        """
        r = self.session.get(
            f"{self.BASE_URL}/v1/signal/{symbol.upper()}",
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def get_regime(self) -> dict:
        """Current macro risk regime (no symbol required)."""
        r = self.session.get(f"{self.BASE_URL}/v1/regime", timeout=10)
        r.raise_for_status()
        return r.json()

    def get_sentiment(self, symbol: str) -> dict:
        """Raw sentiment breakdown for a symbol."""
        r = self.session.get(
            f"{self.BASE_URL}/v1/sentiment/{symbol.upper()}",
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def get_signal_batch(self, symbols: list[str] = None) -> dict:
        """Batch signals for multiple symbols at once."""
        params = {}
        if symbols:
            params["symbols"] = ",".join(s.upper() for s in symbols)
        r = self.session.get(
            f"{self.BASE_URL}/v1/signal/batch",
            params=params,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
