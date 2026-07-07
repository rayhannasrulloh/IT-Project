import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.services.intent_service import IntentService
from app.services.clarification_service import ClarificationService
from app.services.sql_service import SqlService
from app.services.chat_service import ChatService
from app.services.benchmark_service import BenchmarkService
from app.utils.sql_validator import validate_sql_safety
from app.models.profiles import Profile
from app.models.conversations import Conversation

# Local Sqlite memory db setup for async tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as session:
        # Create a test profile
        profile = Profile(id="test-user-id", email="user@cda.com", full_name="Test User", role="user")
        admin_profile = Profile(id="admin-user-id", email="admin@cda.com", full_name="Admin User", role="admin")
        session.add_all([profile, admin_profile])
        await session.commit()
        
        yield session
    await engine.dispose()

@pytest.mark.asyncio
async def test_intent_detection():
    service = IntentService()
    
    # Greetings
    assert await service.detect_intent("hello") == "GREETING"
    assert await service.detect_intent("hi there") == "GREETING"
    
    # Small talk
    assert await service.detect_intent("how are you") == "SMALL_TALK"
    
    # Help
    assert await service.detect_intent("what can you do") == "HELP"
    
    # Data query - database questions
    assert await service.detect_intent("how many customers in surabaya") == "DATA_QUERY"
    assert await service.detect_intent("show revenue this month") == "DATA_QUERY"
    
    # Unsupported questions
    assert await service.detect_intent("who is messi") == "UNSUPPORTED"


@pytest.mark.asyncio
async def test_clarification_logic():
    service = ClarificationService()
    
    # Ambiguous revenue
    is_amb, intent, missing, msg = service.check_ambiguity("Show revenue")
    assert is_amb
    assert intent == "revenue_analysis"
    assert "revenue_type" in missing
    assert "Which revenue would you like to see?" in msg

    # Ambiguous sales
    is_amb, intent, missing, msg = service.check_ambiguity("Show sales")
    assert is_amb
    assert intent == "sales_analysis"
    assert "time_period" in missing

    # Ambiguous customer
    is_amb, intent, missing, msg = service.check_ambiguity("top customers")
    assert is_amb
    assert intent == "customer_ranking"
    assert "customer_metric" in missing

    # Ambiguous product
    is_amb, intent, missing, msg = service.check_ambiguity("best products")
    assert is_amb
    assert intent == "product_performance"
    assert "performance_metric" in missing

    # Ambiguous orders
    is_amb, intent, missing, msg = service.check_ambiguity("show orders")
    assert is_amb
    assert intent == "order_analysis"
    assert "order_breakdown" in missing

    # Resolving fields
    success, data = service.resolve_missing_field("sales_analysis", "This year")
    assert success
    assert data["time_period"] == "this year"


def test_response_formatter():
    from app.services.response_formatter import ResponseFormatter
    formatter = ResponseFormatter()
    
    # Test single value format
    res = formatter.format_single_value("how many customers in surabaya", "count", 12)
    assert res == "There are currently 12 customers located in Surabaya."
    
    res = formatter.format_single_value("What is the total revenue this month?", "total", 24890.0)
    assert res == "The total revenue for this month is $24,890."

    # Test table summary format
    res = formatter.format_table_summary("Which city has the most customers?", ["city", "customers"], [{"city": "Surabaya", "customers": 124}])
    assert res == "Surabaya has the highest number of customers with 124 registered customers."
    
    res = formatter.format_table_summary("What are the top selling products?", ["name"], [{"name": "Laptop Pro"}, {"name": "Wireless Mouse"}])
    assert "1. Laptop Pro" in res
    assert "2. Wireless Mouse" in res


@pytest.mark.asyncio
async def test_sql_generation_and_safety():
    sql_service = SqlService()
    
    # Mock SQL compilation
    is_amb, clar, sql, reasoning = await sql_service.generate_sql("Who are our top customers by revenue?")
    assert not is_amb
    assert sql is not None
    assert "customers" in sql.lower()
    
    # Safety validator assertions
    assert validate_sql_safety("SELECT * FROM customers;")
    assert validate_sql_safety("WITH active_orders AS (SELECT * FROM orders) SELECT * FROM active_orders;")
    assert not validate_sql_safety("INSERT INTO customers (name) VALUES ('Hacker');")
    assert not validate_sql_safety("DROP TABLE customers;")
    assert not validate_sql_safety("SELECT * FROM customers; DELETE FROM orders;")


@pytest.mark.asyncio
async def test_chat_service_flows(test_db):
    chat_service = ChatService(test_db)
    
    # Test Greeting flow (returns checklist, no SQL)
    res = await chat_service.handle_message(
        user_id="test-user-id",
        query_text="hello"
    )
    assert res["type"] == "conversation"
    assert "Conversational Data Analyst" in res["message"]
    
    # Test Ambiguous flow (triggers clarification context)
    res = await chat_service.handle_message(
        user_id="test-user-id",
        query_text="Show revenue"
    )
    assert res["type"] == "clarification"
    assert "revenue_type" in res["missing_fields"]
    
    # Follow-up reply to resolve clarification context
    conversation_id = res["db_message"].conversation_id
    res_resolved = await chat_service.handle_message(
        user_id="test-user-id",
        query_text="by month",
        conversation_id=conversation_id
    )
    # Should now run SQL compilation
    assert res_resolved["type"] in ["query_result", "conversation"]


@pytest.mark.asyncio
async def test_benchmark_runner(test_db):
    benchmark_service = BenchmarkService(test_db)
    
    # Seed and execute benchmark test suite
    res = await benchmark_service.run_benchmarks()
    assert res.summary.total_tests > 0
    assert len(res.results) == res.summary.total_tests
    
    # Verify result log is accessible
    logs = await benchmark_service.get_benchmark_results(limit=10)
    assert len(logs) > 0
