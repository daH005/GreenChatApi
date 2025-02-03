from _tests.data.http_.set_for_tests.chat import CHAT
from _tests.data.http_.set_for_tests.chat_messages import CHAT_MESSAGES
from _tests.data.http_.set_for_tests.chat_new import CHAT_NEW
from _tests.data.http_.set_for_tests.chat_typing import CHAT_TYPING
from _tests.data.http_.set_for_tests.chat_unread_count import CHAT_UNREAD_COUNT
from _tests.data.http_.set_for_tests.message import MESSAGE
from _tests.data.http_.set_for_tests.message_delete import MESSAGE_DELETE
from _tests.data.http_.set_for_tests.message_edit import MESSAGE_EDIT
from _tests.data.http_.set_for_tests.message_files_delete import MESSAGE_FILES_DELETE
from _tests.data.http_.set_for_tests.message_files_get import MESSAGE_FILES_GET
from _tests.data.http_.set_for_tests.message_files_names import MESSAGE_FILES_NAMES
from _tests.data.http_.set_for_tests.message_files_update import MESSAGE_FILES_UPDATE
from _tests.data.http_.set_for_tests.message_new import MESSAGE_NEW
from _tests.data.http_.set_for_tests.message_read import MESSAGE_READ
from _tests.data.http_.set_for_tests.user import USER
from _tests.data.http_.set_for_tests.user_avatar import USER_AVATAR
from _tests.data.http_.set_for_tests.user_avatar_edit import USER_AVATAR_EDIT
from _tests.data.http_.set_for_tests.user_background import USER_BACKGROUND
from _tests.data.http_.set_for_tests.user_background_edit import USER_BACKGROUND_EDIT
from _tests.data.http_.set_for_tests.user_chats import USER_CHATS
from _tests.data.http_.set_for_tests.user_edit import USER_EDIT
from _tests.data.http_.set_for_tests.user_login import USER_LOGIN
from _tests.data.http_.set_for_tests.user_login_email_code_check import USER_LOGIN_EMAIL_CODE_CHECK
from _tests.data.http_.set_for_tests.user_login_email_code_send import USER_LOGIN_EMAIL_CODE_SEND
from _tests.data.http_.set_for_tests.user_logout import USER_LOGOUT
from _tests.data.http_.set_for_tests.user_refresh_access import USER_REFRESH_ACCESS

__all__ = (
    'SetForTest',
)


class SetForTest:

    user_login = USER_LOGIN
    user_login_email_code_send = USER_LOGIN_EMAIL_CODE_SEND
    user_login_email_code_check = USER_LOGIN_EMAIL_CODE_CHECK
    user_logout = USER_LOGOUT
    user_refresh_access = USER_REFRESH_ACCESS
    user_edit = USER_EDIT
    user = USER
    user_avatar_edit = USER_AVATAR_EDIT
    user_avatar = USER_AVATAR
    user_background_edit = USER_BACKGROUND_EDIT
    user_background = USER_BACKGROUND

    chat_new = CHAT_NEW
    message_new = MESSAGE_NEW
    message_delete = MESSAGE_DELETE
    message_edit = MESSAGE_EDIT
    message_files_update = MESSAGE_FILES_UPDATE
    message_files_delete = MESSAGE_FILES_DELETE
    message_read = MESSAGE_READ
    message_files_names = MESSAGE_FILES_NAMES
    message_files_get = MESSAGE_FILES_GET
    chat_unread_count = CHAT_UNREAD_COUNT
    chat_typing = CHAT_TYPING
    chat = CHAT
    message = MESSAGE
    chat_messages = CHAT_MESSAGES
    user_chats = USER_CHATS
