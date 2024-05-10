__all__ = (
    'CHECK_EMAIL_SPECS',
    'AUTH_SPECS',
    'REFRESH_TOKEN_SPECS',
    'USER_INFO_SPECS',
    'USER_AVATAR_SPECS',
    'USER_EDIT_INFO_SPECS',
    'USER_EDIT_AVATAR_SPECS',
    'USER_CHATS_SPECS',
    'SEND_CODE_SPECS',
    'CHECK_CODE_SPECS',
    'CHAT_HISTORY_SPECS',
)


def make_simple_request_response(status_code: int) -> dict:
    return {
        'schema': {
            'type': 'object',
            'properties': {
                'status': {'type': 'integer', 'example': status_code}
            },
        }
    }


USER_TAGS = ['User']
CHAT_TAGS = ['Chat']

SIMPLE_REQUEST_RESPONSES = {
    200: make_simple_request_response(200),
    400: make_simple_request_response(400),
    403: make_simple_request_response(403),
    404: make_simple_request_response(404),
    409: make_simple_request_response(409),
}

JWT_RESPONSE = {
    'schema': {
        'type': 'object',
        'properties': {
            'JWT': {
                'type': 'string',
            },
        },
    },
}

JWT_HEADER_PARAM = {
    'name': 'Authorization',
    'in': 'header',
    'required': True,
    'type': 'string',
    'example': 'Bearer {JWT}'
}

USER_INFO_SCHEMA = {
    'type': 'object',
    'required': [
        'id',
        'firstName',
        'lastName',
    ],
    'properties': {
        'id': {
            'type': 'integer',
        },
        'firstName': {
            'type': 'string',
        },
        'lastName': {
            'type': 'string',
        },
        'email': {
            'type': 'string',
        },
    },
}

CHAT_MESSAGE_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer',
        },
        'chatId': {
            'type': 'integer',
        },
        'userId': {
            'type': 'integer',
        },
        'text': {
            'type': 'string',
        },
        'creatingDatetime': {
            'type': 'string',
        },
        'isRead': {
            'type': 'boolean',
        },
    },
}

# SPECS:

CHECK_EMAIL_SPECS = {
    'tags': USER_TAGS,
    'parameters': [
        {
            'name': 'email',
            'in': 'query',
            'type': 'string',
            'required': True,
        },
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'object',
                'properties': {
                    'isAlreadyTaken': {
                        'type': 'boolean',
                    },
                },
            },
        },
        400: SIMPLE_REQUEST_RESPONSES[400],
    },
}

AUTH_SPECS = {
    'tags': USER_TAGS,
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                    },
                    'code': {
                        'type': 'integer',
                        'example': 9999,
                    },
                },
            },
        },
    ],
    'responses': {
        200: JWT_RESPONSE,
        201: JWT_RESPONSE,
        400: SIMPLE_REQUEST_RESPONSES[400],
    },
}

REFRESH_TOKEN_SPECS = {
    'tags': USER_TAGS,
    'parameters': [
        JWT_HEADER_PARAM,
    ],
    'responses': {
        200: JWT_RESPONSE,
    },
}

USER_INFO_SPECS = {
    'tags': USER_TAGS,
    'parameters': [
        JWT_HEADER_PARAM,
        {
            'name': 'id',
            'in': 'query',
            'type': 'integer',
            'required': False,
        }
    ],
    'responses': {
        200: {
            'schema': USER_INFO_SCHEMA,
        },
        400: SIMPLE_REQUEST_RESPONSES[400],
        404: SIMPLE_REQUEST_RESPONSES[404],
    }
}

USER_AVATAR_SPECS = {
    'tags': USER_TAGS,
    'parameters': [
        JWT_HEADER_PARAM,
        {
            'name': 'userId',
            'in': 'query',
            'type': 'integer',
            'required': True,
        }
    ],
    'responses': {
        200: {
            'description': 'Image file bytes',
        },
        400: SIMPLE_REQUEST_RESPONSES[400],
    }
}

USER_EDIT_INFO_SPECS = {
    'tags': USER_TAGS,
    'parameters': [
        JWT_HEADER_PARAM,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'firstName': {
                        'type': 'string',
                    },
                    'lastName': {
                        'type': 'string',
                    },
                },
            },
        },
    ],
    'responses': {
        200: SIMPLE_REQUEST_RESPONSES[200],
        400: SIMPLE_REQUEST_RESPONSES[400],
    }
}

USER_EDIT_AVATAR_SPECS = {
    'tags': USER_TAGS,
    'parameters': [
        JWT_HEADER_PARAM,
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'type': 'string',
            'format': 'byte',
            'description': 'Image file'
        },
    ],
    'responses': {
        200: SIMPLE_REQUEST_RESPONSES[200],
        400: SIMPLE_REQUEST_RESPONSES[400],
    }
}

USER_CHATS_SPECS = {
    'tags': USER_TAGS,
    'description': 'Chats sorted by "creatingDatetime" of "lastMessage" in descending order.',
    'parameters': [
        JWT_HEADER_PARAM,
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer',
                    },
                    'name': {
                        'type': ['null', 'string'],
                    },
                    'isGroup': {
                        'type': 'boolean',
                    },
                    'unreadCount': {
                        'type': 'integer',
                    },
                    'usersIds': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                    },
                    'lastMessage': CHAT_MESSAGE_SCHEMA,
                },
            }
        },
    }
}

SEND_CODE_SPECS = {
    'tags': USER_TAGS,
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                    },
                },
            },
        },
    ],
    'responses': {
        200: SIMPLE_REQUEST_RESPONSES[200],
        400: SIMPLE_REQUEST_RESPONSES[400],
        409: SIMPLE_REQUEST_RESPONSES[409],
    },
}

CHECK_CODE_SPECS = {
    'tags': USER_TAGS,
    'parameters': [
        {
            'name': 'email',
            'in': 'query',
            'type': 'string',
            'required': True,
        },
        {
            'name': 'code',
            'in': 'query',
            'type': 'integer',
            'required': True,
        },
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'object',
                'properties': {
                    'codeIsValid': {
                        'type': 'boolean',
                    }
                }
            }
        },
        400: SIMPLE_REQUEST_RESPONSES[400],
    },
}

CHAT_HISTORY_SPECS = {
    'tags': CHAT_TAGS,
    'description': 'Messages sorted by "creatingDatetime" in descending order.',
    'parameters': [
        JWT_HEADER_PARAM,
        {
            'name': 'chatId',
            'in': 'url',
            'type': 'integer',
            'required': True,
        },
        {
            'name': 'offsetFromEnd',
            'in': 'query',
            'type': 'integer',
            'required': False,
        }
    ],
    'responses': {
        200: {
            'schema': {
                'type': 'object',
                'properties': {
                    'messages': {
                        'type': 'array',
                        'items': CHAT_MESSAGE_SCHEMA,
                    }
                }
            }
        },
        400: SIMPLE_REQUEST_RESPONSES[400],
        403: SIMPLE_REQUEST_RESPONSES[403],
    }
}
