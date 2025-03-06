import asyncio
from testlib import *


async def main():
    # await BLE_connect("IN100", timeout_s=15)
    await BLE_connect("IN100", True)

if __name__ == "__main__":
    asyncio.run(main())
