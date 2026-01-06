"""
Thread-safe LRU Cache Implementation

Design: HashMap + Doubly Linked List
Time Complexity: O(1) for both get() and put()
Space Complexity: O(capacity)
"""

import threading


class _Node:
    """
    Internal node class for doubly linked list.
    Each node stores a key-value pair and pointers to adjacent nodes.
    """
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Thread-safe LRU Cache using HashMap + Doubly Linked List.
    
    The cache maintains:
    - A dictionary (cache) for O(1) key lookups
    - A doubly linked list to track access order (most recent at head)
    - Dummy head and tail nodes to simplify edge case handling
    - A lock for thread-safety
    """
    
    def __init__(self, capacity: int):
        """
        Initialize the LRU cache.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # HashMap: key -> Node mapping for O(1) lookup
        
        # Dummy head and tail nodes eliminate edge cases
        # Head is most recently used, tail is least recently used
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        
        # Coarse-grained lock for thread-safety
        self.lock = threading.Lock()
    
    def _add_node(self, node: _Node) -> None:
        """
        Add a node right after the head (most recent position).
        This is O(1) because we always insert at a known position.
        """
        # Insert node between head and head.next
        node.prev = self.head
        node.next = self.head.next
        
        # Update adjacent nodes' pointers
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node: _Node) -> None:
        """
        Remove a node from the doubly linked list.
        This is O(1) because we have direct reference to the node.
        """
        prev_node = node.prev
        next_node = node.next
        
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node: _Node) -> None:
        """
        Move an existing node to the head (mark as most recently used).
        This is O(1): remove + add at head.
        """
        self._remove_node(node)
        self._add_node(node)
    
    def _pop_tail(self) -> _Node:
        """
        Remove and return the tail node (least recently used).
        This is O(1) because tail.prev is always the LRU node.
        """
        lru_node = self.tail.prev
        self._remove_node(lru_node)
        return lru_node
    
    def get(self, key: int) -> int:
        """
        Get the value for a key if it exists, otherwise return -1.
        Accessing a key marks it as most recently used.
        
        Time Complexity: O(1)
        """
        with self.lock:
            node = self.cache.get(key)
            
            if node is None:
                return -1
            
            # Move to head to mark as recently used
            self._move_to_head(node)
            return node.value
    
    def put(self, key: int, value: int) -> None:
        """
        Insert or update a key-value pair.
        If capacity is exceeded, evict the least recently used item.
        
        Time Complexity: O(1)
        """
        with self.lock:
            node = self.cache.get(key)
            
            if node is None:
                # New key: create new node
                new_node = _Node(key, value)
                
                if len(self.cache) >= self.capacity:
                    # Evict LRU item
                    tail = self._pop_tail()
                    del self.cache[tail.key]
                
                # Add new node to head and cache
                self._add_node(new_node)
                self.cache[key] = new_node
            else:
                # Existing key: update value and move to head
                node.value = value
                self._move_to_head(node)


# Test block demonstrating correctness
if __name__ == "__main__":
    print("=" * 60)
    print("LRU Cache Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    def assert_test(condition, test_name, error_msg=""):
        """Helper to run assertions and track results"""
        global tests_passed, tests_failed
        try:
            assert condition, error_msg
            print(f"[PASS] {test_name}")
            tests_passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test_name}")
            if error_msg:
                print(f"  Error: {error_msg}")
            tests_failed += 1
    
    # Test 1: Basic operations
    print("\n[Test 1] Basic get/put operations")
    try:
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        assert_test(cache.get(1) == 1, "get(1) returns 1")
        
        cache.put(3, 3)  # Evicts key 2
        assert_test(cache.get(2) == -1, "get(2) returns -1 (evicted)")
        assert_test(cache.get(3) == 3, "get(3) returns 3")
        
        cache.put(4, 4)  # Evicts key 1
        assert_test(cache.get(1) == -1, "get(1) returns -1 (evicted)")
        assert_test(cache.get(3) == 3, "get(3) still returns 3")
        assert_test(cache.get(4) == 4, "get(4) returns 4")
    except Exception as e:
        assert_test(False, "Test 1 execution", str(e))
    
    # Test 2: Update existing key
    print("\n[Test 2] Update existing key")
    try:
        cache2 = LRUCache(2)
        cache2.put(1, 1)
        cache2.put(2, 2)
        cache2.put(1, 10)  # Update key 1
        assert_test(cache2.get(1) == 10, "get(1) returns updated value 10")
        assert_test(cache2.get(2) == 2, "get(2) still returns 2")
    except Exception as e:
        assert_test(False, "Test 2 execution", str(e))
    
    # Test 3: Capacity 1
    print("\n[Test 3] Edge case: Capacity 1")
    try:
        cache3 = LRUCache(1)
        cache3.put(1, 1)
        cache3.put(2, 2)
        assert_test(cache3.get(1) == -1, "get(1) returns -1 (evicted)")
        assert_test(cache3.get(2) == 2, "get(2) returns 2")
    except Exception as e:
        assert_test(False, "Test 3 execution", str(e))
    
    # Test 4: Invalid capacity
    print("\n[Test 4] Invalid capacity handling")
    try:
        try:
            invalid_cache = LRUCache(0)
            assert_test(False, "LRUCache(0) raises ValueError", "Should raise ValueError for capacity <= 0")
        except ValueError:
            assert_test(True, "LRUCache(0) raises ValueError")
        
        try:
            invalid_cache = LRUCache(-1)
            assert_test(False, "LRUCache(-1) raises ValueError", "Should raise ValueError for capacity <= 0")
        except ValueError:
            assert_test(True, "LRUCache(-1) raises ValueError")
    except Exception as e:
        assert_test(False, "Test 4 execution", str(e))
    
    # Test 5: Multiple evictions
    print("\n[Test 5] Multiple evictions")
    try:
        cache5 = LRUCache(3)
        cache5.put(1, 1)
        cache5.put(2, 2)
        cache5.put(3, 3)
        cache5.get(1)  # Mark 1 as recently used
        cache5.put(4, 4)  # Should evict 2 (least recently used)
        assert_test(cache5.get(2) == -1, "get(2) returns -1 (evicted)")
        assert_test(cache5.get(1) == 1, "get(1) still returns 1")
        assert_test(cache5.get(3) == 3, "get(3) still returns 3")
        assert_test(cache5.get(4) == 4, "get(4) returns 4")
    except Exception as e:
        assert_test(False, "Test 5 execution", str(e))
    
    # Test 6: Thread safety (concurrent access)
    print("\n[Test 6] Thread safety with concurrent access")
    try:
        cache6 = LRUCache(100)
        results = []
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(50):
                    key = thread_id * 1000 + i
                    cache6.put(key, i)
                    val = cache6.get(key)
                    results.append(val == i)
            except Exception as e:
                errors.append(str(e))
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert_test(len(errors) == 0, "No exceptions in threads", f"Errors: {errors}" if errors else "")
        assert_test(all(results), f"All {len(results)} concurrent operations successful", 
                   f"Failed operations: {results.count(False)}")
    except Exception as e:
        assert_test(False, "Test 6 execution", str(e))
    
    # Test 7: Access order maintenance
    print("\n[Test 7] LRU eviction order correctness")
    try:
        cache7 = LRUCache(3)
        cache7.put(1, 1)
        cache7.put(2, 2)
        cache7.put(3, 3)
        # Access pattern: 1, 3, 2 (1 is most recent, 2 is least recent)
        cache7.get(1)
        cache7.get(3)
        cache7.get(2)
        # Now 2 is most recent, 1 is least recent
        cache7.put(4, 4)  # Should evict 1
        assert_test(cache7.get(1) == -1, "get(1) returns -1 (correctly evicted)")
        assert_test(cache7.get(2) == 2, "get(2) still returns 2")
        assert_test(cache7.get(3) == 3, "get(3) still returns 3")
        assert_test(cache7.get(4) == 4, "get(4) returns 4")
    except Exception as e:
        assert_test(False, "Test 7 execution", str(e))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {tests_passed + tests_failed}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    
    if tests_failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
        exit(0)
    else:
        print(f"\n[ERROR] {tests_failed} TEST(S) FAILED")
        print("=" * 60)
        exit(1)

