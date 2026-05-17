# Data Structures

PolePosition exposes a small runtime data-structure namespace:

```python
from polepos.data import LRUCache, SortedDict, Trie
```

This API is for application code that wants a few practical structures Python
does not provide as first-class built-in containers. It is intentionally small,
pure Python, and dependency-free.

## Import Boundary

`polepos.data` is a runtime package. It is separate from the internal
`pole_position` CLI implementation package.

Use it from generated applications like this:

```python
from polepos.data import IndexedPriorityQueue
```

Do not import from `pole_position.cli...` in generated app code. That package
is for the generator and command implementation.

## Available Structures

Current exports:

- `LRUCache`: bounded least-recently-used cache
- `TTLCache`: lazy-expiring in-memory cache
- `OrderedSet`: insertion-ordered set
- `SortedList`: sorted list with bisect helpers
- `SortedSet`: unique sorted values
- `SortedDict`: mapping that iterates keys in sorted order
- `IndexedPriorityQueue`: min-priority queue with update/remove by key
- `Trie`: prefix tree for string keys
- `UnionFind`: disjoint-set union
- `Graph`: adjacency-set graph with BFS, DFS, shortest path, and topological sort

## Examples

### LRU Cache

```python
from polepos.data import LRUCache

cache = LRUCache[str, dict](max_size=500)
cache["user:1"] = {"id": 1}
user = cache["user:1"]
```

### Indexed Priority Queue

```python
from polepos.data import IndexedPriorityQueue

jobs = IndexedPriorityQueue[str, int, dict]()
jobs.push("sync-users", priority=10, value={"kind": "sync"})
jobs.update("sync-users", priority=1)

next_job = jobs.pop()
```

### Trie

```python
from polepos.data import Trie

names = Trie[int]()
names.insert("customer", 1)
names.insert("customs", 2)

matches = names.keys("cust")
```

### Sorted Dict

```python
from polepos.data import SortedDict

scores = SortedDict[str, int]()
scores["alice"] = 10
scores["bob"] = 8

for name, score in scores.items():
    ...
```

## Runtime Caveat

These structures are in-memory and process-local. In a FastAPI app with
multiple Uvicorn workers, each worker has its own copy. Use them for local
indices, request-time algorithms, bounded caches, and test doubles.

For shared or persistent state, prefer infrastructure-backed structures:

- Redis sets, sorted sets, streams, and TTL keys
- PostgreSQL tables, indexes, materialized views, and full-text search
- Kafka or RabbitMQ for cross-process event streams

PolePosition may add higher-level module templates around these structures, but
the import surface remains explicit application code:

```python
from polepos.data import Graph
```
