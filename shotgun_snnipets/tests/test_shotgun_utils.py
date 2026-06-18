import time
import unittest

from shotgun_utils import (
    _instantiate_shogrid,
    async_find,
)


class TestAsyncFind(unittest.TestCase):
    def test_async_find(self):
        sg = _instantiate_shogrid()
        fields = list(sg.schema_field_read("Task").keys())

        start = time.perf_counter()
        normal = sg.find("Task", [], fields)
        normal_time = time.perf_counter() - start

        start = time.perf_counter()
        async_result = async_find(
            "Task",
            fields=fields,
        )
        async_time = time.perf_counter() - start

        self.assertEqual(len(normal), len(async_result))

        print(f"\nNormal find : {normal_time:.2f}s")
        print(f"Async find  : {async_time:.2f}s")
        print(f"Speedup     : {normal_time / async_time:.2f}x")


if __name__ == "__main__":
    unittest.main()
