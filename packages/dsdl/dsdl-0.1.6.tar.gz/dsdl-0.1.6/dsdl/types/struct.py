from .field import Field
from .registry import registry
from ..exception import ValidationError


class StructMetaclass(type):
    def __new__(mcs, name, bases, attributes):
        super_new = super().__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, StructMetaclass)]
        if not parents:
            return super_new(mcs, name, bases, attributes)

        mappings = dict()
        for k, v in attributes.items():
            if isinstance(v, Field):
                mappings[k] = v
        for k in mappings.keys():
            attributes.pop(k)
        attributes["__mappings__"] = mappings
        new_class = super_new(mcs, name, bases, attributes)
        registry.register(name, new_class)
        return new_class


class Struct(dict, metaclass=StructMetaclass):
    def __init__(self, file_reader=None, **kwargs):
        super().__init__()
        self.file_reader = file_reader
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):

        if key not in self.__mappings__:
            self[key] = value
            return

        if hasattr(self.__mappings__[key], "set_file_reader"):
            self.__mappings__[key].set_file_reader(self.file_reader)
        try:
            self[key] = self.__mappings__[key].validate(value)
        except ValidationError as error:
            raise ValidationError(f"Field '{key}' validation error: {error}.")

    def get_mapping(self):
        return self.__mappings__
