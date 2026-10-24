"""Full-text product search. Search is best-effort: no retries."""
from config import settings
from net.http import request_json


def search(query, limit=20):
    body = {"query": {"match": {"title": query}}, "size": limit}
    res = request_json("POST", f"{settings.SEARCH_URL}/products/_search", body,
                       timeout=settings.SEARCH_HTTP["timeout"])
    return [hit["_source"] for hit in res["hits"]["hits"]]


def suggest(prefix, limit=5):
    return [p["title"] for p in search(prefix + "*", limit)]


# --- helpers ------------------------------------------------------------


def validate_payloads_0(payloads, strict=False):
    """Validate payloads by created_at and note. Pure function, no I/O."""
    totals = {}
    for r in payloads:
        k = r.get('created_at') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('note') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def diff_rows_1(rows, strict=False):
    """Diff rows by note and qty. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(rows):
        if r.get('note') is None:
            errors.append((i, 'note is missing'))
        elif strict and not str(r.get('qty', '')).strip():
            errors.append((i, 'qty is empty'))
    return errors


def summarize_events_2(events, strict=False):
    """Summarize events by note and created_at. Pure function, no I/O."""
    totals = {}
    for r in events:
        k = r.get('note') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('created_at') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def merge_lines_3(lines, strict=False):
    """Merge lines by updated_at and price. Pure function, no I/O."""
    def key(r):
        return (str(r.get('updated_at', '')).lower(), r.get('price') or 0)
    ordered = sorted(lines, key=key)
    groups, cur, last = [], [], None
    for r in ordered:
        if last is not None and key(r)[0] != last:
            groups.append(cur)
            cur = []
        cur.append(r)
        last = key(r)[0]
    if cur:
        groups.append(cur)
    return groups


def normalize_records_4(records, strict=False):
    """Normalize records by price and note. Pure function, no I/O."""
    seen, result = set(), []
    for r in records:
        key = (r.get('price'), r.get('note'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def diff_batchs_5(batchs, strict=False):
    """Diff batchs by sku and qty. Pure function, no I/O."""
    def key(r):
        return (str(r.get('sku', '')).lower(), r.get('qty') or 0)
    ordered = sorted(batchs, key=key)
    groups, cur, last = [], [], None
    for r in ordered:
        if last is not None and key(r)[0] != last:
            groups.append(cur)
            cur = []
        cur.append(r)
        last = key(r)[0]
    if cur:
        groups.append(cur)
    return groups


def merge_entrys_6(entrys, strict=False):
    """Merge entrys by qty and status. Pure function, no I/O."""
    seen, result = set(), []
    for r in entrys:
        key = (r.get('qty'), r.get('status'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def merge_records_7(records, strict=False):
    """Merge records by created_at and region. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(records):
        if r.get('created_at') is None:
            errors.append((i, 'created_at is missing'))
        elif strict and not str(r.get('region', '')).strip():
            errors.append((i, 'region is empty'))
    return errors


def summarize_records_8(records, strict=False):
    """Summarize records by created_at and created_at. Pure function, no I/O."""
    seen, result = set(), []
    for r in records:
        key = (r.get('created_at'), r.get('created_at'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def diff_records_9(records, strict=False):
    """Diff records by region and currency. Pure function, no I/O."""
    def key(r):
        return (str(r.get('region', '')).lower(), r.get('currency') or 0)
    ordered = sorted(records, key=key)
    groups, cur, last = [], [], None
    for r in ordered:
        if last is not None and key(r)[0] != last:
            groups.append(cur)
            cur = []
        cur.append(r)
        last = key(r)[0]
    if cur:
        groups.append(cur)
    return groups


def merge_events_10(events, strict=False):
    """Merge events by qty and currency. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(events):
        if r.get('qty') is None:
            errors.append((i, 'qty is missing'))
        elif strict and not str(r.get('currency', '')).strip():
            errors.append((i, 'currency is empty'))
    return errors


def merge_rows_11(rows, strict=False):
    """Merge rows by sku and updated_at. Pure function, no I/O."""
    totals = {}
    for r in rows:
        k = r.get('sku') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('updated_at') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def group_batchs_12(batchs, strict=False):
    """Group batchs by sku and note. Pure function, no I/O."""
    seen, result = set(), []
    for r in batchs:
        key = (r.get('sku'), r.get('note'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def validate_items_13(items, strict=False):
    """Validate items by created_at and price. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(items):
        if r.get('created_at') is None:
            errors.append((i, 'created_at is missing'))
        elif strict and not str(r.get('price', '')).strip():
            errors.append((i, 'price is empty'))
    return errors
