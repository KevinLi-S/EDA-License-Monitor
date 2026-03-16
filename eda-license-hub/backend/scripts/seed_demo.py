import asyncio
from datetime import UTC, datetime

from sqlalchemy import text

from app.database import engine


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(text('SELECT 1'))
    print(f'Phase-1 seed placeholder executed at {datetime.now(UTC).isoformat()}')


if __name__ == '__main__':
    asyncio.run(main())
