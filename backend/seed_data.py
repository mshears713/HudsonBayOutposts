"""
Seed Script for Sample Outpost Data

Run this script to populate the database with sample Hudson Bay outposts
for testing and demonstration purposes.
"""

import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

from models import Outpost, ExpeditionLog, Base

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://hudsonbay:hudsonbay@localhost:5432/hudsonbay"
)


async def seed_outposts(session: AsyncSession):
    """Create sample outpost data"""

    outposts = [
        Outpost(
            id=uuid.uuid4(),
            name="Fort Churchill",
            location_lat=58.7684,
            location_lon=-94.1648,
            description="Northern outpost monitoring Arctic weather patterns and wildlife",
            api_endpoint="http://192.168.1.100:8000",
        ),
        Outpost(
            id=uuid.uuid4(),
            name="York Factory",
            location_lat=57.0,
            location_lon=-92.3,
            description="Historical trading post with modern environmental sensors",
            api_endpoint="http://192.168.1.101:8000",
        ),
        Outpost(
            id=uuid.uuid4(),
            name="Norway House",
            location_lat=53.9781,
            location_lon=-97.8446,
            description="Central hub for data aggregation and communication relay",
            api_endpoint="http://192.168.1.102:8000",
        ),
        Outpost(
            id=uuid.uuid4(),
            name="Cumberland House",
            location_lat=53.9667,
            location_lon=-102.2500,
            description="Western outpost tracking river systems and aquatic data",
            api_endpoint="http://192.168.1.103:8000",
        ),
    ]

    session.add_all(outposts)
    await session.commit()

    print(f"✅ Created {len(outposts)} sample outposts")
    return outposts


async def seed_logs(session: AsyncSession, outposts: list[Outpost]):
    """Create sample expedition log entries"""

    logs = []
    for outpost in outposts[:2]:  # Add logs for first 2 outposts
        logs.extend([
            ExpeditionLog(
                id=uuid.uuid4(),
                timestamp=datetime.utcnow(),
                outpost_id=outpost.id,
                event_type="sensor_reading",
                details={
                    "temperature": 15.5,
                    "humidity": 65.2,
                    "pressure": 1013.25,
                    "sensor": "DHT22"
                }
            ),
            ExpeditionLog(
                id=uuid.uuid4(),
                timestamp=datetime.utcnow(),
                outpost_id=outpost.id,
                event_type="status_update",
                details={
                    "status": "operational",
                    "uptime": "72h",
                    "battery": "85%"
                }
            ),
        ])

    session.add_all(logs)
    await session.commit()

    print(f"✅ Created {len(logs)} sample log entries")


async def main():
    """Main seed function"""

    print("🌱 Seeding Hudson Bay database...")

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Create tables if they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Seed data
        outposts = await seed_outposts(session)
        await seed_logs(session, outposts)

    await engine.dispose()

    print("✅ Database seeding complete!")
    print("\nSample outposts created:")
    for outpost in outposts:
        print(f"  • {outpost.name} at ({outpost.location_lat}, {outpost.location_lon})")


if __name__ == "__main__":
    asyncio.run(main())
