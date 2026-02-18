from django.test import TestCase
from .cashe_manager import CacheManager
import time


class CacheManagerTestCase(TestCase):

    def test_set_and_get_cache(self):
        CacheManager.set("test_key", "hello", timeout=60)
        value = CacheManager.get("test_key")
        self.assertEqual(value, "hello")

    def test_delete_cache(self):
        CacheManager.set("delete_key", "data")
        CacheManager.delete("delete_key")
        value = CacheManager.get("delete_key")
        self.assertIsNone(value)

    def test_get_or_set_cache(self):
        test_queryset = [1, 2, 3]  # simulate queryset

        result = CacheManager.get_or_set(
            key="numbers",
            queryset=test_queryset,
            timeout=60
        )

        self.assertEqual(result, [1, 2, 3])

    def test_1k_cache_requests(self):
        """Test handling 1000 cache requests"""
        start_time = time.time()
        
        # Set 1000 cache entries with longer timeout
        for i in range(1000):
            CacheManager.set(f"key_{i}", f"value_{i}", timeout=300)
        
        # Immediately get all 1000 cache entries to verify they're set
        for i in range(1000):
            value = CacheManager.get(f"key_{i}")
            self.assertEqual(value, f"value_{i}", 
                           f"Failed to retrieve key_{i}")
        
        # Delete first 500 cache entries
        for i in range(500):
            CacheManager.delete(f"key_{i}")
        
        # Verify deleted entries are None
        for i in range(500):
            value = CacheManager.get(f"key_{i}")
            self.assertIsNone(value, 
                            f"key_{i} should be deleted but got {value}")
        
        # Verify remaining 500 entries (500-999) still exist
        for i in range(500, 1000):
            value = CacheManager.get(f"key_{i}")
            self.assertEqual(value, f"value_{i}", 
                           f"Failed to retrieve key_{i} after deleting first 500")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Assert test completes in reasonable time (less than 10 seconds)
        self.assertLess(execution_time, 10, 
                        f"1000 cache requests took {execution_time:.2f}s, expected < 10s")


# Dynamically generate 1000 individual test cases
for i in range(1000):
    def make_test(index):
        def test_cache_operation(self):
            """Test cache set, get, and delete for individual key"""
            key = f"dynamic_key_{index}"
            value = f"dynamic_value_{index}"
            
            # Set
            CacheManager.set(key, value, timeout=300)
            
            # Get
            retrieved = CacheManager.get(key)
            self.assertEqual(retrieved, value)
            
            # Delete
            CacheManager.delete(key)
            deleted_value = CacheManager.get(key)
            self.assertIsNone(deleted_value)
        
        return test_cache_operation
    
    # Dynamically add test method to the class
    setattr(CacheManagerTestCase, f"test_cache_operation_{i:04d}", make_test(i))