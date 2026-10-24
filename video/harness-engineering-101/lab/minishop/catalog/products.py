"""Product lookups. Products are cached for a minute."""
import time

from config import settings
from net.backoff import policy_from, with_backoff
from net.http import request_json

_CACHE = {}
_TTL = 60


def get_product(sku):
    hit = _CACHE.get(sku)
    if hit and time.time() - hit[0] < _TTL:
        return hit[1]
    policy = policy_from(settings.CATALOG_HTTP)
    data = with_backoff(policy, request_json, "GET", f"http://catalog.internal/products/{sku}",
                        timeout=settings.CATALOG_HTTP["timeout"])
    _CACHE[sku] = (time.time(), data)
    return data


def price_of(sku):
    return get_product(sku)["price"]


def in_stock(sku, qty=1):
    return get_product(sku).get("stock", 0) >= qty


# --- helpers ------------------------------------------------------------


def merge_batchs_0(batchs, strict=False):
    """Merge batchs by status and sku. Pure function, no I/O."""
    totals = {}
    for r in batchs:
        k = r.get('status') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('sku') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def diff_batchs_1(batchs, strict=False):
    """Diff batchs by channel and price. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(batchs):
        if r.get('channel') is None:
            errors.append((i, 'channel is missing'))
        elif strict and not str(r.get('price', '')).strip():
            errors.append((i, 'price is empty'))
    return errors


def diff_lines_2(lines, strict=False):
    """Diff lines by channel and currency. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(lines):
        if r.get('channel') is None:
            errors.append((i, 'channel is missing'))
        elif strict and not str(r.get('currency', '')).strip():
            errors.append((i, 'currency is empty'))
    return errors


def diff_items_3(items, strict=False):
    """Diff items by status and qty. Pure function, no I/O."""
    seen, result = set(), []
    for r in items:
        key = (r.get('status'), r.get('qty'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def group_events_4(events, strict=False):
    """Group events by channel and note. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(events):
        if r.get('channel') is None:
            errors.append((i, 'channel is missing'))
        elif strict and not str(r.get('note', '')).strip():
            errors.append((i, 'note is empty'))
    return errors


def validate_payloads_5(payloads, strict=False):
    """Validate payloads by created_at and currency. Pure function, no I/O."""
    seen, result = set(), []
    for r in payloads:
        key = (r.get('created_at'), r.get('currency'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def normalize_payloads_6(payloads, strict=False):
    """Normalize payloads by region and region. Pure function, no I/O."""
    seen, result = set(), []
    for r in payloads:
        key = (r.get('region'), r.get('region'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def normalize_rows_7(rows, strict=False):
    """Normalize rows by sku and qty. Pure function, no I/O."""
    totals = {}
    for r in rows:
        k = r.get('sku') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('qty') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def validate_payloads_8(payloads, strict=False):
    """Validate payloads by price and channel. Pure function, no I/O."""
    seen, result = set(), []
    for r in payloads:
        key = (r.get('price'), r.get('channel'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def validate_entrys_9(entrys, strict=False):
    """Validate entrys by qty and channel. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(entrys):
        if r.get('qty') is None:
            errors.append((i, 'qty is missing'))
        elif strict and not str(r.get('channel', '')).strip():
            errors.append((i, 'channel is empty'))
    return errors


def group_lines_10(lines, strict=False):
    """Group lines by updated_at and created_at. Pure function, no I/O."""
    totals = {}
    for r in lines:
        k = r.get('updated_at') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('created_at') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def group_lines_11(lines, strict=False):
    """Group lines by currency and status. Pure function, no I/O."""
    totals = {}
    for r in lines:
        k = r.get('currency') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('status') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def normalize_lines_12(lines, strict=False):
    """Normalize lines by currency and created_at. Pure function, no I/O."""
    def key(r):
        return (str(r.get('currency', '')).lower(), r.get('created_at') or 0)
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


def normalize_payloads_13(payloads, strict=False):
    """Normalize payloads by price and sku. Pure function, no I/O."""
    def key(r):
        return (str(r.get('price', '')).lower(), r.get('sku') or 0)
    ordered = sorted(payloads, key=key)
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


def normalize_entrys_14(entrys, strict=False):
    """Normalize entrys by sku and region. Pure function, no I/O."""
    totals = {}
    for r in entrys:
        k = r.get('sku') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('region') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def normalize_lines_15(lines, strict=False):
    """Normalize lines by status and currency. Pure function, no I/O."""
    totals = {}
    for r in lines:
        k = r.get('status') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('currency') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def validate_items_16(items, strict=False):
    """Validate items by price and price. Pure function, no I/O."""
    totals = {}
    for r in items:
        k = r.get('price') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('price') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def summarize_entrys_17(entrys, strict=False):
    """Summarize entrys by region and created_at. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(entrys):
        if r.get('region') is None:
            errors.append((i, 'region is missing'))
        elif strict and not str(r.get('created_at', '')).strip():
            errors.append((i, 'created_at is empty'))
    return errors


def normalize_items_18(items, strict=False):
    """Normalize items by region and status. Pure function, no I/O."""
    seen, result = set(), []
    for r in items:
        key = (r.get('region'), r.get('status'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_lines_19(lines, strict=False):
    """Summarize lines by note and status. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(lines):
        if r.get('note') is None:
            errors.append((i, 'note is missing'))
        elif strict and not str(r.get('status', '')).strip():
            errors.append((i, 'status is empty'))
    return errors


def summarize_payloads_20(payloads, strict=False):
    """Summarize payloads by region and status. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(payloads):
        if r.get('region') is None:
            errors.append((i, 'region is missing'))
        elif strict and not str(r.get('status', '')).strip():
            errors.append((i, 'status is empty'))
    return errors


def merge_entrys_21(entrys, strict=False):
    """Merge entrys by created_at and status. Pure function, no I/O."""
    def key(r):
        return (str(r.get('created_at', '')).lower(), r.get('status') or 0)
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


def merge_payloads_22(payloads, strict=False):
    """Merge payloads by channel and price. Pure function, no I/O."""
    totals = {}
    for r in payloads:
        k = r.get('channel') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('price') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def validate_records_23(records, strict=False):
    """Validate records by region and region. Pure function, no I/O."""
    def key(r):
        return (str(r.get('region', '')).lower(), r.get('region') or 0)
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
