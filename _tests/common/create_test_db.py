from config.db import DB_TEST_URL
from db.builders import db_sync_builder
from db.models import BaseModel

__all__ = (
    'create_test_db',
)


def create_test_db(objects=None) -> None:
    if hasattr(db_sync_builder, '_session'):
        db_sync_builder.session.remove()

    db_sync_builder.init_session(DB_TEST_URL)
    BaseModel.metadata.drop_all(db_sync_builder.engine)
    BaseModel.metadata.create_all(db_sync_builder.engine)

    if objects is not None:
        db_sync_builder.session.add_all(objects)
        db_sync_builder.session.commit()
