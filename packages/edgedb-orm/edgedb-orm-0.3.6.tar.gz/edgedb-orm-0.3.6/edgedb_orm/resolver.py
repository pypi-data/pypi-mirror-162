import typing as T
from uuid import UUID
from enum import Enum
import re
import edgedb
from devtools import debug
from pydantic import BaseModel, PrivateAttr
from .execute import query as execute_query
from .node import Node
from .constants import ALIAS_PATTERN, random_str
from .span import safe_span

NodeType = T.TypeVar("NodeType", bound=Node)

FILTER_FIELDS = ["_filter", "_limit", "_offset", "_order_by"]

ThisResolverType = T.TypeVar("ThisResolverType", bound="Resolver")


class ResolverException(Exception):
    pass


class UpdateOperation(str, Enum):
    """You can clear by choosing a resolver with REMOVE without filters"""

    REPLACE = ":="
    ADD = "+="
    REMOVE = "-="


EdgeResolverType = T.TypeVar("EdgeResolverType", bound="Resolver")


class DependencyInfo(BaseModel):
    fields: T.Set[str]
    ignore_if_admin: bool
    ignore_if_no_auth_id: bool
    require_user: bool
    # name of edge using
    edge: str
    # resolver instead of any
    required_nested_resolver_f_map: dict[str, set[T.Callable]] = {}


FieldDepMapAlias = T.Dict[str, DependencyInfo]


class FilterConnector(str, Enum):
    AND = " AND "
    OR = " OR "


from .nested_resolvers import NestedResolvers


class Resolver(BaseModel, T.Generic[NodeType]):
    """Can construct an EdgeQL query string from this!"""

    _node: T.ClassVar[T.Type[NodeType]]
    _edge_resolver_map: T.ClassVar[T.Dict[str, EdgeResolverType]]
    _field_dependency_map: T.ClassVar[FieldDepMapAlias]

    _filter: str = PrivateAttr(None)
    _order_by: str = PrivateAttr(None)
    _limit: int = PrivateAttr(None)
    _offset: int = PrivateAttr(None)
    _extra_fields: str = PrivateAttr(None)

    # this is for importing functions or libraries i think
    _modules: str = PrivateAttr(None)

    # this is just for updating
    _update_operation: UpdateOperation = PrivateAttr(None)

    _query_variables: T.Dict[str, T.Any] = PrivateAttr(default_factory=dict)
    _nested_resolvers: NestedResolvers = PrivateAttr(default_factory=NestedResolvers)

    _fields_to_return: T.Set[str] = PrivateAttr(None)
    _fields_to_include: T.Set[str] = PrivateAttr(default_factory=set)

    _merged: bool = PrivateAttr(False)
    _metadata: dict = PrivateAttr(default=dict)

    _pre_merge_resolver: T.Optional["Resolver"] = PrivateAttr(None)

    def __hash__(self):
        return hash(
            str(self._get_nested_query_variables()) + self.to_str() + self._model_name
        )

    @staticmethod
    def replace_str_with_vars(s: str, d: dict) -> str:
        if not s:
            return ""
        for var_name, var_val in d.items():
            s = re.sub(
                rf"(\$)({var_name})(\W*)", r"\1" + f"[({var_val})]" + r"\3", s
            ).replace(f"[({var_val})]", f"{var_val}")
        return s

    def to_compare_filter_str(self) -> str:
        q_str = self.all_filters_str()
        q_str = self.replace_str_with_vars(s=q_str, d=self._query_variables)
        return q_str

    def to_compare_extra_str(self) -> str:
        return self.replace_str_with_vars(s=self._extra_fields, d=self._query_variables)

    def is_subset(self, other: "Resolver", should_debug: bool = False) -> bool:
        # first compare top level resolver, then go down from there
        # if self has more fields to return than other, self cannot be a subset
        if set(self.get_fields_to_return()) - set(other.get_fields_to_return()):
            if should_debug:
                print(f"self {self.__class__.__name__} has more fields than other")
            return False

        # if other does not have all extra fields that self has, return false
        if self._extra_fields:
            if self.to_compare_extra_str() not in other.to_compare_extra_str():
                if should_debug:
                    print("GOING FALSE IN EXTRA FIELDS")
                return False

        # if self has different filters than other, self cannot be a subset
        if self.to_compare_filter_str() != other.to_compare_filter_str():
            if should_debug:
                print(
                    f"self {self.__class__.__name__} has diff filters, "
                    f"{self.to_compare_filter_str()=} {other.to_compare_filter_str()=}"
                )
            return False
        # now nested resolvers
        if not self._nested_resolvers.is_subset(other._nested_resolvers):
            if should_debug:
                print("NESTED RESOLVERS NO GO")
            return False
        return True

    """PROPERTIES"""

    @property
    def metadata(self) -> dict:
        return self._metadata

    @classmethod
    def set_field_dependency_map(cls, field_dep_map: FieldDepMapAlias) -> None:
        cls._field_dependency_map = field_dep_map

    @property
    def nested_resolvers(self) -> NestedResolvers:
        return self._nested_resolvers

    @classmethod
    @property
    def field_dependency_map(cls) -> FieldDepMapAlias:
        if getattr(cls, "_field_dependency_map", None) is None:
            cls.set_field_dependency_map(dict())
        return cls._field_dependency_map

    @classmethod
    def add_required_nested_resolver(
        cls, field: str, edge: str, resolver_f: callable
    ) -> None:
        # TODO need all this dependency info shit? -> it is really resolver dependent
        if field not in cls.field_dependency_map:
            cls.field_dependency_map[field] = DependencyInfo(
                fields=set(),
                ignore_if_admin=False,
                ignore_if_no_auth_id=False,
                require_user=False,
                edge=field,
            )
        prev_dep_info: DependencyInfo = cls.field_dependency_map[field]
        f_map = prev_dep_info.required_nested_resolver_f_map
        if edge not in f_map:
            f_map[edge] = set()
        f_map[edge].add(resolver_f)

    @classmethod
    def upsert_dependency_info(cls, field: str, dep_info: DependencyInfo) -> None:
        if getattr(cls, "_field_dependency_map", None) is None:
            cls.set_field_dependency_map(dict())
        prev_dep_info: DependencyInfo = cls._field_dependency_map.get(field)
        if prev_dep_info:
            prev_dep_info.fields.update(dep_info.fields)
            prev_dep_info.require_user = (
                prev_dep_info.require_user or dep_info.require_user
            )
            prev_dep_info.ignore_if_admin = (
                prev_dep_info.ignore_if_admin and dep_info.ignore_if_admin
            )
            prev_dep_info.ignore_if_no_auth_id = (
                prev_dep_info.ignore_if_no_auth_id and dep_info.ignore_if_no_auth_id
            )
        else:
            cls._field_dependency_map[field] = dep_info

    @classmethod
    @property
    def _model_name(cls) -> str:
        return cls._node._model_name

    def get_fields_to_return(self) -> T.List[str]:
        """Include nested fields with DOT notation"""
        if self._fields_to_return is None:
            fields = {
                *(self.get_aliases() - self._node._appendix_properties),
                *self._fields_to_include,
            }
        else:
            fields = self._fields_to_return
        return sorted(list(fields))

    @property
    def _filter_str(self) -> str:
        if not self._filter:
            return ""
        return f"FILTER {self._filter}"

    @property
    def _order_by_str(self) -> str:
        if not self._order_by:
            return ""
        return f"ORDER BY {self._order_by}"

    @property
    def _limit_str(self) -> str:
        if self._limit is None or self._limit == 0:
            return ""
        return f"LIMIT {self._limit}"

    @property
    def _offset_str(self) -> str:
        if self._offset is None or self._offset == 0:
            return ""
        return f"OFFSET {self._offset}"

    @property
    def filters_to_dict(self) -> T.Dict[str, T.Any]:
        return {
            "filter": self._filter,
            "order by": self._order_by,
            "limit": self._limit,
            "offset": self._offset,
        }

    @property
    def update_operation_str(self) -> str:
        if not self._update_operation:
            return ""
        return self._update_operation.value

    """SETTERS"""

    def fields_to_return(
        self: ThisResolverType, *fields_to_return: str
    ) -> ThisResolverType:
        self._fields_to_return = set(fields_to_return)
        return self

    def include_fields(
        self: ThisResolverType, *fields_to_include: str
    ) -> ThisResolverType:
        self._fields_to_include.update(set(fields_to_include))
        return self

    def exclude_fields(
        self: ThisResolverType, *fields_to_exclude: str
    ) -> ThisResolverType:
        self._fields_to_include = self._fields_to_include - set(fields_to_exclude)
        return self

    def include_computed_fields(self: ThisResolverType) -> ThisResolverType:
        self._fields_to_include.update(self._node._computed_properties)
        return self

    def include_appendix_fields(self: ThisResolverType) -> ThisResolverType:
        self._fields_to_include.update(self._node._appendix_properties)
        return self

    @staticmethod
    def validate_no_intersections_helper(
        set_a: T.Set = None, set_b: T.Set = None
    ) -> None:
        if set_a is None or set_b is None:
            return
        if used_keys := (set(set_a) & set(set_b)):
            raise ResolverException(
                f"Variable(s) {','.join(used_keys)} are already used."
            )

    def validate_against_query_variables(self, new_variables: dict = None) -> None:
        if not new_variables:
            return
        set_a = set(self._get_nested_query_variables().keys())
        set_b = set(new_variables.keys())
        self.validate_no_intersections_helper(set_a, set_b)

    def _add_variables(
        self, /, variables: T.Optional[T.Dict[str, T.Any]] = None
    ) -> None:
        # turn enums into strs
        if variables:
            variables = {
                k: v if not isinstance(v, Enum) else v.value
                for k, v in variables.items()
            }
        if variables is not None:
            self.validate_against_query_variables(variables)
            self._query_variables = {**self._query_variables, **variables}

    def modules(self: ThisResolverType, module_str: str) -> ThisResolverType:
        if self._modules:
            raise ResolverException(
                f"Module of {self._modules} has already been provided."
            )
        self._modules = module_str
        return self

    def filter(
        self: ThisResolverType,
        filter_str: str,
        variables: T.Optional[T.Dict[str, T.Any]] = None,
        connector: FilterConnector = FilterConnector.AND,
    ) -> ThisResolverType:
        if self._filter and not connector:
            raise ResolverException(
                f"Filter of {self._filter} has already been provided."
            )
        # TODO change variable names
        self._add_variables(variables)
        if not self._filter:
            self._filter = ""
        else:
            if connector and self._filter:
                self._filter += connector.value
        self._filter += filter_str
        return self

    def filter_by(self, connector: FilterConnector = FilterConnector.AND, **kwargs):
        """For now, only expecting one key value pair to be given, but could be more in future"""
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if not kwargs:
            raise ResolverException("Nothing to filter by.")
        conversion_map = self._node._edgedb_conversion_map
        filter_strs = []
        variables = {}
        for field_name, field_value in kwargs.items():
            cast = conversion_map[field_name]["cast"]
            variable_name = f"{field_name}{random_str(10)}"
            filter_strs.append(f".{field_name} = <{cast}>${variable_name}")
            variables[variable_name] = field_value
        filter_str = " AND ".join(filter_strs)
        return self.filter(
            filter_str=filter_str, variables=variables, connector=connector
        )

    def filter_in(
        self, connector: FilterConnector = FilterConnector.AND, **kwargs: list
    ):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if not kwargs:
            raise ResolverException("Nothing to filter by.")
        conversion_map = self._node._edgedb_conversion_map
        filter_strs = []
        variables = {}
        for field_name, value_lst in kwargs.items():
            cast = conversion_map[field_name]["cast"]
            variable_name = f"{field_name}s{random_str(10)}"
            filter_strs.append(
                f".{field_name} in array_unpack(<array<{cast}>>${variable_name})"
            )
            variables[variable_name] = value_lst
        filter_str = " AND ".join(filter_strs)
        return self.filter(
            filter_str=filter_str, variables=variables, connector=connector
        )

    def extra_fields(
        self: ThisResolverType,
        extra_fields_str: str,
        variables: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> ThisResolverType:
        if self._extra_fields:
            raise ResolverException(
                f"Extra fields of {self._extra_fields} has already been provided."
            )
        # TODO change variable names
        self._add_variables(variables)
        self._extra_fields = extra_fields_str
        return self

    def order_by(
        self: ThisResolverType,
        order_by_str: str,
        variables: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> ThisResolverType:
        if self._order_by:
            raise ResolverException(
                f"Order by of {self._order_by} has already been provided."
            )
        self._add_variables(variables)
        self._order_by = order_by_str
        return self

    def limit(self: ThisResolverType, /, _: T.Optional[int]) -> ThisResolverType:
        if self._limit is not None:
            raise ResolverException(
                f"Limit of {self._limit} has already been provided."
            )
        self._limit = _
        return self

    def offset(self: ThisResolverType, /, _: T.Optional[int]) -> ThisResolverType:
        if self._offset is not None:
            raise ResolverException(
                f"Offset of {self._offset} has already been provided."
            )
        self._offset = _
        return self

    def update_operation(
        self: ThisResolverType,
        operation: UpdateOperation = None,
        *,
        add: bool = None,
        replace: bool = None,
        remove: bool = None,
    ) -> ThisResolverType:
        if self._update_operation:
            raise ResolverException(
                f"update_operation of {self._update_operation} has already been provided."
            )
        if operation:
            self._update_operation = operation
            return self
        if len([None for _ in [add, replace, remove] if _ is None]) != 2:
            raise ResolverException("Must give exactly one update operation")
        if add:
            opp = UpdateOperation.ADD
        elif replace:
            opp = UpdateOperation.REPLACE
        elif remove:
            opp = UpdateOperation.REMOVE
        else:
            raise ResolverException("Must provide an update operation")
        self._update_operation = opp
        return self

    """QUERY STRING"""

    def _get_nested_query_variables(self) -> T.Dict[str, T.Any]:
        query_variables = {**self._query_variables}
        for nested_resolver in self._nested_resolvers.all_resolvers():
            nested_query_variables = nested_resolver._get_nested_query_variables()
            if not nested_query_variables:
                continue
            if intersections := set(query_variables.keys()).intersection(
                set(nested_query_variables.keys())
            ):
                for intersection_key in intersections:
                    if (
                        query_variables[intersection_key]
                        != nested_query_variables[intersection_key]
                    ):
                        raise ResolverException(
                            f"'{intersection_key}' query value used multiple times with different value."
                        )
            query_variables = {**query_variables, **nested_query_variables}
        return query_variables

    def all_filters_str(self) -> str:
        s_lst: list[str] = [
            self._filter_str,
            self._order_by_str,
            self._offset_str,
            self._limit_str,
        ]
        s = " ".join([s for s in s_lst if s])
        if s:
            return " " + s
        return ""

    def to_str(self, include_filters: bool = True, ignore_nested: bool = False) -> str:
        """
        OUTPUT: { name, created_at, bookings: { created_at } FILTER .created_at > $booking_created_at } FILTER .name = $name }
        """
        s = ""
        s += ", ".join(self.get_fields_to_return())
        if self._extra_fields:
            s += f", {self._extra_fields}"
        nested_resolver_str = self._nested_resolvers.to_str()
        if nested_resolver_str:
            s += f", {nested_resolver_str}"
        s = f"{{ {s} }}"
        if include_filters:
            s += self.all_filters_str()
        return s

    """HELPERS"""

    def has_filters(self) -> T.Optional[str]:
        for field in FILTER_FIELDS:
            if (val := getattr(self, field)) is not None:
                return val
        return None

    def clear_filters(self, remove_id_variable: bool = True) -> None:
        for field in FILTER_FIELDS:
            setattr(self, field, None)
        """Clearing filters does not clear query variables. 
        This is because you are only clearing the first level of filters."""
        if remove_id_variable:
            if "id" in self._query_variables:
                del self._query_variables["id"]

    """QUERY"""

    def full_query_str(self) -> str:
        module_str = "" if not self._modules else f"{self._modules} "
        return f"{module_str}SELECT {self._model_name} {self.to_str()}"

    def inner_delete_str(self) -> str:
        return f"DELETE {self._model_name} {self._filter_str}"

    def full_delete_str(self) -> str:
        return (
            f"WITH model := ({self.inner_delete_str()}) "
            f"SELECT model {self.to_str(include_filters=False)}"
        )

    async def query(
        self,
        given_client: edgedb.AsyncIOClient = None,
        only_one: bool = False,
        merge: bool = True,
    ) -> T.Union[T.List[NodeType], NodeType]:
        if merge:
            self.merge()
        query_str = self.full_query_str()
        with safe_span(
            op=f"edgedb.query.{self._model_name}", description=query_str[:200]
        ):
            raw_d = await execute_query(
                client=given_client or self._node.db_client,
                query_str=query_str,
                variables=self._get_nested_query_variables(),
                only_one=only_one,
            )
        description = len(raw_d) if not only_one else "only-one"
        with safe_span(op=f"parse.{self._model_name}", description=f"{description}"):
            if not only_one:
                return [self.parse_nested_obj(d) for d in raw_d]
            if not raw_d:
                return None
            return self.parse_nested_obj(raw_d)

    def clear_top_level_filters_and_variables(self) -> None:
        if self._filter:
            variables = re.findall(ALIAS_PATTERN, self._filter)
            for variable in variables:
                if variable in self._query_variables:
                    del self._query_variables[variable]
        self.clear_filters()

    async def get(
        self, *, given_client: edgedb.AsyncIOClient = None, merge: bool = True, **kwargs
    ) -> T.Optional[NodeType]:
        if merge:
            self.merge()
        """Caveat is this must be a string value or an UUID"""
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if len(kwargs) != 1:
            raise ResolverException(f"Must only give one argument, received {kwargs}")
        # if getting, make sure there are no filters attached to the resolver
        if existing_filter_str := self.has_filters():
            raise ResolverException(
                f"This resolver already has filters: {existing_filter_str}. "
                f"If you wish to GET an object, use a new resolver."
            )
        key, value = list(kwargs.items())[0]
        if key not in self._node._exclusive_fields:
            raise ResolverException(f"Field '{key}' is not exclusive.")
        # this is to avoid nested collisions
        conversion_map = self._node._edgedb_conversion_map
        variables = {key: value}
        value_str = f'<{conversion_map[key]["cast"]}>${key}'
        self.filter(f".{key} = {value_str}", variables=variables)
        query_str = self.full_query_str()
        with safe_span(op=f"get.{self._model_name}", description=query_str[:200]):
            raw_d = await execute_query(
                client=given_client or self._node.db_client,
                query_str=query_str,
                variables=self._get_nested_query_variables(),
                only_one=True,
            )
        if not raw_d:
            return None
        with safe_span(op=f"parse.{self._model_name}"):
            return self.parse_nested_obj(raw_d)

    async def gerror(
        self, *, given_client: edgedb.AsyncIOClient = None, merge: bool = True, **kwargs
    ) -> NodeType:
        model = await self.get(merge=merge, **kwargs)
        if not model:
            raise ResolverException(f"No {self._model_name} in db with fields {kwargs}")
        return model

    @classmethod
    def get_aliases(cls: T.Type[ThisResolverType]) -> T.Set[str]:
        return cls._node.get_aliases()

    def parse_nested_obj(
        self, raw_d: dict, error_for_extra_fields: bool = False
    ) -> NodeType:
        node: NodeType = self._node.parse_obj(raw_d)
        # pass on other fields as an "extra" dict
        # problem with this is aliases are currently also added to extra... do i want this?
        other_fields = set(raw_d.keys()) - self.get_aliases()
        for field_name in sorted(other_fields):
            resolver = self._nested_resolvers.resolver_from_field_name(field_name)
            if resolver is None:
                message = f"No nested resolver for {field_name=} found."
                if error_for_extra_fields:
                    raise ResolverException(message)
                node.extra[field_name] = raw_d[field_name]
                # print(message)
                continue
            nested_d = raw_d[field_name]
            value_to_save = nested_d
            if nested_d:
                if (list_or_set := type(nested_d)) in {list, set}:
                    val = list_or_set(resolver.parse_nested_obj(d) for d in nested_d)
                else:
                    val = resolver.parse_nested_obj(nested_d)
                value_to_save = val
            edge_name = NestedResolvers.edge_from_field_name(field_name)
            node.cache.add(
                edge=edge_name, resolver=resolver, val=value_to_save, raw_d=raw_d
            )
        node._used_resolver = self.copy(deep=True)
        node._original_dict = raw_d.copy()
        return node

    def merge(self) -> None:
        from .resolver_helpers import merge_nested_resolver

        pre_merge_resolver = self.copy(deep=True)
        self._pre_merge_resolver = pre_merge_resolver
        self._nested_resolvers = merge_nested_resolver(self.nested_resolvers)

    def debug_nested_resolvers(self) -> None:
        debug(self._nested_resolvers)
        for edge, resolvers in self._nested_resolvers.d.items():
            print(f"{edge=}")
            for r in resolvers:
                r.debug_nested_resolvers()
