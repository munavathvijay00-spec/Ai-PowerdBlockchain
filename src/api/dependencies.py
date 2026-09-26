"""
Shared dependencies for API routes.
Provides database repositories to endpoint handlers.
"""
from typing import AsyncGenerator
from src.database.connection import get_db
from src.database.repositories import AddressRepository, TransactionRepository


async def get_transaction_repo() -> TransactionRepository:
    """Provide a TransactionRepository to routes."""
    db = await get_db()
    addresses = AddressRepository(db)
    return TransactionRepository(db, addresses)


async def get_address_repo() -> AddressRepository:
    """Provide an AddressRepository to routes."""
    db = await get_db()
    return AddressRepository(db)