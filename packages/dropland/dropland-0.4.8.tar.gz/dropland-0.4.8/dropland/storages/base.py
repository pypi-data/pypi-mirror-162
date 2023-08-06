import contextlib
import inspect
import pickle
from builtins import property
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
from importlib import import_module
from types import ClassMethodDescriptorType, FunctionType, GetSetDescriptorType, MappingProxyType, MemberDescriptorType, \
    MethodDescriptorType, MethodType, MethodWrapperType, WrapperDescriptorType
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Set, Union

from pydantic.main import BaseModel as PydanticModel

from dropland.data.context import ContextData


@dataclass
class FieldsCache:
    priv: Set[str] = field(default_factory=set)
    pub: Set[str] = field(default_factory=set)
    ser: Set[str] = field(default_factory=set)


class StorageBackend:
    @property
    def name(self) -> str:
        raise NotImplementedError


class StorageEngine:
    def __init__(self, backend: StorageBackend):
        self._backend = backend

    @property
    def backend(self):
        return self._backend

    @property
    def is_async(self):
        raise NotImplementedError

    def new_connection(self):
        raise NotImplementedError

    def start(self):
        pass

    def stop(self):
        pass

    async def async_start(self):
        pass

    async def async_stop(self):
        pass


@dataclass
class Relationship:
    key: Union[str, Callable[['StorageModel'], str]]
    model: Union[type, str]
    single: bool = True
    _globals: Dict[str, Any] = field(default_factory=lambda: inspect.stack()[2][0].f_globals, repr=False, compare=False)

    def get_key(self, instance: 'StorageModel'):
        if callable(self.key):
            return self.key(instance)
        return getattr(instance, self.key)

    def get_model(self):
        if isinstance(self.model, str):
            if '.' in self.model:
                class_path, class_name = self.model.rsplit('.', maxsplit=1)
                try:
                    module = import_module(class_path)
                    return getattr(module, class_name)
                except ImportError:
                    pass

            if self.model in self._globals:
                return self._globals[self.model]
            else:
                return eval(self.model, self._globals)

        return self.model


class StorageModel:
    class Meta:
        private_fields: Set[str] = set()
        public_fields: Set[str] = set()
        serializable_fields: Set[str] = set()
        non_serializable_fields: Set[str] = set()
        _fields_cache: Dict[str, FieldsCache] = dict()
        relationships: Dict[str, Relationship] = dict()

    def get_id_value(self) -> Any:
        raise NotImplementedError

    @classmethod
    def get_engine(cls) -> StorageEngine:
        raise NotImplementedError

    @classmethod
    def has_cache(cls):
        return False

    @classmethod
    def _fields_cache_key(cls):
        return '.'.join([cls.__module__, cls.__qualname__])

    # noinspection PyProtectedMember
    @classmethod
    def _calculate_fields(cls):
        private_types = (
            type, FunctionType, MethodType, MappingProxyType,
            WrapperDescriptorType, MethodWrapperType, MethodDescriptorType,
            ClassMethodDescriptorType, GetSetDescriptorType, MemberDescriptorType
        )

        private_fields, public_fields, serializable_fields = set(), set(), set()
        relationship_keys = cls.Meta.relationships.keys()

        for field in dir(cls):
            value = getattr(cls, field)
            if isinstance(value, private_types) or field[0] == '_':
                private_fields.add(field)
            elif not isinstance(value, private_types):
                if not isinstance(value, property) and field not in relationship_keys:
                    serializable_fields.add(field)
                public_fields.add(field)

        private_fields.update(cls.Meta.private_fields)
        private_fields.difference_update(cls.Meta.public_fields)
        public_fields.update(cls.Meta.public_fields)
        public_fields.difference_update(cls.Meta.private_fields)
        serializable_fields.update(cls.Meta.serializable_fields)
        serializable_fields.difference_update(cls.Meta.non_serializable_fields)
        cls.Meta._fields_cache[cls._fields_cache_key()] = \
            FieldsCache(priv=private_fields, pub=public_fields, ser=serializable_fields)

    # noinspection PyProtectedMember
    @classmethod
    def drop_fields_cache(cls):
        key = cls._fields_cache_key()
        cls.Meta._fields_cache.pop(key, None)

    # noinspection PyProtectedMember
    @classmethod
    def get_serializable_fields(cls) -> Set[str]:
        key = cls._fields_cache_key()
        if key not in cls.Meta._fields_cache:
            cls._calculate_fields()
        return cls.Meta._fields_cache[key].ser

    # noinspection PyProtectedMember
    @classmethod
    def get_private_fields(cls) -> Set[str]:
        key = cls._fields_cache_key()
        if key not in cls.Meta._fields_cache:
            cls._calculate_fields()
        return cls.Meta._fields_cache[key].priv

    # noinspection PyProtectedMember
    @classmethod
    def get_public_fields(cls) -> Set[str]:
        key = cls._fields_cache_key()
        if key not in cls.Meta._fields_cache:
            cls._calculate_fields()
        return cls.Meta._fields_cache[key].pub

    @classmethod
    def get_fields(cls) -> Set[str]:
        return cls.get_public_fields()

    def get_values(
        self, only_fields: List[str] = None,
            exclude_fields: List[str] = None) -> Dict[str, Any]:
        public_fields = self.get_public_fields()
        only_fields = set(only_fields) if only_fields else set()
        exclude_fields = set(exclude_fields) if exclude_fields else set()

        return {
            name: getattr(self, name) for name in public_fields
            if hasattr(self, name) and (not only_fields or name in only_fields)
                and (not exclude_fields or name not in exclude_fields)
        }

    @classmethod
    async def get(cls, id_value: Any, **kwargs) -> Optional['StorageModel']:
        raise NotImplementedError

    async def save(self, *args, **kwargs) -> bool:
        raise NotImplementedError

    async def load(self, field_names: List[str] = None) -> bool:
        raise NotImplementedError

    @classmethod
    async def get_any(cls, indices: List[Any], **kwargs) -> List[Optional['StorageModel']]:
        raise NotImplementedError

    @classmethod
    async def save_all(cls, objects: List['StorageModel'], *args, **kwargs) -> bool:
        raise NotImplementedError

    #
    # Construct operations
    #

    def assign(self, data: Dict[str, Any]) -> 'StorageModel':
        for k, v in data.items():
            setattr(self, k, v)
        return self

    @classmethod
    async def construct(cls, ctx: ContextData, data, **kwargs) -> Optional['StorageModel']:
        if isinstance(data, dict):
            if issubclass(cls, PydanticModel):
                return cls(**data)
            else:
                return cls().assign(data)
        return data

    @classmethod
    async def construct_rela(
        cls, ctx: ContextData, instance: Optional['StorageModel'],
            load_fields: Optional[Set[str]] = None, **kwargs) -> Optional['StorageModel']:
        res = await cls.construct_relationships(ctx, [instance], load_fields, **kwargs)
        return res[0]

    @classmethod
    async def construct_list(
            cls, ctx: ContextData, objects: List['StorageModel'], **kwargs) -> List['StorageModel']:
        for i, data in enumerate(objects):
            if data is not None:
                objects[i] = await cls.construct(ctx, data, **kwargs)
        return objects

    @classmethod
    async def construct_rela_list(
        cls, ctx: ContextData, objects: List['StorageModel'],
            load_fields: Optional[Set[str]] = None, **kwargs) -> List['StorageModel']:
        return await cls.construct_relationships(ctx, objects, load_fields, **kwargs)

    @classmethod
    async def construct_relationships(
        cls, _: ContextData, objects: List['StorageModel'],
            load_fields: Optional[Set[str]] = None, **kwargs) -> List['StorageModel']:
        deps_ids: Dict[str, Dict[Any, Set[Any]]] = defaultdict(lambda: defaultdict(set))
        deps_values: Dict[str, Dict[Any, Any]] = defaultdict(dict)
        rela_map = cls.Meta.relationships.items()
        load_all = load_fields is None

        for instance in objects:
            if instance is None:
                continue

            for dep_key, relationship in rela_map:
                if not load_all and dep_key not in load_fields:
                    continue

                dep_key_value = relationship.get_key(instance)

                if relationship.single:
                    dep_key_value = [dep_key_value]

                deps_ids[dep_key][instance.get_id_value()].update(set(dep_key_value))

        for dep_key, relationship in rela_map:
            dep_keys = set()
            for v in deps_ids[dep_key].values():
                dep_keys.update(v)
            model_class = relationship.get_model()
            dep_values = await model_class.get_any(list(dep_keys), **kwargs)

            for k, v in zip(dep_keys, dep_values):
                deps_values[dep_key][k] = v

        for instance in objects:
            if instance is None:
                continue

            for dep_key, relationship in rela_map:
                if not load_all and dep_key not in load_fields:
                    continue

                dep_key_values = list(deps_ids[dep_key][instance.get_id_value()])

                if relationship.single:
                    dep_key_value = dep_key_values[0] if len(dep_key_values) > 0 else dep_key_values
                    dep_value = deps_values[dep_key][dep_key_value]
                    setattr(instance, dep_key, dep_value)
                else:
                    dep_values = [deps_values[dep_key][k] for k in dep_key_values]
                    setattr(instance, dep_key, dep_values)

        return objects


class CacheModel(StorageModel):
    class Meta(StorageModel.Meta):
        cache_ttl_enable = True

    @classmethod
    def get_model_cache_key(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_cache_id(cls, id_value: Any) -> str:
        return str(id_value)

    @classmethod
    def get_cache_key(cls, id_value: Any) -> str:
        return f'{cls.get_model_cache_key()}:{cls.get_cache_id(id_value)}'

    def get_id_value(self) -> Any:
        raise NotImplementedError

    def get_serializable_values(self, only_fields: List[str] = None) -> Dict[str, Any]:
        serializable_fields = self.get_serializable_fields()
        only_fields = set(only_fields) if only_fields else set()

        return {
            name: getattr(self, name) for name in serializable_fields
            if hasattr(self, name) and (not only_fields or name in only_fields)
        }

    def serialize(self, only_fields: List[str] = None) -> bytes:
        return pickle.dumps(self.get_serializable_values(only_fields))

    @classmethod
    def deserialize(cls, data: bytes) -> Optional[Dict[str, Any]]:
        try:
            values = pickle.loads(data) if data else None
        except (pickle.UnpicklingError, ValueError, ModuleNotFoundError, MemoryError):
            return None

        return values

    @classmethod
    @contextlib.asynccontextmanager
    async def _async_connection_context(cls, ctx: ContextData = None):
        raise NotImplementedError

    @classmethod
    async def get(cls, id_value: Any, **kwargs) -> Optional['CacheModel']:
        async with cls._async_connection_context() as ctx:
            exists, data = await cls._load_one(ctx, cls.get_cache_key(id_value))
            if exists:
                if instance := await cls.construct(ctx, data, **kwargs):
                    return await cls.construct_rela(ctx, instance, **kwargs)
        return None

    @classmethod
    async def get_any(cls, indices: List[Any], **kwargs) -> List[Optional['CacheModel']]:
        async with cls._async_connection_context() as ctx:
            data = await cls._load_many(ctx, indices, **kwargs)
            objects = await cls.construct_list(ctx, data, **kwargs)
            return await cls.construct_rela_list(ctx, objects, **kwargs)

    async def save(self, exp: Optional[timedelta] = None, **kwargs) -> bool:
        async with self._async_connection_context() as ctx:
            return await self._cache_one(ctx, self, exp=exp, **kwargs)

    async def load(self, field_names: List[str] = None) -> bool:
        async with self._async_connection_context() as ctx:
            exists, data = await self._load_one(ctx, self.get_cache_key(self.get_id_value()))
            if exists:
                await type(self).construct_rela(
                    ctx, self.assign(data), load_fields=set(field_names) if field_names else set())
                return True
        return False

    @classmethod
    async def save_all(cls, objects: List['CacheModel'], exp: timedelta = None, **kwargs) -> bool:
        async with cls._async_connection_context() as ctx:
            return await cls._cache_many(ctx, objects, exp, **kwargs)

    async def drop(self) -> bool:
        async with self._async_connection_context() as ctx:
            return await self._drop_one(ctx, self.get_cache_key(self.get_id_value()))

    @classmethod
    async def drop_all(cls, indices: List[Any] = None) -> bool:
        async with cls._async_connection_context() as ctx:
            return await cls._drop_many(ctx, indices)

    @classmethod
    async def exists(cls, id_value: Any) -> bool:
        async with cls._async_connection_context() as ctx:
            return await cls._exists(ctx, cls.get_cache_key(id_value))

    @classmethod
    async def scan(cls, match: str, count: int = None, **kwargs) -> Tuple[str, Optional['CacheModel']]:
        async with cls._async_connection_context() as ctx:
            async for k, data in cls._scan(ctx, cls.get_model_cache_key(), match, count):
                if data is None:
                    yield k, None
                elif instance := await cls.construct(ctx, data, **kwargs):
                    yield k, await cls.construct_rela(ctx, instance, **kwargs)
                else:
                    yield k, None

    @classmethod
    async def _cache_one(
        cls, ctx: ContextData, instance: Optional['CacheModel'] = None,
            id_value: Optional[Any] = None, data: Optional[Dict[str, Any]] = None,
            exp: Optional[timedelta] = None, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    async def _cache_many(
            cls, ctx: ContextData, objects: List['CacheModel'], exp: timedelta = None, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    async def _load_one(
            cls, ctx: ContextData, cache_key: str, **kwargs) -> Tuple[bool, Optional[Dict[str, Any]]]:
        raise NotImplementedError

    @classmethod
    async def _load_many(
            cls, ctx: ContextData, indices: List[Any], **kwargs) -> List[Optional[Dict[str, Any]]]:
        raise NotImplementedError

    @classmethod
    async def _drop_one(cls, ctx: ContextData, cache_key: str) -> bool:
        raise NotImplementedError

    @classmethod
    async def _drop_many(cls, ctx: ContextData, indices: List[Any] = None) -> bool:
        raise NotImplementedError

    @classmethod
    async def _exists(cls, ctx: ContextData, cache_key: str) -> bool:
        raise NotImplementedError

    @classmethod
    @contextlib.asynccontextmanager
    async def _scan(cls, ctx: ContextData, cache_key: str = None,
                    match: str = None, count: int = None) -> Tuple[str, Optional[Dict[str, Any]]]:
        raise NotImplementedError
