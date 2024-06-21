import pytest

from api.common.json_ import (
    ChatHistoryJSONDictMaker,
    ChatMessageJSONDictMaker,
    ChatMessageTypingJSONDictMaker,
    UserChatsJSONDictMaker,
    ChatJSONDictMaker,
    JWTJSONDictMaker,
    UserJSONDictMaker,
    CodeIsValidFlagJSONDictMaker,
    NewUnreadCountJSONDictMaker,
    ReadChatMessagesIdsJSONDictMaker,
)
from api._tests.data.json_ import (
    JWT_TOKEN_KWARGS_AND_JSON_DICTS,
    CODE_IS_VALID_FLAG_KWARGS_AND_JSON_DICTS,
    USER_CHATS_KWARGS_AND_JSON_DICTS,
    CHAT_INFO_KWARGS_AND_JSON_DICTS,
    USER_INFO_KWARGS_AND_JSON_DICTS,
    CHAT_HISTORY_KWARGS_AND_JSON_DICTS,
    CHAT_MESSAGE_KWARGS_AND_JSON_DICTS,
    NEW_UNREAD_COUNT_KWARGS_AND_JSON_DICTS,
    READ_CHAT_MESSAGES_KWARGS_AND_JSON_DICTS,
    CHAT_MESSAGE_TYPING_KWARGS_AND_JSON_DICTS,
)


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), JWT_TOKEN_KWARGS_AND_JSON_DICTS)
def test_positive_jwt_token(maker_kwargs: dict,
                            expected_dict: dict,
                            ) -> None:
    assert JWTJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), CODE_IS_VALID_FLAG_KWARGS_AND_JSON_DICTS)
def test_positive_code_is_valid_flag(maker_kwargs: dict,
                                     expected_dict: dict,
                                     ) -> None:
    assert CodeIsValidFlagJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), USER_CHATS_KWARGS_AND_JSON_DICTS)
def test_positive_user_chats(maker_kwargs: dict,
                             expected_dict: dict,
                             ) -> None:
    assert UserChatsJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), CHAT_INFO_KWARGS_AND_JSON_DICTS)
def test_positive_chat_info(maker_kwargs: dict,
                            expected_dict: dict,
                            ) -> None:
    assert ChatJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), USER_INFO_KWARGS_AND_JSON_DICTS)
def test_positive_user_info(maker_kwargs: dict,
                            expected_dict: dict,
                            ) -> None:
    assert UserJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), CHAT_HISTORY_KWARGS_AND_JSON_DICTS)
def test_positive_chat_history(maker_kwargs: dict,
                               expected_dict: dict,
                               ) -> None:
    assert ChatHistoryJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), CHAT_MESSAGE_KWARGS_AND_JSON_DICTS)
def test_positive_chat_message(maker_kwargs: dict,
                               expected_dict: dict,
                               ) -> None:
    assert ChatMessageJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), CHAT_MESSAGE_TYPING_KWARGS_AND_JSON_DICTS)
def test_positive_chat_message_typing(maker_kwargs: dict,
                                      expected_dict: dict,
                                      ) -> None:
    assert ChatMessageTypingJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), NEW_UNREAD_COUNT_KWARGS_AND_JSON_DICTS)
def test_positive_new_unread_count(maker_kwargs: dict,
                                   expected_dict: dict,
                                   ) -> None:
    assert NewUnreadCountJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), READ_CHAT_MESSAGES_KWARGS_AND_JSON_DICTS)
def test_positive_read_chat_messages(maker_kwargs: dict,
                                     expected_dict: dict,
                                     ) -> None:
    assert ReadChatMessagesIdsJSONDictMaker.make(**maker_kwargs) == expected_dict
