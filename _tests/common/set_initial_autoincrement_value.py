from sqlalchemy import text

from db.builder import db_builder

__all__ = (
    'set_initial_autoincrement_value',
)


def set_initial_autoincrement_value(tablename: str,
                                    value: int,
                                    ) -> None:
    with db_builder.engine.connect() as connection:
        connection.execute(text(f'ALTER TABLE {tablename} AUTO_INCREMENT = {value}'))
