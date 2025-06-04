import logging
from datetime import datetime, timezone

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFoundError
from app.models.models import Transaction

logger = logging.getLogger(__name__)

class TransactionService:
    """Service to handle transaction operations."""
    def get_user_transactions(
        self,
        user_id: str,
        db: Session,
        limit: None|int,
        offset: None|int,
        from_date: None|datetime,
        to_date: None|datetime,
    ) -> dict:
        """Get transaction history for a user.

        Args:
            user_id: User identifier
            db: Database session
            limit: Maximum number of transactions to return
            offset: Offset for pagination
            from_date: Filter transactions from this date
            to_date: Filter transactions to this date
        Returns:
            Dict: Transaction history with metadata
        Raises:
            UserNotFoundError: If no transactions found for user
        """
        # Start with base user query
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        # First check if user has any transactions
        if query.count() == 0:
            raise UserNotFoundError(user_id)

        logger.info("\nConstructing query with filters:")
        logger.info(f"User ID: {user_id}")
        logger.info(f"From date: {from_date}")
        logger.info(f"To date: {to_date}")

        # Apply date filters
        if from_date:
            # Ensure UTC timezone
            from_date = from_date.astimezone(timezone.utc)
            msg = f"Filtering transactions >= {from_date}"
            logger.info(msg)
            query = query.filter(Transaction.timestamp >= from_date)

        if to_date:
            # Ensure UTC timezone
            to_date = to_date.astimezone(timezone.utc)
            msg = f"Filtering transaction >= {to_date}"
            logger.info(msg)
            query = query.filter(Transaction.timestamp <= to_date)

        # Get filtered count
        filtered_count = query.count()
        msg = f"Found {filtered_count} transactions after date filtering"
        logger.info(msg)


        # Apply ordering (newest first)
        query = query.order_by(desc(Transaction.timestamp))

        # Apply pagination if specified
        if offset is not None and offset >= 0:
            query = query.offset(offset)
        if limit is not None and limit > 0:
            query = query.limit(limit)

        # Execute query
        transactions = query.all()

        # formatted_transactions
        formatted_transactions = [self._format_transaction(tx) for tx in transactions]

        result = {
            "user_id": user_id,
            "transactions": formatted_transactions,
            "count": len(formatted_transactions),
            "total": filtered_count
        }
        msg = f"Returning {len(formatted_transactions)} transactions"
        logger.info(msg)
        return result


    def _format_transactions(self, transaction: Transaction) -> dict:
        """
        Format transaction model to response dictionary.

        Args:
            transaction: Transaction model
        """
        # Ensure timezone info and proper ISO format
        timestamp = transaction.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return {
            "transaction_id": transaction.id,
            "from": {
                "currency": transaction.source_currency,
                "amount": transaction.source_amount,
            },
            "to": {
                "currency": transaction.target_currency,
                "amount": transaction.target_amount,
            },
            "rate": transaction.exchange_rate,
            "timestamp": timestamp,
        }
