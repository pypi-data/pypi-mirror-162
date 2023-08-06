import typing as T
import time
from pydantic import BaseModel
from .unset import UNSET, UnsetType

if T.TYPE_CHECKING:
    from .resolver import Resolver


class CacheNode(BaseModel):
    val: T.Any
    resolver: T.Any  # circular unfortunately
    raw_d: dict
    timestamp: float


class Cache(BaseModel):
    d: dict[str, list[CacheNode]] = {}

    def get(self, edge: str) -> list[CacheNode]:
        return self.d.get(edge, [])

    def has(self, edge: str) -> bool:
        return edge in self.d

    def add(self, edge: str, resolver: "Resolver", val: T.Any, raw_d: dict) -> None:
        if not self.has(edge):
            self.d[edge] = []
        self.d[edge].append(
            CacheNode(resolver=resolver, val=val, raw_d=raw_d, timestamp=time.time())
        )

    def replace(self, edge: str, cache_nodes: list[CacheNode]) -> None:
        self.d[edge] = cache_nodes

    def clear(self, edge: str) -> None:
        if edge in self.d:
            del self.d[edge]

    def remove(self, edge: str, resolver: "Resolver") -> None:
        nodes = self.get(edge)
        new_nodes = []
        for node in list(nodes):
            if node.resolver is not resolver:
                new_nodes.append(node.resolver)
        self.d[edge] = new_nodes

    def val(
        self, edge: str, resolver: "Resolver", revert_to_first: bool = False
    ) -> T.Union[T.Any, UnsetType]:
        nodes = self.get(edge)
        if not nodes:
            return UNSET
        first_superset_node: T.Optional[CacheNode] = None
        for node in nodes:
            if node.resolver is resolver:
                return node.val
            if not first_superset_node:
                if resolver.is_subset(node.resolver, should_debug=True):
                    first_superset_node = node
        if first_superset_node:
            return first_superset_node.val
        if revert_to_first:
            return nodes[0].val
        return UNSET

    def is_empty(self) -> bool:
        return len(self.d) == 0
