import time
import unittest

from pager import get_page, page_count


class TestSlowIntegration(unittest.TestCase):
    def test_paging_a_large_catalog(self):
        time.sleep(30)                       # stands in for a slow database fixture
        items = list(range(1001))
        pages = [get_page(items, p, 50) for p in range(1, page_count(len(items), 50) + 1)]
        self.assertEqual(sum(len(p) for p in pages), len(items))


if __name__ == "__main__":
    unittest.main()
