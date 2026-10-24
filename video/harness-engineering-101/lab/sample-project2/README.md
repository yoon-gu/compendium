# pager

Tiny pagination helper used in the hands-on lessons. Run `python3 -m unittest test_pager` for the fast tests
and `python3 -m unittest test_slow` for the slow integration test (it takes about thirty seconds).

The pacakge has no dependencies. Pages are numbered from one, and the last page may be shorter than the others.
If you change `page_count`, run both test files before you comitt.
