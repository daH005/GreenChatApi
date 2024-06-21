from unittest.mock import patch

from api.db.db_builder import DBBuilder
from api.db.models import BaseModel
from api.common.json_ import ChatMessageJSONDictMaker
from api._tests.common import COMMON_DATETIME
from api._tests.data.db import (
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

    patch('api.common.json_.ChatMessageJSONDictMaker.make', chat_message_json_dict_maker_make_method_mock).start()
    prepare_db()


def prepare_db() -> None:
    DBBuilder.init_session('sqlite:///:memory:')
    BaseModel.metadata.create_all(bind=DBBuilder.engine)

    DBBuilder.session.add_all([
        *USERS.values(),
        *CHATS.values(),
        *USERS_CHATS_MATCHES,
        *UNREAD_COUNTS,
    ])
    DBBuilder.session.commit()

    # For correct `creating_datetime`:
    for message in CHATS_MESSAGES:
        DBBuilder.session.add(message)
        DBBuilder.session.commit()
