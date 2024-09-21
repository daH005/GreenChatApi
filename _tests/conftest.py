from unittest.mock import patch

from db.builder import db_builder
from db.models import BaseModel
from common.json_ import ChatMessageJSONDictMaker
from _tests.common_ import COMMON_DATETIME
from _tests.data.db import (
    USERS,
    CHATS,
    USERS_CHATS_MATCHES,
    UNREAD_COUNTS,
    CHATS_MESSAGES,
)


def pytest_sessionstart() -> None:
    _chat_message_json_dict_maker_make_method_backup = ChatMessageJSONDictMaker.make
    def chat_message_json_dict_maker_make_method_mock(*args, **kwargs) -> dict:
        return {
            **_chat_message_json_dict_maker_make_method_backup(*args, **kwargs),
            'creatingDatetime': COMMON_DATETIME.isoformat(),
        }

    patch('common.json_.ChatMessageJSONDictMaker.make', chat_message_json_dict_maker_make_method_mock).start()

    _prepare_db()
    patch('db.builder.db_builder.session.remove', lambda: 0).start()


def _prepare_db() -> None:
    db_builder.init_session('sqlite:///:memory:', isolation_level=None)
    BaseModel.metadata.create_all(bind=db_builder.engine)

    db_builder.session.add_all([
        *USERS.values(),
        *CHATS.values(),
        *USERS_CHATS_MATCHES,
        *UNREAD_COUNTS,
    ])
    db_builder.session.commit()

    # For correct `creating_datetime`:
    for message in CHATS_MESSAGES:
        db_builder.session.add(message)
        db_builder.session.commit()
