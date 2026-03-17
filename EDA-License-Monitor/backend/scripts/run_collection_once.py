import asyncio

from app.database import AsyncSessionLocal
from app.services.collector_service import collector_service


async def main() -> None:
    async with AsyncSessionLocal() as session:
        results = await collector_service.collect_all(session)
    for result in results:
        print(result)


if __name__ == '__main__':
    asyncio.run(main())
