from sqlalchemy import select, func, delete, insert

from database.base import Session
from database.models import SinkingFund

from decimal import Decimal, InvalidOperation

def add_sinking_fund(user, group, name):
    session = Session()

    try:
        clean_names = [item.strip().lower() for item in name]

        valid_items = []
        invalid_items = []

        for item in clean_names:
            parts = item.split()

            if len(parts) < 2:
                invalid_items.append(item)
                continue

            try:
                valid_items.append([" ".join(parts[:-1]), Decimal(parts[-1])])
            except InvalidOperation:
                invalid_items.append(item)
        name_list = [item[:-1] for item in valid_items]
        exists = select(SinkingFund).where(SinkingFund.group_id==group.id, func.lower(SinkingFund.name).in_(name_list))
        item_exists = session.scalars(exists).all()
        existing_items = {item.name.lower() for item in item_exists}
        add_items = [item for item in valid_items if item[0] not in existing_items]
        items_to_add = [item[0] for item in add_items]
        if existing_items and not add_items:
            return list(existing_items), items_to_add, invalid_items, True

        bulk_data = [{"group_id": group.id, "owner_id": user.id, "name": item[0].lower(), "goal": int(item[1])} for item in add_items]
        session.execute(insert(SinkingFund), bulk_data)
        session.commit()
        return list(existing_items), items_to_add, invalid_items, False

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

def list_sinking_funds(user, group):
    session = Session()

    try:
        exists = select(SinkingFund).where(SinkingFund.group_id==group.id)
        sinking_funds = session.scalars(exists).all()
        if sinking_funds:
            return sinking_funds, True
        return sinking_funds, False
    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

def remove_sinking_funds(user, group, name):
    session = Session()

    try:
        exists = select(SinkingFund).where(SinkingFund.group_id==group.id, func.lower(SinkingFund.name).in_(name))
        item_exists = session.scalars(exists).all()
        if not item_exists:
            return item_exists, False

        to_delete = delete(SinkingFund).where(SinkingFund.group_id==group.id, func.lower(SinkingFund.name).in_(name))
        session.execute(to_delete)
        session.commit()
        deleted = [item.name for item in item_exists]
        return deleted, True

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
