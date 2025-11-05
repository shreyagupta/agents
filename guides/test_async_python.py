import asyncio
import random

async def do_some_work(x="A"):
    print(f"Starting work {x}")
    await asyncio.sleep(1)
    print(f"Work complete {x}")

async def do_a_lot_of_work():
    await asyncio.gather(do_some_work(), do_some_work("B"), do_some_work("C"))

if __name__ == "__main__":
    asyncio.run(do_a_lot_of_work())