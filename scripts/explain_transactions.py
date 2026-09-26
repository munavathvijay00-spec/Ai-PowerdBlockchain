"""
AI explanation batch job.
Generates plain-English explanations for flagged transactions.
Run: python -m scripts.explain_transactions
"""
import asyncio
import json
import time

from src.database.connection import get_db, close_db
from src.database.repositories import AddressRepository, TransactionRepository
from src.agents.explainer import get_explainer


async def main():
    print("\n" + "=" * 60)
    print("🧠 AI EXPLANATION ENGINE")
    print("=" * 60 + "\n")

    start_time = time.time()

    # 1. Connect to database with error handling
    print("🗄️  Connecting to database...")
    try:
        db = await get_db()
        if db is None or db.pool is None:
            print("❌ Database connection failed — is Docker running?")
            print("   Try: docker compose up -d")
            return
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("   Try: docker compose up -d")
        return

    addresses = AddressRepository(db)
    transactions = TransactionRepository(db, addresses)
    print("✅ Connected\n")

    # 2. Initialize explainer
    print("🧠 Initializing AI explainer...")
    try:
        explainer = get_explainer()
        print(f"✅ Explainer ready ({explainer.provider}/{explainer.model})\n")
    except Exception as e:
        print(f"❌ Explainer failed to initialize: {e}")
        print("   Is Ollama running? Try: ollama serve")
        await close_db()
        return

    # 3. Fetch flagged transactions
    print("📦 Fetching flagged transactions (risk_score >= 20)...")
    flagged = await transactions.list_flagged(min_score=20, limit=100)
    print(f"✅ Found {len(flagged)} transactions to explain\n")

    if not flagged:
        print("ℹ️  No flagged transactions. Nothing to explain.")
        await close_db()
        return

    # 4. Explain each
    print("🤖 Generating AI explanations...")
    explained = 0
    failed = 0
    skipped = 0

    for i, tx in enumerate(flagged, 1):
        try:
            if tx.get('ai_explanation'):
                skipped += 1
                print(f"   [{i}/{len(flagged)}] Skipped (already explained): {tx['hash'][:15]}")
                continue

            factors = tx.get('risk_factors') or []
            if isinstance(factors, str):
                factors = json.loads(factors)

            print(f"   [{i}/{len(flagged)}] Explaining {tx['hash'][:15]}...", end=" ", flush=True)

            explanation = await explainer.explain(tx, factors)

            if explanation:
                await transactions.update_explanation(tx['hash'], explanation)
                explained += 1
                print("✅")
            else:
                failed += 1
                print("❌")

        except Exception as e:
            failed += 1
            print(f"❌ {type(e).__name__}: {e}")

    # 5. Summary
    elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print(f"✅ Explained: {explained}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"⏱️  Total time: {elapsed:.1f}s")
    print("=" * 60 + "\n")

    # 6. Show sample
    print("📋 Sample explanations:")
    print("-" * 60)
    sample = await transactions.list_flagged(min_score=20, limit=3)
    for tx in sample:
        if tx.get('ai_explanation'):
            print(f"\n🔹 {tx['hash'][:15]}... (Score: {tx['risk_score']})")
            print(f"   {tx['ai_explanation']}")
    print()

    await close_db()


if __name__ == "__main__":
    asyncio.run(main())