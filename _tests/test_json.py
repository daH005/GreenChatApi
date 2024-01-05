import pytest

from api.json_ import JSONDictPreparer
from api._tests.db_test_data import *  # noqa
from api._tests.common import make_random_string  # noqa


@pytest.mark.parametrize(('dict_', 'keys'), [
    (JSONDictPreparer.prepare_jwt_token(make_random_string()), {'JWTToken'}),
    (JSONDictPreparer.prepare_already_taken(True), {'isAlreadyTaken'}),
    (JSONDictPreparer.prepare_code_is_valid(True), {'codeIsValid'}),
    (JSONDictPreparer.prepare_user_chats(CHATS.values()), {'chats'}),
    (JSONDictPreparer.prepare_chat_info(CHATS[1]), {
        'id', 'name', 'isGroup', 'users', 'lastMessage',
    }),
    (JSONDictPreparer.prepare_user_info(USERS[1]), {
        'id', 'firstName', 'lastName',
    }),
    (JSONDictPreparer.prepare_user_info(USERS[2], exclude_important_info=False), {
        'id', 'firstName', 'lastName', 'username', 'email',
    }),
    (JSONDictPreparer.prepare_chat_history(CHATS[1].messages), {'messages'}),
    (JSONDictPreparer.prepare_chat_message(CHATS_MESSAGES[1]), {
        'id', 'chatId', 'text', 'creatingDatetime', 'user',
    })
])
def test_positive_dict_has_key(dict_: dict, keys: list[str] | set[str]) -> None:
    assert set(dict_.keys()) == set(keys)
