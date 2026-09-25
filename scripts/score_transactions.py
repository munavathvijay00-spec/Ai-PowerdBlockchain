"""
Risk scoring batch job.
Scores every transaction in the database.
Run: python -m scripts.score_transactions
"""
import asyncio
from collections import Counter

from src.database.connection import get_db, close_db
from src.database.repositories import AddressRepository, TransactionRepository
from src.risk.scorer import get_scorer


async def main():
    print("\n" + "=" * 60)
    print("🧠 RISK SCORING ENGINE")
    print("=" * 60 + "\n")

    print("🗄️  Connecting to database...")
    db = await get_db()
    addresses = AddressRepository(db)
    transactions = TransactionRepository(db, addresses)
    scorer = get_scorer()
    print("✅ Connected\n")

    print("📦 Fetching transactions from database...")
    all_txs = await transactions.list_all(limit=1000)
    print(f"✅ Found {len(all_txs)} transactions\n")

    print("🧠 Scoring transactions...")
    distribution = Counter()
    total_score = 0
    scored = 0
    errors = 0

    for i, tx in enumerate(all_txs, 1):
        try:
            history = []

            from_black = await addresses.is_blacklisted(tx['from_address'])
            to_black = await addresses.is_blacklisted(tx['to_address'])
            is_blacklisted = from_black or to_black

            result = await scorer.score_transaction(
                tx=tx,
                address_history=history,
                is_blacklisted=is_blacklisted,
            )

            await transactions.update_risk(
                tx['hash'], result['score'], result['factors']
            )

            total_score += result['score']
            scored += 1

            if result['score'] >= 80:
                distribution['HIGH'] += 1
            elif result['score'] >= 40:
                distribution['MEDIUM'] += 1
            elif result['score'] >= 15:
                distribution['LOW'] += 1
            else:
                distribution['MINIMAL'] += 1

            if i % 100 == 0:
                print(f"   ...{i}/{len(all_txs)} scored")

        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"   ❌ Error on {tx['hash'][:20]}: {type(e).__name__}: {e}")

    avg_score = total_score / scored if scored else 0
    print()
    print("=" * 60)
    print(f"✅ Scored: {scored}")
    print(f"❌ Errors: {errors}")
    print(f"📊 Average score: {avg_score:.2f}")
    print()
    print("📊 Risk Distribution:")
    for level in ['MINIMAL', 'LOW', 'MEDIUM', 'HIGH']:
        count = distribution[level]
        pct = (count / scored * 100) if scored else 0
        bar = "█" * int(pct / 2)
        print(f"   {level:8s} {count:4d} ({pct:5.1f}%) {bar}")
    print("=" * 60 + "\n")

    await close_db()


if __name__ == "__main__":
    asyncio.run(main())