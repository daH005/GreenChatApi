from flask import request

__all__ = (
    'make_user_identify'
)


def make_user_identify() -> str:
    return request.remote_addr + request.user_agent.string
