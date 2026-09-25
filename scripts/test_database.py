"""
Test script: Connects to PostgreSQL and does a full round-trip.
Run: python -m scripts.test_database
"""
import asyncio
from datetime import datetime

from src.database.connection import get_db, close_db
from src.database.repositories import AddressRepository, TransactionRepository


async def main():
    print("\n" + "="*60)
    print("🧪 DATABASE CONNECTION TEST")
    print("="*60 + "\n")
    
    # 1. Connect
    print("📡 Connecting to database...")
    db = await get_db()
    print("✅ Connected!\n")
    
    # 2. Set up repositories
    addresses = AddressRepository(db)
    transactions = TransactionRepository(db, addresses)
    
    # 3. Insert a test address
    print("📝 Inserting test address...")
    test_address = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
    address_id = await addresses.get_or_create(test_address)
    print(f"✅ Address inserted with ID: {address_id}\n")
    
    # 4. Query it back
    print("🔍 Querying address back...")
    address_row = await addresses.get_by_address(test_address)
    print(f"✅ Found: {address_row}\n")
    
    # 5. Check blacklist
    print("🚨 Checking blacklist status...")
    is_black = await addresses.is_blacklisted(test_address)
    print(f"✅ Blacklisted: {is_black}\n")
    
    # 6. Insert a transaction
    print("💸 Inserting test transaction...")
    test_tx = {
        "hash": "0x" + "a" * 64,
        "from_address": test_address,
        "to_address": "0x0000000000000000000000000000000000000000",
        "value": 1000000000000000000,
        "block_number": 21000000,
        "timestamp": datetime.now(),
        "status": "confirmed",
        "risk_score": 25,
    }
    tx_id = await transactions.create(test_tx)
    print(f"✅ Transaction inserted with ID: {tx_id}\n")
    
    # 7. Query it back
    print("🔍 Querying transaction back...")
    tx_row = await transactions.get_by_hash(test_tx["hash"])
    print(f"✅ Found: {tx_row}\n")
    
    # 8. Stats
    print("📊 Statistics:")
    print(f"   Total addresses: {await addresses.count()}")
    print(f"   Total transactions: {await transactions.count()}\n")
    
    # 9. Cleanup
    print("🔌 Closing connection...")
    await close_db()
    print("✅ Done!\n")
    
    print("="*60)
    print("🎉 ALL TESTS PASSED — DATABASE LAYER WORKS!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())