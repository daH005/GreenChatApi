from abc import ABCMeta

__all__ = (
    'SingletonMeta',
    'AbstractSingletonMeta',
)


def _create_singleton_meta(base_metatype: type[type]):

    class _SingletonMeta(base_metatype):
        __instances: dict[type, object] = {}

        def __call__(cls, *args, **kwargs) -> object:
            if cls not in cls.__instances:
                cls.__instances[cls] = super().__call__(*args, **kwargs)
            return cls.__instances[cls]
    return _SingletonMeta


SingletonMeta = _create_singleton_meta(type)
AbstractSingletonMeta = _create_singleton_meta(ABCMeta)
