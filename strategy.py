"""
strategy.py — plug your logic in here
Default: simple strength-threshold long/short with trailing stop.
"""
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info


class Strategy:
    LONG_THRESHOLD = 62
    SHORT_THRESHOLD = 38
    BASE_SIZE_USD = 100  # replace with % of balance logic

    def __init__(self, exchange: Exchange, info: Info):
        self.exchange = exchange
        self.info = info
        self.open_positions = {}

    async def evaluate(self, symbol: str, signal: dict):
        strength = signal.get("signal_strength", 50)
        direction = signal.get("signal", "neutral")
        confidence = signal.get("confidence", 0.5)

        if direction == "long" and strength >= self.LONG_THRESHOLD:
            await self._enter(symbol, "buy", strength, confidence)
        elif direction == "short" and strength <= self.SHORT_THRESHOLD:
            await self._enter(symbol, "sell", strength, confidence)

    async def _enter(self, symbol: str, side: str, strength: int, confidence: float):
        if symbol in self.open_positions:
            return  # already in

        # Scale size by confidence
        size = (self.BASE_SIZE_USD * confidence) / 100  # TODO: fetch current price
        try:
            result = self.exchange.market_open(symbol, side == "buy", size)
            self.open_positions[symbol] = {
                "side": side,
                "strength": strength,
                "confidence": confidence,
            }
            print(f"  -> Entered {side.upper()} {symbol} (strength={strength}, conf={confidence:.2f})")
        except Exception as e:
            print(f"  -> Order failed for {symbol}: {e}")
