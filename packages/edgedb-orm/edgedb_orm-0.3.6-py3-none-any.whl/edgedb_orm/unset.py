from pydantic import BaseModel
import typing as T


class UnsetType(BaseModel):
    __instance: T.Optional["UnsetType"] = None

    def __new__(cls: T.Type["UnsetType"]) -> "UnsetType":
        if cls.__instance is None:
            ret = super().__new__(cls)
            cls.__instance = ret
            return ret
        else:
            return cls.__instance

    def __str__(self):
        return ""

    def __repr__(self) -> str:
        return "UNSET"

    def __bool__(self):
        return False


UNSET: T.Any = UnsetType()


class ComputedPropertyException(Exception):
    pass


class AppendixPropertyException(Exception):
    pass
