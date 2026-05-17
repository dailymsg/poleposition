from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar


T = TypeVar("T")


class Graph(Generic[T]):
    """A small adjacency-set graph."""

    def __init__(
        self,
        edges: Iterable[tuple[T, T]] = (),
        *,
        directed: bool = False,
    ) -> None:
        self.directed = directed
        self._adjacency: dict[T, set[T]] = {}
        for source, target in edges:
            self.add_edge(source, target)

    def __contains__(self, node: object) -> bool:
        return node in self._adjacency

    def __len__(self) -> int:
        return len(self._adjacency)

    def add_node(self, node: T) -> None:
        self._adjacency.setdefault(node, set())

    def add_edge(self, source: T, target: T) -> None:
        self.add_node(source)
        self.add_node(target)
        self._adjacency[source].add(target)
        if not self.directed:
            self._adjacency[target].add(source)

    def remove_edge(self, source: T, target: T) -> None:
        self._adjacency[source].remove(target)
        if not self.directed:
            self._adjacency[target].remove(source)

    def remove_node(self, node: T) -> None:
        del self._adjacency[node]
        for neighbors in self._adjacency.values():
            neighbors.discard(node)

    def nodes(self) -> set[T]:
        return set(self._adjacency)

    def edges(self) -> set[tuple[T, T]]:
        if self.directed:
            return {
                (source, target)
                for source, neighbors in self._adjacency.items()
                for target in neighbors
            }

        seen: set[frozenset[T]] = set()
        edges: set[tuple[T, T]] = set()
        for source, neighbors in self._adjacency.items():
            for target in neighbors:
                key = frozenset((source, target))
                if key in seen:
                    continue
                seen.add(key)
                edges.add((source, target))
        return edges

    def neighbors(self, node: T) -> set[T]:
        return set(self._adjacency[node])

    def bfs(self, start: T) -> Iterator[T]:
        seen = {start}
        queue: deque[T] = deque([start])
        while queue:
            node = queue.popleft()
            yield node
            for neighbor in self._adjacency[node]:
                if neighbor in seen:
                    continue
                seen.add(neighbor)
                queue.append(neighbor)

    def dfs(self, start: T) -> Iterator[T]:
        seen: set[T] = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            yield node
            stack.extend(reversed(tuple(self._adjacency[node])))

    def shortest_path(self, source: T, target: T) -> list[T]:
        parents: dict[T, T | None] = {source: None}
        queue: deque[T] = deque([source])
        while queue:
            node = queue.popleft()
            if node == target:
                return self._reconstruct_path(parents, target)
            for neighbor in self._adjacency[node]:
                if neighbor in parents:
                    continue
                parents[neighbor] = node
                queue.append(neighbor)
        raise ValueError("no path found")

    def topological_sort(self) -> list[T]:
        if not self.directed:
            raise ValueError("topological_sort requires a directed graph")

        indegree = {node: 0 for node in self._adjacency}
        for neighbors in self._adjacency.values():
            for neighbor in neighbors:
                indegree[neighbor] += 1

        ready = deque(node for node, degree in indegree.items() if degree == 0)
        ordered: list[T] = []
        while ready:
            node = ready.popleft()
            ordered.append(node)
            for neighbor in self._adjacency[node]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    ready.append(neighbor)

        if len(ordered) != len(indegree):
            raise ValueError("graph contains a cycle")
        return ordered

    def _reconstruct_path(self, parents: dict[T, T | None], target: T) -> list[T]:
        path = [target]
        current = target
        while parents[current] is not None:
            current = parents[current]  # type: ignore[assignment]
            path.append(current)
        path.reverse()
        return path
