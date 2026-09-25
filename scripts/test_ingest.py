"""
Ingest pipeline: Fetch a live Ethereum block and store its transactions.
Run: python -m scripts.test_ingest
"""
import asyncio
import time
from src.blockchain.client import BlockchainClient
from src.blockchain.normalizer import TransactionNormalizer
from src.database.connection import get_db, close_db
from src.database.repositories import AddressRepository, TransactionRepository


async def main():
    print("\n" + "=" * 60)
    print("📥 BLOCKCHAIN INGEST PIPELINE")
    print("=" * 60 + "\n")

    start_time = time.time()

    # 1. Connect to blockchain
    print("📡 Connecting to Ethereum...")
    client = BlockchainClient()
    connected = await client.connect()
    if not connected:
        print("❌ Blockchain connection failed")
        return
    print()

    # 2. Connect to database
    print("🗄️  Connecting to PostgreSQL...")
    db = await get_db()
    addresses = AddressRepository(db)
    transactions = TransactionRepository(db, addresses)
    print()

    # 3. Fetch latest block WITH full transactions
    print("📦 Fetching latest block with transactions...")
    latest = await client.get_latest_block_number()
    block = await client.get_block(latest, full_transactions=True)
    raw_txs = [dict(tx) for tx in block.get('transactions', [])]
    print(f"✅ Block #{latest:,} contains {len(raw_txs)} transactions\n")

    # 4. Normalize all transactions
    print("🔧 Normalizing transactions...")
    normalizer = TransactionNormalizer()
    normalized = normalizer.normalize_batch(raw_txs, block)
    print(f"✅ Normalized {len(normalized)} transactions\n")

    # 5. Store in database
    print("💾 Storing in PostgreSQL...")
    inserted = 0
    failed = 0
    first_error_shown = False

    for i, tx in enumerate(normalized, 1):
        try:
            await transactions.create(tx)
            inserted += 1
            if i % 50 == 0:
                print(f"   ...{i}/{len(normalized)} transactions processed")
        except Exception as e:
            failed += 1
            if not first_error_shown:
                print(f"\n❌ FIRST ERROR DETAILS:")
                print(f"   Transaction hash: {tx.get('hash', 'unknown')}")
                print(f"   From: {tx.get('from_address', 'unknown')}")
                print(f"   To:   {tx.get('to_address', 'unknown')}")
                print(f"   Value: {tx.get('value', 'unknown')}")
                print(f"   Error type: {type(e).__name__}")
                print(f"   Error message: {e}\n")
                first_error_shown = True

    print(f"\n✅ Inserted: {inserted}")
    print(f"❌ Failed: {failed}\n")

    # 6. Verify with a query
    print("🔍 Verifying with database query...")
    total = await transactions.count()
    print(f"✅ Total transactions in DB: {total}\n")

    # 7. Show most recent transactions
    print("📋 Latest 3 transactions from the block:")
    print("-" * 60)
    recent = await transactions.list_recent(limit=3)
    for tx in recent:
        value_eth = tx['value'] / 10**18
        print(f"   {tx['hash'][:20]}... | {value_eth:.6f} ETH | block {tx['block_number']}")

    elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print(f"🎉 INGEST COMPLETE in {elapsed:.2f}s")
    print("=" * 60 + "\n")

    # Cleanup
    await client.close()
    await close_db()


if __name__ == "__main__":
    asyncio.run(main())