from db.builder import db_builder
from db.models import BaseModel

__all__ = (
    'create_test_db',
)


def create_test_db(objects=None) -> None:
    db_builder.init_session('sqlite:///:memory:', isolation_level=None)
    BaseModel.metadata.create_all(bind=db_builder.engine)

    if objects is not None:
        db_builder.session.add_all(objects)
        db_builder.session.commit()
