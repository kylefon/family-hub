from sqlalchemy import select

from database.models import Category

DEFAULT_CATEGORIES = [
    "groceries",
    "dining",
    "transportation",
    "utilities",
    "health",
    "entertainment",
    "shopping",
    "education",
    "travel",
    "savings",
    "other",
]


def seed_categories(session, group, user):
    for category_name in DEFAULT_CATEGORIES:
        existing = session.scalar(
            select(Category).where(
                Category.group_id == group.id,
                Category.name == category_name,
            )
        )

        if existing:
            continue

        session.add(
            Category(
                group_id=group.id,
                created_by=user.id,
                name=category_name,
            )
        )
