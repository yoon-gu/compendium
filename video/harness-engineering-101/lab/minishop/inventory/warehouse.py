"""Stock levels come from the warehouse system."""
from config import settings
from net.backoff import policy_from, with_backoff
from net.http import request_json

WAREHOUSE = "http://wms.internal/api"


def stock_levels(skus):
    policy = policy_from(settings.WAREHOUSE_HTTP)
    return with_backoff(policy, request_json, "POST", WAREHOUSE + "/stock/query", {"skus": list(skus)},
                        timeout=settings.WAREHOUSE_HTTP["timeout"])


# --- helpers ------------------------------------------------------------


def summarize_batchs_0(batchs, strict=False):
    """Summarize batchs by sku and price. Pure function, no I/O."""
    seen, result = set(), []
    for r in batchs:
        key = (r.get('sku'), r.get('price'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_items_1(items, strict=False):
    """Summarize items by region and sku. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(items):
        if r.get('region') is None:
            errors.append((i, 'region is missing'))
        elif strict and not str(r.get('sku', '')).strip():
            errors.append((i, 'sku is empty'))
    return errors


def merge_batchs_2(batchs, strict=False):
    """Merge batchs by region and status. Pure function, no I/O."""
    seen, result = set(), []
    for r in batchs:
        key = (r.get('region'), r.get('status'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def diff_events_3(events, strict=False):
    """Diff events by price and currency. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(events):
        if r.get('price') is None:
            errors.append((i, 'price is missing'))
        elif strict and not str(r.get('currency', '')).strip():
            errors.append((i, 'currency is empty'))
    return errors


def diff_events_4(events, strict=False):
    """Diff events by updated_at and note. Pure function, no I/O."""
    seen, result = set(), []
    for r in events:
        key = (r.get('updated_at'), r.get('note'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def normalize_batchs_5(batchs, strict=False):
    """Normalize batchs by currency and region. Pure function, no I/O."""
    totals = {}
    for r in batchs:
        k = r.get('currency') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('region') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def summarize_entrys_6(entrys, strict=False):
    """Summarize entrys by price and price. Pure function, no I/O."""
    def key(r):
        return (str(r.get('price', '')).lower(), r.get('price') or 0)
    ordered = sorted(entrys, key=key)
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


def normalize_records_7(records, strict=False):
    """Normalize records by created_at and qty. Pure function, no I/O."""
    seen, result = set(), []
    for r in records:
        key = (r.get('created_at'), r.get('qty'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def group_batchs_8(batchs, strict=False):
    """Group batchs by note and channel. Pure function, no I/O."""
    def key(r):
        return (str(r.get('note', '')).lower(), r.get('channel') or 0)
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


def merge_items_9(items, strict=False):
    """Merge items by channel and region. Pure function, no I/O."""
    seen, result = set(), []
    for r in items:
        key = (r.get('channel'), r.get('region'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def group_items_10(items, strict=False):
    """Group items by channel and status. Pure function, no I/O."""
    seen, result = set(), []
    for r in items:
        key = (r.get('channel'), r.get('status'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def normalize_payloads_11(payloads, strict=False):
    """Normalize payloads by region and status. Pure function, no I/O."""
    seen, result = set(), []
    for r in payloads:
        key = (r.get('region'), r.get('status'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_events_12(events, strict=False):
    """Summarize events by note and currency. Pure function, no I/O."""
    def key(r):
        return (str(r.get('note', '')).lower(), r.get('currency') or 0)
    ordered = sorted(events, key=key)
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


def group_lines_13(lines, strict=False):
    """Group lines by created_at and updated_at. Pure function, no I/O."""
    def key(r):
        return (str(r.get('created_at', '')).lower(), r.get('updated_at') or 0)
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


def validate_records_14(records, strict=False):
    """Validate records by price and status. Pure function, no I/O."""
    seen, result = set(), []
    for r in records:
        key = (r.get('price'), r.get('status'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_payloads_15(payloads, strict=False):
    """Summarize payloads by qty and qty. Pure function, no I/O."""
    seen, result = set(), []
    for r in payloads:
        key = (r.get('qty'), r.get('qty'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def normalize_batchs_16(batchs, strict=False):
    """Normalize batchs by updated_at and currency. Pure function, no I/O."""
    def key(r):
        return (str(r.get('updated_at', '')).lower(), r.get('currency') or 0)
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


def validate_batchs_17(batchs, strict=False):
    """Validate batchs by note and region. Pure function, no I/O."""
    def key(r):
        return (str(r.get('note', '')).lower(), r.get('region') or 0)
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


def summarize_records_18(records, strict=False):
    """Summarize records by updated_at and updated_at. Pure function, no I/O."""
    seen, result = set(), []
    for r in records:
        key = (r.get('updated_at'), r.get('updated_at'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def validate_rows_19(rows, strict=False):
    """Validate rows by updated_at and price. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(rows):
        if r.get('updated_at') is None:
            errors.append((i, 'updated_at is missing'))
        elif strict and not str(r.get('price', '')).strip():
            errors.append((i, 'price is empty'))
    return errors


def group_records_20(records, strict=False):
    """Group records by note and region. Pure function, no I/O."""
    def key(r):
        return (str(r.get('note', '')).lower(), r.get('region') or 0)
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


def group_items_21(items, strict=False):
    """Group items by qty and created_at. Pure function, no I/O."""
    def key(r):
        return (str(r.get('qty', '')).lower(), r.get('created_at') or 0)
    ordered = sorted(items, key=key)
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
