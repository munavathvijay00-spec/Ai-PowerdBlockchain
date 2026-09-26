"""
Repositories: organized database operations.
Separates SQL logic from business logic.
"""
import json
from typing import Optional, List, Dict
from loguru import logger

from src.database.connection import Database


class AddressRepository:
    """All address-related database operations."""

    def __init__(self, db: Database):
        self.db = db

    async def get_or_create(self, address: str) -> int:
        """Get address ID, creating if not exists. Returns address ID."""
        query = """
            INSERT INTO addresses (address) 
            VALUES ($1) 
            ON CONFLICT (address) DO UPDATE 
            SET last_seen = CURRENT_TIMESTAMP
            RETURNING id
        """
        return await self.db.fetchval(query, address.lower())

    async def get_by_address(self, address: str) -> Optional[Dict]:
        """Fetch address by string value."""
        query = """
            SELECT id, address, first_seen, last_seen, 
                   label, is_blacklisted, risk_score
            FROM addresses 
            WHERE address = $1
        """
        return await self.db.fetchrow(query, address.lower())

    async def is_blacklisted(self, address: str) -> bool:
        """Check if address is in blacklist."""
        query = "SELECT EXISTS(SELECT 1 FROM blacklist WHERE address = $1)"
        return await self.db.fetchval(query, address.lower())

    async def count(self) -> int:
        """Total addresses tracked."""
        return await self.db.fetchval("SELECT COUNT(*) FROM addresses")

    async def list_all(self, limit: int = 10) -> List[Dict]:
        """List recent addresses."""
        query = """
            SELECT address, first_seen, risk_score
            FROM addresses
            ORDER BY first_seen DESC
            LIMIT $1
        """
        return await self.db.fetch(query, limit)


class TransactionRepository:
    """All transaction-related database operations."""

    def __init__(self, db: Database, address_repo: AddressRepository):
        self.db = db
        self.addresses = address_repo

    async def create(self, tx: Dict) -> int:
        """Insert a transaction. Returns the new row ID."""
        from_id = await self.addresses.get_or_create(tx['from_address'])
        to_id = await self.addresses.get_or_create(tx['to_address'])

        query = """
            INSERT INTO transactions 
            (hash, from_address_id, to_address_id, value, 
             block_number, timestamp, status, risk_score)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (hash) DO UPDATE 
            SET risk_score = EXCLUDED.risk_score
            RETURNING id
        """
        return await self.db.fetchval(
            query,
            tx['hash'],
            from_id,
            to_id,
            tx['value'],
            tx['block_number'],
            tx['timestamp'],
            tx.get('status', 'confirmed'),
            tx.get('risk_score', 0),
        )

    async def get_by_hash(self, tx_hash: str) -> Optional[Dict]:
        """Fetch a transaction by its hash."""
        query = """
            SELECT 
                t.hash,
                a_from.address AS from_address,
                a_to.address AS to_address,
                t.value,
                t.block_number,
                t.timestamp,
                t.status,
                t.risk_score,
                t.risk_factors,
                t.ai_explanation
            FROM transactions t
            JOIN addresses a_from ON t.from_address_id = a_from.id
            JOIN addresses a_to ON t.to_address_id = a_to.id
            WHERE t.hash = $1
        """
        return await self.db.fetchrow(query, tx_hash)

    async def list_recent(self, limit: int = 10) -> List[Dict]:
        """List recent transactions."""
        query = """
            SELECT 
                t.hash,
                a_from.address AS from_address,
                a_to.address AS to_address,
                t.value,
                t.block_number,
                t.timestamp,
                t.risk_score
            FROM transactions t
            JOIN addresses a_from ON t.from_address_id = a_from.id
            JOIN addresses a_to ON t.to_address_id = a_to.id
            ORDER BY t.timestamp DESC
            LIMIT $1
        """
        return await self.db.fetch(query, limit)

    async def list_all(self, limit: int = 1000) -> List[Dict]:
        """Fetch all transactions for batch risk scoring."""
        query = """
            SELECT 
                t.hash,
                a_from.address AS from_address,
                a_to.address AS to_address,
                t.value,
                t.block_number,
                t.timestamp,
                t.risk_score
            FROM transactions t
            JOIN addresses a_from ON t.from_address_id = a_from.id
            JOIN addresses a_to ON t.to_address_id = a_to.id
            ORDER BY t.block_number DESC
            LIMIT $1
        """
        return await self.db.fetch(query, limit)

    async def list_flagged(self, min_score: int = 20, limit: int = 100) -> List[Dict]:
        """Fetch flagged transactions (risk_score >= min_score) for AI explanation."""
        query = """
            SELECT 
                t.hash,
                a_from.address AS from_address,
                a_to.address AS to_address,
                t.value,
                t.block_number,
                t.timestamp,
                t.risk_score,
                t.risk_factors,
                t.ai_explanation
            FROM transactions t
            JOIN addresses a_from ON t.from_address_id = a_from.id
            JOIN addresses a_to ON t.to_address_id = a_to.id
            WHERE t.risk_score >= $1
            ORDER BY t.risk_score DESC, t.timestamp DESC
            LIMIT $2
        """
        return await self.db.fetch(query, min_score, limit)

    async def count(self) -> int:
        """Total transactions stored."""
        return await self.db.fetchval("SELECT COUNT(*) FROM transactions")

    async def update_risk(self, tx_hash: str, score: int, factors: list) -> None:
        """Update risk score and factors for a transaction."""
        query = """
            UPDATE transactions 
            SET risk_score = $1, risk_factors = $2::jsonb
            WHERE hash = $3
        """
        await self.db.execute(query, score, json.dumps(factors), tx_hash)

    async def update_explanation(self, tx_hash: str, explanation: str) -> None:
        """Update AI-generated explanation for a transaction."""
        query = """
            UPDATE transactions 
            SET ai_explanation = $1
            WHERE hash = $2
        """
        await self.db.execute(query, explanation, tx_hash)