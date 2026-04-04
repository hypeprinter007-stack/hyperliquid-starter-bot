"""
signalfuse_client.py — SignalFuse API wrapper
Fused trading intelligence: sentiment + macro regime + market structure.
Docs: https://signalfuse.co

Two payment modes:
  1. Credit token (simplest) — get 25 free calls, then buy packs
  2. x402 per-call — automatic USDC on Base, requires x402 SDK + funded wallet
"""
import os

BASE_URL = "https://api.signalfuse.co"


def create_client(credit_token: str = None, wallet_private_key: str = None):
    """
    Create a SignalFuse HTTP client.

    Args:
        credit_token: Pre-paid credit token (from /v1/credits/trial or /v1/credits/buy).
                      Simplest option — works with plain HTTP.
        wallet_private_key: Ethereum private key for x402 pay-per-call on Base.
                            Requires: pip install x402 httpx eth-account

    Returns one of:
        - x402HttpxClient (if wallet key provided — handles 402→sign→pay automatically)
        - httpx.Client with X-Credit-Token header (if credit token provided)
    """
    if wallet_private_key:
        # x402 per-call: client handles 402→sign USDC→resend automatically
        from eth_account import Account
        from x402 import x402Client
        from x402.mechanisms.evm import EthAccountSigner
        from x402.mechanisms.evm.exact import ExactEvmScheme
        from x402.http.clients.httpx import x402HttpxClient

        account = Account.from_key(wallet_private_key)
        signer = EthAccountSigner(account)
        client = x402Client()
        client.register("eip155:*", ExactEvmScheme(signer=signer))
        return x402HttpxClient(client)

    # Credit token: plain HTTP with token header
    import httpx
    headers = {}
    if credit_token:
        headers["X-Credit-Token"] = credit_token
    return httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=15.0)


class SignalFuseClient:
    """Convenience wrapper around the SignalFuse API."""

    def __init__(self, credit_token: str = None, wallet_private_key: str = None):
        self._credit_token = credit_token
        self._wallet_key = wallet_private_key
        self._client = None
        self._is_x402 = bool(wallet_private_key)

    async def _get_client(self):
        if self._client is None:
            self._client = create_client(self._credit_token, self._wallet_key)
        return self._client

    async def get_signal(self, symbol: str) -> dict:
        """Fetch fused directional signal for a symbol."""
        client = await self._get_client()
        url = f"{BASE_URL}/v1/signal/{symbol.upper()}" if self._is_x402 else f"/v1/signal/{symbol.upper()}"
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()

    async def get_regime(self) -> dict:
        """Current macro risk regime."""
        client = await self._get_client()
        url = f"{BASE_URL}/v1/regime" if self._is_x402 else "/v1/regime"
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()

    async def get_sentiment(self, symbol: str) -> dict:
        """Raw sentiment breakdown for a symbol."""
        client = await self._get_client()
        url = f"{BASE_URL}/v1/sentiment/{symbol.upper()}" if self._is_x402 else f"/v1/sentiment/{symbol.upper()}"
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()

    async def get_signal_batch(self, symbols: list[str] = None) -> dict:
        """Batch signals for multiple symbols."""
        client = await self._get_client()
        params = {}
        if symbols:
            params["symbols"] = ",".join(s.upper() for s in symbols)
        url = f"{BASE_URL}/v1/signal/batch" if self._is_x402 else "/v1/signal/batch"
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
