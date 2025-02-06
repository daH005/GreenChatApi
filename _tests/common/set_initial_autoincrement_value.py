from sqlalchemy import text

from db.builders import db_sync_builder

__all__ = (
    'set_initial_autoincrement_value',
)


def set_initial_autoincrement_value(tablename: str,
                                    value: int,
                                    ) -> None:
    with db_sync_builder.engine.connect() as connection:
        connection.execute(text(f'ALTER TABLE {tablename} AUTO_INCREMENT = {value}'))
