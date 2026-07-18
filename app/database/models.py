from .base import Base

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, BigInteger, Numeric, UniqueConstraint, ForeignKey
from datetime import datetime, date
from zoneinfo import ZoneInfo


def phtime_now():
    return datetime.now(ZoneInfo("Asia/Manila"))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=False)
    is_allowed = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False,nullable=False)
    created_at = Column(DateTime(timezone=True), default=phtime_now)
    updated_at = Column(DateTime(timezone=True), default=phtime_now, onupdate=phtime_now)

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    telegram_chat_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, nullable=False)
    group_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=phtime_now)
    updated_at = Column(DateTime(timezone=True), default=phtime_now, onupdate=phtime_now)

class GroupMember(Base):
    __tablename__ = "group_members"

    __table_args__ = (
        UniqueConstraint("group_id","user_id", name="uq_group_member"),
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey("groups.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), default=phtime_now)

class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey("groups.id"), nullable=False)
    added_by = Column(ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    is_done = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=phtime_now)
    updated_at = Column(DateTime(timezone=True), default=phtime_now, onupdate=phtime_now)

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey("groups.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(precision=10, scale=2),nullable=False)
    category_id = Column(ForeignKey("categories.id"),nullable=False)
    expense_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), default=phtime_now)
    updated_at = Column(DateTime(timezone=True), default=phtime_now, onupdate=phtime_now)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey("groups.id"), nullable=False)
    created_by = Column(ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=phtime_now, onupdate=phtime_now)

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey("groups.id"), nullable=False)
    created_by = Column(ForeignKey("users.id"), nullable=False)
    assigned_to = Column(ForeignKey("users.id"), nullable=True)
    text = Column(String, nullable=False)
    remind_at = Column(DateTime(timezone=True),nullable=False)
    recurrence = Column(String, nullable=True)
    is_done = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=phtime_now)

class SinkingFund(Base):
    __tablename__ = "sinking_funds"

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey("groups.id"),nullable=False)
    owner_id = Column(ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    goal = Column(Numeric(precision=12, scale=2), nullable=False)
    current_amount = Column(Numeric(precision=12, scale=2),default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=phtime_now)
    updated_at = Column(DateTime(timezone=True), default=phtime_now, onupdate=phtime_now)

class FundContribution(Base):
    __tablename__ = "fund_contributions"

    id = Column(Integer, primary_key=True)
    fund_id = Column(ForeignKey("sinking_funds.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    note = Column(String, nullable=True)
    contribution_date = Column(Date, default=date.today)
    created_at = Column(DateTime(timezone=True), default=phtime_now)

