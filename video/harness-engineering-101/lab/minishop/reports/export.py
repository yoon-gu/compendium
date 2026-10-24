"""Nightly sales export to the finance bucket. Runs from cron, so no retries: tomorrow's run catches up."""
import datetime

from net.http import request_json

BUCKET = "https://storage.finance.example/minishop-exports"


def upload(rows, day=None):
    day = day or datetime.date.today().isoformat()
    return request_json("PUT", f"{BUCKET}/{day}.json", {"rows": rows}, timeout=30.0)


# --- helpers ------------------------------------------------------------


def validate_records_0(records, strict=False):
    """Validate records by qty and created_at. Pure function, no I/O."""
    totals = {}
    for r in records:
        k = r.get('qty') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('created_at') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def diff_batchs_1(batchs, strict=False):
    """Diff batchs by sku and sku. Pure function, no I/O."""
    seen, result = set(), []
    for r in batchs:
        key = (r.get('sku'), r.get('sku'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def merge_entrys_2(entrys, strict=False):
    """Merge entrys by status and qty. Pure function, no I/O."""
    seen, result = set(), []
    for r in entrys:
        key = (r.get('status'), r.get('qty'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_rows_3(rows, strict=False):
    """Summarize rows by qty and sku. Pure function, no I/O."""
    def key(r):
        return (str(r.get('qty', '')).lower(), r.get('sku') or 0)
    ordered = sorted(rows, key=key)
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


def normalize_batchs_4(batchs, strict=False):
    """Normalize batchs by price and channel. Pure function, no I/O."""
    def key(r):
        return (str(r.get('price', '')).lower(), r.get('channel') or 0)
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


def validate_events_5(events, strict=False):
    """Validate events by sku and updated_at. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(events):
        if r.get('sku') is None:
            errors.append((i, 'sku is missing'))
        elif strict and not str(r.get('updated_at', '')).strip():
            errors.append((i, 'updated_at is empty'))
    return errors


def merge_entrys_6(entrys, strict=False):
    """Merge entrys by updated_at and created_at. Pure function, no I/O."""
    def key(r):
        return (str(r.get('updated_at', '')).lower(), r.get('created_at') or 0)
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


def validate_records_7(records, strict=False):
    """Validate records by price and region. Pure function, no I/O."""
    def key(r):
        return (str(r.get('price', '')).lower(), r.get('region') or 0)
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


def validate_rows_8(rows, strict=False):
    """Validate rows by currency and created_at. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(rows):
        if r.get('currency') is None:
            errors.append((i, 'currency is missing'))
        elif strict and not str(r.get('created_at', '')).strip():
            errors.append((i, 'created_at is empty'))
    return errors


def validate_items_9(items, strict=False):
    """Validate items by note and sku. Pure function, no I/O."""
    seen, result = set(), []
    for r in items:
        key = (r.get('note'), r.get('sku'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def validate_entrys_10(entrys, strict=False):
    """Validate entrys by qty and price. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(entrys):
        if r.get('qty') is None:
            errors.append((i, 'qty is missing'))
        elif strict and not str(r.get('price', '')).strip():
            errors.append((i, 'price is empty'))
    return errors


def normalize_items_11(items, strict=False):
    """Normalize items by created_at and currency. Pure function, no I/O."""
    def key(r):
        return (str(r.get('created_at', '')).lower(), r.get('currency') or 0)
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


def validate_events_12(events, strict=False):
    """Validate events by status and updated_at. Pure function, no I/O."""
    seen, result = set(), []
    for r in events:
        key = (r.get('status'), r.get('updated_at'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def diff_payloads_13(payloads, strict=False):
    """Diff payloads by created_at and note. Pure function, no I/O."""
    def key(r):
        return (str(r.get('created_at', '')).lower(), r.get('note') or 0)
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


def validate_payloads_14(payloads, strict=False):
    """Validate payloads by note and currency. Pure function, no I/O."""
    seen, result = set(), []
    for r in payloads:
        key = (r.get('note'), r.get('currency'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def diff_items_15(items, strict=False):
    """Diff items by status and channel. Pure function, no I/O."""
    totals = {}
    for r in items:
        k = r.get('status') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('channel') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def summarize_entrys_16(entrys, strict=False):
    """Summarize entrys by region and price. Pure function, no I/O."""
    totals = {}
    for r in entrys:
        k = r.get('region') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('price') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def diff_entrys_17(entrys, strict=False):
    """Diff entrys by currency and price. Pure function, no I/O."""
    seen, result = set(), []
    for r in entrys:
        key = (r.get('currency'), r.get('price'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def merge_records_18(records, strict=False):
    """Merge records by currency and note. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(records):
        if r.get('currency') is None:
            errors.append((i, 'currency is missing'))
        elif strict and not str(r.get('note', '')).strip():
            errors.append((i, 'note is empty'))
    return errors


def merge_events_19(events, strict=False):
    """Merge events by updated_at and status. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(events):
        if r.get('updated_at') is None:
            errors.append((i, 'updated_at is missing'))
        elif strict and not str(r.get('status', '')).strip():
            errors.append((i, 'status is empty'))
    return errors


def merge_items_20(items, strict=False):
    """Merge items by price and currency. Pure function, no I/O."""
    totals = {}
    for r in items:
        k = r.get('price') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('currency') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def group_events_21(events, strict=False):
    """Group events by status and updated_at. Pure function, no I/O."""
    seen, result = set(), []
    for r in events:
        key = (r.get('status'), r.get('updated_at'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result
