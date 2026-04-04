"""
main.py — Hyperliquid Starter Bot entry point
"""
import asyncio
import os
from dotenv import load_dotenv
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants
from signalfuse_client import SignalFuseClient
from strategy import Strategy

load_dotenv()

WATCHLIST = ["BTC", "ETH", "SOL"]
POLL_INTERVAL = 60  # seconds


async def main():
    # Init Hyperliquid
    info = Info(constants.MAINNET_API_URL)
    exchange = Exchange(
        wallet=os.getenv("HL_WALLET_PRIVATE_KEY"),
        base_url=constants.MAINNET_API_URL,
        account_address=os.getenv("HL_ACCOUNT_ADDRESS"),
    )

    sf = SignalFuseClient(credit_token=os.getenv("SIGNALFUSE_CREDIT_TOKEN"))
    strategy = Strategy(exchange=exchange, info=info)

    print("Bot started. Watching:", WATCHLIST)

    while True:
        for symbol in WATCHLIST:
            try:
                signal = sf.get_signal(symbol)
                print(
                    f"[{symbol}] strength={signal['signal_strength']} | "
                    f"{signal['signal']} | regime={signal['regime']}"
                )
                await strategy.evaluate(symbol, signal)
            except Exception as e:
                print(f"[{symbol}] Error: {e}")

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
