import pytest

from api._tests.all_test_data.json_test_data import *  # noqa: must be first!
from api.json_ import *
from api._tests.common import make_random_string  # noqa
from api._tests.replacing import ChatMessageJSONDictMakeReplacer  # noqa


def setup_module() -> None:
    ChatMessageJSONDictMakeReplacer.replace()


def teardown_module() -> None:
    ChatMessageJSONDictMakeReplacer.back()


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), JWT_TOKEN_KWARGS_AND_JSON_DICTS)
def test_positive_jwt_token(maker_kwargs: dict,
                            expected_dict: dict,
                            ) -> None:
    assert JWTTokenJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), ALREADY_TAKEN_FLAG_KWARGS_AND_JSON_DICTS)
def test_positive_already_taken_flag(maker_kwargs: dict,
                                     expected_dict: dict,
                                     ) -> None:
    assert AlreadyTakenFlagJSONDictMaker.make(**maker_kwargs) == expected_dict


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
    assert ChatInfoJSONDictMaker.make(**maker_kwargs) == expected_dict


@pytest.mark.parametrize(('maker_kwargs', 'expected_dict'), USER_INFO_KWARGS_AND_JSON_DICTS)
def test_positive_user_info(maker_kwargs: dict,
                            expected_dict: dict,
                            ) -> None:
    assert UserInfoJSONDictMaker.make(**maker_kwargs) == expected_dict


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
