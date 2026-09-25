"""
Test script: Connects to Ethereum and fetches real blockchain data.
Run: python -m scripts.test_blockchain
"""
import asyncio
from src.blockchain.client import BlockchainClient


async def main():
    print("\n" + "="*60)
    print("🔗 ETHEREUM CONNECTION TEST")
    print("="*60 + "\n")
    
    # 1. Connect
    print("📡 Connecting to Ethereum via Alchemy...")
    client = BlockchainClient()
    connected = await client.connect()
    
    if not connected:
        print("❌ Failed to connect. Check your ALCHEMY_API_KEY in .env")
        return
    
    print()
    
    # 2. Get latest block
    print("📦 Fetching latest block number...")
    latest = await client.get_latest_block_number()
    print(f"✅ Latest block: {latest:,}\n")
    
    # 3. Fetch the block
    print("🔍 Fetching block details...")
    block = await client.get_block(latest)
    print(f"✅ Block #{block['number']:,}")
    print(f"   Hash: 0x{block['hash'].hex() if hasattr(block['hash'], 'hex') else block['hash']}")
    print(f"   Timestamp: {block['timestamp']}")
    print(f"   Transactions: {len(block.get('transactions', []))}")
    print(f"   Gas used: {block.get('gasUsed', 0):,}")
    print(f"   Gas limit: {block.get('gasLimit', 0):,}")
    print()
    
    # 4. Fetch full transactions in the block
    print("💸 Fetching transactions in this block...")
    transactions = await client.get_transactions_in_block(latest)
    print(f"✅ Found {len(transactions)} transactions\n")
    
    # 5. Show first 3 transactions
    print("🔎 First 3 transactions:")
    print("-" * 60)
    for i, tx in enumerate(transactions[:3], 1):
        tx_hash = tx['hash'].hex() if hasattr(tx['hash'], 'hex') else tx['hash']
        value_eth = tx.get('value', 0) / 10**18
        
        print(f"\n[{i}] Hash: {tx_hash[:50]}...")
        print(f"    From: {tx.get('from', 'N/A')}")
        print(f"    To:   {tx.get('to', 'Contract Creation')}")
        print(f"    Value: {value_eth:.6f} ETH")
        print(f"    Gas price: {tx.get('gasPrice', 0) / 10**9:.2f} Gwei")
    
    print()
    print("="*60)
    print("🎉 SUCCESS — YOU'RE CONNECTED TO ETHEREUM!")
    print("="*60 + "\n")
    
    # Cleanup
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())