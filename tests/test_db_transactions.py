from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db_models.base import Base

from db_models.account_transaction_template import AccountTransactionTemplate


@pytest.fixture
def db_session():
    """Provide an isolated in-memory database for transaction tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def _transfer_money(session, from_user: str, to_user: str, amount: int) -> None:
    """Move money atomically; roll back the session if any step fails."""
    try:
        from_account = (
            session.query(AccountTransactionTemplate)
            .filter_by(user=from_user)
            .one()
        )
        to_account = (
            session.query(AccountTransactionTemplate)
            .filter_by(user=to_user)
            .one()
        )

        if from_account.balance < amount:
            raise ValueError("Недостаточно средств на счете")

        from_account.balance -= amount
        to_account.balance += amount
        session.commit()
    except Exception:
        session.rollback()
        raise


def _create_accounts(session, stan_balance: int, bob_balance: int):
    suffix = uuid4().hex
    stan = AccountTransactionTemplate(user=f"Stan_{suffix}", balance=stan_balance)
    bob = AccountTransactionTemplate(user=f"Bob_{suffix}", balance=bob_balance)
    session.add_all([stan, bob])
    session.commit()
    return stan, bob


def _remove_accounts(session, *users: str) -> None:
    session.rollback()
    session.query(AccountTransactionTemplate).filter(
        AccountTransactionTemplate.user.in_(users)
    ).delete(synchronize_session=False)
    session.commit()


@pytest.mark.database
def test_accounts_transaction_template_transfers_money(db_session):
    stan, bob = _create_accounts(db_session, stan_balance=1000, bob_balance=500)
    try:
        _transfer_money(db_session, stan.user, bob.user, amount=200)

        db_session.expire_all()
        stan_after = (
            db_session.query(AccountTransactionTemplate)
            .filter_by(user=stan.user)
            .one()
        )
        bob_after = (
            db_session.query(AccountTransactionTemplate)
            .filter_by(user=bob.user)
            .one()
        )
        assert stan_after.balance == 800
        assert bob_after.balance == 700
    finally:
        _remove_accounts(db_session, stan.user, bob.user)


@pytest.mark.database
def test_accounts_transaction_template_rolls_back_insufficient_funds(db_session):
    stan, bob = _create_accounts(db_session, stan_balance=100, bob_balance=500)
    try:
        with pytest.raises(ValueError, match="Недостаточно средств"):
            _transfer_money(db_session, stan.user, bob.user, amount=200)

        db_session.expire_all()
        stan_after = (
            db_session.query(AccountTransactionTemplate)
            .filter_by(user=stan.user)
            .one()
        )
        bob_after = (
            db_session.query(AccountTransactionTemplate)
            .filter_by(user=bob.user)
            .one()
        )
        assert stan_after.balance == 100
        assert bob_after.balance == 500
    finally:
        _remove_accounts(db_session, stan.user, bob.user)
