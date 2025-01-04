from config import DB_TEST_URL
from db.builder import db_builder
from db.models import BaseModel

__all__ = (
    'create_test_db',
)


def create_test_db(objects=None) -> None:
    if db_builder.session:
        db_builder.session.remove()

    db_builder.init_session(DB_TEST_URL)
    BaseModel.metadata.drop_all(db_builder.engine)
    BaseModel.metadata.create_all(db_builder.engine)

    if objects is not None:
        db_builder.session.add_all(objects)
        db_builder.session.commit()
