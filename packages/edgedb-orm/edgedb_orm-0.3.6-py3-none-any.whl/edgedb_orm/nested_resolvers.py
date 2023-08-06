import typing as T
from pydantic import BaseModel

if T.TYPE_CHECKING:
    from .resolver import Resolver

SEPARATOR = "__AHH__"


class NestedResolvers(BaseModel):
    d: dict[str, list[T.Any]] = {}

    def get(self, edge: str) -> list["Resolver"]:
        return self.d.get(edge, [])

    def has(self, edge: str) -> bool:
        return edge in self.d

    def add(
        self,
        edge: str,
        resolver: "Resolver",
        *,
        merge: bool = False,
        ignore_if_subset: bool = False,
        make_first: bool = False,
    ) -> None:
        from .resolver_helpers import merge_resolvers

        if not self.has(edge):
            self.d[edge] = []
        if ignore_if_subset:
            for r in list(self.get(edge)):
                if resolver.is_subset(r):
                    resolver = r
                    self.get(edge).remove(resolver)
                    break
        if merge:
            existing_resolvers = self.get(edge)
            new_resolvers: list["Resolver"] = []
            has_merged = False
            for existing_r in existing_resolvers:
                if has_merged is False and (
                    merged_r := merge_resolvers(resolver, existing_r)
                ):
                    new_resolvers.append(merged_r)
                    has_merged = True
                else:
                    new_resolvers.append(existing_r)
            self.d[edge] = new_resolvers
            if has_merged is True:
                return

        if make_first:
            self.d[edge].insert(0, resolver)
        else:
            self.d[edge].append(resolver)

    def has_subset(self, edge: str, resolver: "Resolver") -> bool:
        resolvers = self.get(edge)
        for r in resolvers:
            if resolver.is_subset(r, should_debug=True):
                return True
        return False

    def is_subset(self, other: "NestedResolvers") -> bool:
        # is this nested resolver a subset of the other
        for edge, resolvers in self.d.items():
            for r in resolvers:
                if not other.has_subset(edge, r):
                    return False
        return True

    def all_resolvers(self) -> list["Resolver"]:
        all_resolver_lst: list["Resolver"] = []
        for resolver_lst in self.d.values():
            all_resolver_lst.extend(resolver_lst)
        return all_resolver_lst

    def edge_to_str(self, edge: str) -> str:
        resolvers = self.get(edge)
        resolvers_str = []
        for i, r in enumerate(resolvers):
            if i == 0:
                resolvers_str.append(f"{edge}: {r.to_str()}")
            else:
                resolvers_str.append(
                    f"{edge}{SEPARATOR}{i} := (select .{edge} {r.to_str()})"
                )
        return ", ".join(resolvers_str)

    def to_str(self) -> str:
        return ", ".join([self.edge_to_str(e) for e in self.d.keys()])

    @staticmethod
    def edge_from_field_name(field_name: str) -> str:
        return field_name.split(SEPARATOR)[0]

    def resolver_from_field_name(self, field_name: str) -> T.Optional["Resolver"]:
        possible_edge = self.edge_from_field_name(field_name)
        resolvers = self.get(possible_edge)
        if not resolvers:
            return None
        if SEPARATOR not in field_name:
            return resolvers[0]
        try:
            index = int(field_name.split(SEPARATOR)[1])
            return resolvers[index]
        except (IndexError, ValueError) as e:
            print(f"{e=}, {field_name=}")
            return None
