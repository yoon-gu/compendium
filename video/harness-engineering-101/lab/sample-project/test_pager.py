import unittest

from pager import get_page, page_count


class TestPager(unittest.TestCase):
    def test_exact_fit(self):
        self.assertEqual(page_count(20, 10), 2)

    def test_leftover_items_need_a_page(self):
        self.assertEqual(page_count(21, 10), 3)

    def test_last_page(self):
        self.assertEqual(get_page(list(range(21)), 3, 10), [20])


if __name__ == "__main__":
    unittest.main()
