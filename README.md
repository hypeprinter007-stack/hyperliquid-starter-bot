# Hyperliquid Starter Bot

A minimal, production-ready algorithmic trading bot for [Hyperliquid](https://hyperliquid.xyz) perpetuals.
Uses [SignalFuse](https://signalfuse.co) for trading intelligence — fused sentiment, macro regime, and market structure in one API call.

## Features

- Hyperliquid Python SDK — market + limit orders, position management
- SignalFuse signal layer — fused sentiment + macro + market structure
- Two payment modes — credit tokens (simplest) or x402 per-call (USDC on Base)
- Simple strategy scaffold — plug in your own logic
- Clean async architecture — runs on any Linux/Mac

## Quick Start

```bash
git clone https://github.com/hypeprinter007-stack/hyperliquid-starter-bot
cd hyperliquid-starter-bot
pip install -r requirements.txt
cp .env.example .env
# Fill in your .env values
python main.py
```

## How SignalFuse Works

```python
from signalfuse_client import SignalFuseClient

# Credit token (simplest)
sf = SignalFuseClient(credit_token="your-token")

# Or x402 per-call (requires x402 + eth-account packages)
# sf = SignalFuseClient(wallet_private_key="0x...")

signal = await sf.get_signal("BTC")

print(signal)
# {
#   "symbol": "BTC",
#   "signal": "long",
#   "signal_strength": 74,
#   "confidence": 0.82,
#   "regime": "risk_on",
#   "components": {
#     "social": {"score": 0.49, "label": "bullish"},
#     "macro": {"score": 0.63, "label": "bullish"},
#     "market": {"score": 0.42, "label": "long_bias"}
#   }
# }
```

Get 25 free calls — no signup:
```bash
curl -X POST https://api.signalfuse.co/v1/credits/trial \
  -H "Content-Type: application/json" \
  -d '{"wallet":"YOUR_ETH_ADDRESS"}'
```

Full docs at [https://signalfuse.co](https://signalfuse.co)

## Strategy Logic

The default strategy is simple and intentionally minimal — override `strategy.py` with your own logic:

1. Fetch SignalFuse signal for each asset in your watchlist
2. If `signal_strength > 62` and direction is `long` -> enter long, size based on confidence
3. If `signal_strength < 38` and direction is `short` -> enter short or close long
4. Trailing stop at 2% from entry

## Architecture

```
main.py              — entry point, main loop
signalfuse_client.py — SignalFuse API wrapper
strategy.py          — signal -> order logic
.env                 — your keys (never commit this)
```

## Contributing

PRs welcome. If you build something cool on top of this, open an issue and share it.

## License

MIT
