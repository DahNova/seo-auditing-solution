"""
Test database models - isolated version
"""
import pytest
import asyncio
import os
from datetime import datetime
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_models.db"

Base = declarative_base()

# Simplified model definitions for testing
class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Website(Base):
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String(255), nullable=False)
    name = Column(String(255))
    description = Column(Text)
    scan_frequency = Column(String(50), default="monthly")
    max_pages = Column(Integer, default=1000)
    max_depth = Column(Integer, default=5)
    robots_respect = Column(Boolean, default=True)
    include_external = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="pending")
    pages_found = Column(Integer, default=0)
    pages_scanned = Column(Integer, default=0)
    pages_failed = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()

class TestClientModel:
    """Test Client model"""
    
    async def test_create_client(self, test_session):
        """Test creating a client"""
        client = Client(
            name="Test Agency",
            contact_email="agency@test.com",
            description="Test description"
        )
        
        test_session.add(client)
        await test_session.commit()
        await test_session.refresh(client)
        
        assert client.id is not None
        assert client.name == "Test Agency"
        assert client.contact_email == "agency@test.com"
        assert client.created_at is not None
    
    async def test_client_unique_email(self, test_session):
        """Test that client emails must be unique"""
        client1 = Client(
            name="Agency 1",
            contact_email="same@email.com"
        )
        client2 = Client(
            name="Agency 2",
            contact_email="same@email.com"
        )
        
        test_session.add(client1)
        await test_session.commit()
        
        test_session.add(client2)
        
        # This should raise an integrity error
        with pytest.raises(Exception):  # SQLAlchemy will raise some kind of integrity error
            await test_session.commit()

class TestWebsiteModel:
    """Test Website model"""
    
    async def test_create_website(self, test_session):
        """Test creating a website"""
        # First create a client
        client = Client(
            name="Test Client",
            contact_email="client@test.com"
        )
        test_session.add(client)
        await test_session.commit()
        await test_session.refresh(client)
        
        # Then create website
        website = Website(
            client_id=client.id,
            domain="https://example.com",
            name="Example Site",
            scan_frequency="weekly",
            max_pages=500,
            max_depth=3,
            robots_respect=True,
            include_external=False,
            is_active=True
        )
        
        test_session.add(website)
        await test_session.commit()
        await test_session.refresh(website)
        
        assert website.id is not None
        assert website.domain == "https://example.com"
        assert website.scan_frequency == "weekly"
        assert website.max_pages == 500
        assert website.is_active is True
    
    async def test_website_defaults(self, test_session):
        """Test website default values"""
        # Create client first
        client = Client(name="Test Client", contact_email="test@client.com")
        test_session.add(client)
        await test_session.commit()
        await test_session.refresh(client)
        
        website = Website(
            client_id=client.id,
            domain="https://minimal.com"
        )
        
        test_session.add(website)
        await test_session.commit()
        await test_session.refresh(website)
        
        assert website.robots_respect is True
        assert website.scan_frequency == "monthly"
        assert website.max_pages == 1000
        assert website.max_depth == 5
        assert website.include_external is False
        assert website.is_active is True

class TestScanModel:
    """Test Scan model"""
    
    async def test_create_scan(self, test_session):
        """Test creating a scan"""
        # Create client and website first
        client = Client(name="Scan Test Client", contact_email="scan-client@test.com")
        test_session.add(client)
        await test_session.commit()
        await test_session.refresh(client)
        
        website = Website(
            client_id=client.id,
            domain="https://scan-example.com",
            name="Scan Test Site"
        )
        test_session.add(website)
        await test_session.commit()
        await test_session.refresh(website)
        
        # Create scan
        scan = Scan(
            website_id=website.id,
            status="running",
            pages_found=100,
            pages_scanned=50,
            pages_failed=2,
            total_issues=15,
            config={"max_depth": 5, "timeout": 300}
        )
        
        test_session.add(scan)
        await test_session.commit()
        await test_session.refresh(scan)
        
        assert scan.id is not None
        assert scan.status == "running"
        assert scan.pages_found == 100
        assert scan.total_issues == 15
        assert scan.config["max_depth"] == 5
    
    async def test_scan_timestamps(self, test_session):
        """Test scan timestamp handling"""
        # Create dependencies
        client = Client(name="Timestamp Test Client", contact_email="timestamp-client@test.com")
        test_session.add(client)
        await test_session.commit()
        await test_session.refresh(client)
        
        website = Website(client_id=client.id, domain="https://timestamp-test.com")
        test_session.add(website)
        await test_session.commit()
        await test_session.refresh(website)
        
        scan = Scan(
            website_id=website.id,
            status="completed"
        )
        
        test_session.add(scan)
        await test_session.commit()
        await test_session.refresh(scan)
        
        assert scan.created_at is not None
        # started_at and completed_at would be set by application logic, not by default

class TestModelRelationships:
    """Test relationships between models"""
    
    async def test_client_website_relationship(self, test_session):
        """Test that we can query related data"""
        # Create client with website
        client = Client(name="Relationship Test Client", contact_email="relationship-client@test.com")
        test_session.add(client)
        await test_session.commit()
        await test_session.refresh(client)
        
        website = Website(
            client_id=client.id,
            domain="https://relationship-test.com",
            name="Relationship Test Site"
        )
        test_session.add(website)
        await test_session.commit()
        
        # Query to verify relationship data
        from sqlalchemy import select
        
        # Get client and verify website is associated
        result = await test_session.execute(
            select(Client).where(Client.id == client.id)
        )
        stored_client = result.scalar_one()
        assert stored_client.id == client.id
        
        # Get website and verify client association
        result = await test_session.execute(
            select(Website).where(Website.client_id == client.id)
        )
        stored_website = result.scalar_one()
        assert stored_website.client_id == client.id
        assert stored_website.domain == "https://relationship-test.com"
    
    async def test_website_scan_relationship(self, test_session):
        """Test website-scan relationship"""
        # Create full chain: client -> website -> scan
        client = Client(name="Final Test Client", contact_email="final-client@test.com")
        test_session.add(client)
        await test_session.commit()
        await test_session.refresh(client)
        
        website = Website(client_id=client.id, domain="https://final-test.com")
        test_session.add(website)
        await test_session.commit()
        await test_session.refresh(website)
        
        scan = Scan(website_id=website.id, status="completed")
        test_session.add(scan)
        await test_session.commit()
        
        # Verify relationships through queries
        from sqlalchemy import select
        
        result = await test_session.execute(
            select(Scan).where(Scan.website_id == website.id)
        )
        stored_scan = result.scalar_one()
        assert stored_scan.website_id == website.id
        assert stored_scan.status == "completed"