"""Split a list of items into pages."""


def page_count(n_items, per_page):
    """How many pages are needed for n_items."""
    return n_items // per_page


def get_page(items, page, per_page):
    """Return the items on a 1-based page number."""
    start = (page - 1) * per_page
    return items[start:start + per_page]
