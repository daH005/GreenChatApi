from enum import StrEnum

from common.resident_app import resident_app

__all__ = (
    'KeyPrefix',
)


class KeyPrefix(StrEnum):
    EMAIL_CODE = 'greenchat_email_code_'
    EMAIL_CODE_COUNT = 'greenchat_email_code_count_'

    def get(self, identify: str) -> str:
        return resident_app.get(self + identify)

    def set(self, identify: str,
            value: str | int,
            expires: float | None = None,
            ) -> None:
        resident_app.set(self + identify, value, ex=expires)

    def delete(self, identify: str) -> None:
        resident_app.delete(self + identify)

    def exists(self, identify: str) -> bool:
        return resident_app.exists(self + identify)
