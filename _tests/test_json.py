import pytest

from api.json_ import *
from api._tests.db_test_data import *  # noqa
from api._tests.common import make_random_string  # noqa


@pytest.mark.parametrize(('dict_', 'keys'), [
    (JWTTokenJSONDictMaker.make(make_random_string()), {'JWTToken'}),
    (AlreadyTakenFlagJSONDictMaker.make(True), {'isAlreadyTaken'}),
    (CodeIsValidFlagJSONDictMaker.make(True), {'codeIsValid'}),
    (UserChatsJSONDictMaker.make(CHATS.values()), {'chats'}),
    (ChatInfoJSONDictMaker.make(CHATS[1]), {
        'id', 'name', 'isGroup', 'users', 'lastMessage',
    }),
    (UserInfoJSONDictMaker.make(USERS[1]), {
        'id', 'firstName', 'lastName',
    }),
    (UserInfoJSONDictMaker.make(USERS[2], exclude_important_info=False), {
        'id', 'firstName', 'lastName', 'username', 'email',
    }),
    (ChatHistoryJSONDictMaker.make(CHATS[1].messages), {'messages'}),
    (ChatMessageJSONDictMaker.make(CHATS_MESSAGES[1]), {
        'id', 'chatId', 'text', 'creatingDatetime', 'user',
    })
])
def test_positive_dict_has_key(dict_: dict, keys: list[str] | set[str]) -> None:
    assert set(dict_.keys()) == set(keys)
