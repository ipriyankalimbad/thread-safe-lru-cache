# Thread-Safe LRU Cache Implementation

A clean, interview-grade implementation of a Least Recently Used (LRU) Cache in Python, designed to meet Microsoft-level engineering standards.

## Design Rationale

### Data Structure Choice: HashMap + Doubly Linked List

The implementation uses a combination of:
- **HashMap (Python dict)**: Provides O(1) key lookup to find nodes
- **Doubly Linked List**: Maintains access order and enables O(1) insertion/deletion

This hybrid approach achieves O(1) time complexity for both `get()` and `put()` operations, which is optimal for an LRU cache.

### Why Not OrderedDict?

While Python's `OrderedDict` could simplify the implementation, this custom approach:
- Demonstrates understanding of fundamental data structures
- Provides explicit control over the eviction mechanism
- Shows ability to design efficient algorithms from first principles
- Is more interview-friendly (explains the "how" and "why")

### Dummy Head and Tail Nodes

Using sentinel nodes (`head` and `tail`) eliminates edge cases:
- No null pointer checks when inserting at the beginning
- No special cases when removing the last node
- Cleaner, more maintainable code
- Consistent O(1) operations regardless of list size

### Thread Safety: Coarse-Grained Locking

A single `threading.Lock()` protects all cache operations:
- **Pros**: Simple, correct, easy to reason about
- **Cons**: Limits parallelism (only one operation at a time)

This is a pragmatic choice for an interview implementation:
- Guarantees correctness
- Easy to explain and defend
- Sufficient for most use cases
- Can be optimized later if needed (fine-grained locking, lock-free structures)

## Time Complexity

| Operation | Time Complexity | Explanation |
|-----------|----------------|-------------|
| `get(key)` | O(1) | HashMap lookup O(1) + node movement O(1) |
| `put(key, value)` | O(1) | HashMap lookup O(1) + node insertion/update O(1) + eviction O(1) |

All operations are O(1) because:
- Dictionary lookups are average-case O(1)
- Doubly linked list operations (add, remove, move) are O(1) with direct node references
- Eviction removes tail node in O(1) time

## Space Complexity

**O(capacity)**: The cache stores at most `capacity` key-value pairs. Each entry requires:
- One dictionary entry (key → node reference)
- One node in the doubly linked list (key, value, two pointers)
- Two dummy nodes (head and tail) - constant overhead

## Thread Safety Approach

The implementation uses **coarse-grained locking**:
- A single `threading.Lock()` wraps all cache operations
- `get()` and `put()` both acquire the lock using `with self.lock:`
- Ensures atomicity: no interleaving of operations

**Example of thread-safe behavior:**
```python
# Thread 1: cache.put(1, 100)
# Thread 2: cache.get(1)
# Result: Either Thread 1 completes entirely before Thread 2, or vice versa
# No race conditions or inconsistent state
```

## Trade-offs and Possible Improvements

### Current Trade-offs

1. **Coarse-grained lock**: Limits parallelism but ensures correctness
2. **No expiration**: Items remain until evicted (no TTL)
3. **Fixed capacity**: Cannot dynamically resize
4. **Synchronous only**: No async support

### Possible Improvements (for production)

1. **Fine-grained locking**: 
   - Separate locks for read/write operations
   - Read-write locks for better concurrency
   - Trade-off: Increased complexity and potential deadlocks

2. **Lock-free structures**:
   - Atomic operations and compare-and-swap
   - Trade-off: Complex implementation, platform-dependent

3. **Time-to-live (TTL)**:
   - Add expiration timestamps to nodes
   - Background thread to evict expired items
   - Trade-off: Additional memory and complexity

4. **Dynamic capacity**:
   - Allow resizing based on memory pressure
   - Trade-off: More complex eviction logic

5. **Metrics and monitoring**:
   - Hit/miss ratio tracking
   - Access pattern analytics
   - Trade-off: Performance overhead

## Usage Example

```python
from lru_cache import LRUCache

# Create cache with capacity 3
cache = LRUCache(3)

# Add items
cache.put(1, "apple")
cache.put(2, "banana")
cache.put(3, "cherry")

# Access item (marks as recently used)
print(cache.get(2))  # Output: "banana"

# Add new item (evicts least recently used: key 1)
cache.put(4, "date")

# Key 1 is now evicted
print(cache.get(1))  # Output: -1
print(cache.get(4))  # Output: "date"
```

## Testing

Run the test block included in `lru_cache.py`:

```bash
python lru_cache.py
```

The test suite covers:
- Basic get/put operations
- Eviction behavior
- Update existing keys
- Edge cases (capacity = 1)
- Thread safety with concurrent access

## Interview Talking Points

1. **Why HashMap + DLL?** Combines fast lookup with ordered structure
2. **Why dummy nodes?** Simplifies edge cases and reduces bugs
3. **Why coarse-grained lock?** Correctness first, optimize later
4. **O(1) guarantee?** All operations use direct references, no iteration
5. **Alternative designs?** OrderedDict (simpler but less educational), arrays (O(n) operations)

This implementation demonstrates:
- Strong understanding of data structures
- Ability to balance correctness and performance
- Clear code organization and encapsulation
- Thoughtful design decisions with trade-off awareness

