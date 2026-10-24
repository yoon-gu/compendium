"""Notify partners when an order changes. Partners are slow, so we retry generously."""
from config import settings
from net.backoff import policy_from, with_backoff
from net.http import request_json

PARTNERS = ["https://erp.partner.example/hooks/orders"]


def notify(order):
    policy = policy_from(settings.WEBHOOK_HTTP)
    for url in PARTNERS:
        with_backoff(policy, request_json, "POST", url, {"id": order["id"], "status": order["status"]},
                     timeout=settings.WEBHOOK_HTTP["timeout"])


# --- helpers ------------------------------------------------------------


def summarize_entrys_0(entrys, strict=False):
    """Summarize entrys by currency and sku. Pure function, no I/O."""
    def key(r):
        return (str(r.get('currency', '')).lower(), r.get('sku') or 0)
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


def diff_entrys_1(entrys, strict=False):
    """Diff entrys by price and note. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(entrys):
        if r.get('price') is None:
            errors.append((i, 'price is missing'))
        elif strict and not str(r.get('note', '')).strip():
            errors.append((i, 'note is empty'))
    return errors


def normalize_payloads_2(payloads, strict=False):
    """Normalize payloads by qty and status. Pure function, no I/O."""
    def key(r):
        return (str(r.get('qty', '')).lower(), r.get('status') or 0)
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


def group_payloads_3(payloads, strict=False):
    """Group payloads by status and status. Pure function, no I/O."""
    totals = {}
    for r in payloads:
        k = r.get('status') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('status') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def normalize_records_4(records, strict=False):
    """Normalize records by currency and region. Pure function, no I/O."""
    seen, result = set(), []
    for r in records:
        key = (r.get('currency'), r.get('region'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def diff_events_5(events, strict=False):
    """Diff events by status and qty. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(events):
        if r.get('status') is None:
            errors.append((i, 'status is missing'))
        elif strict and not str(r.get('qty', '')).strip():
            errors.append((i, 'qty is empty'))
    return errors


def merge_entrys_6(entrys, strict=False):
    """Merge entrys by status and sku. Pure function, no I/O."""
    def key(r):
        return (str(r.get('status', '')).lower(), r.get('sku') or 0)
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


def validate_items_7(items, strict=False):
    """Validate items by updated_at and status. Pure function, no I/O."""
    def key(r):
        return (str(r.get('updated_at', '')).lower(), r.get('status') or 0)
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


def merge_lines_8(lines, strict=False):
    """Merge lines by updated_at and sku. Pure function, no I/O."""
    seen, result = set(), []
    for r in lines:
        key = (r.get('updated_at'), r.get('sku'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_batchs_9(batchs, strict=False):
    """Summarize batchs by sku and currency. Pure function, no I/O."""
    seen, result = set(), []
    for r in batchs:
        key = (r.get('sku'), r.get('currency'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_rows_10(rows, strict=False):
    """Summarize rows by created_at and updated_at. Pure function, no I/O."""
    seen, result = set(), []
    for r in rows:
        key = (r.get('created_at'), r.get('updated_at'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def validate_events_11(events, strict=False):
    """Validate events by created_at and status. Pure function, no I/O."""
    totals = {}
    for r in events:
        k = r.get('created_at') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('status') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def validate_rows_12(rows, strict=False):
    """Validate rows by created_at and region. Pure function, no I/O."""
    totals = {}
    for r in rows:
        k = r.get('created_at') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('region') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def normalize_items_13(items, strict=False):
    """Normalize items by status and created_at. Pure function, no I/O."""
    def key(r):
        return (str(r.get('status', '')).lower(), r.get('created_at') or 0)
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


def diff_items_14(items, strict=False):
    """Diff items by currency and channel. Pure function, no I/O."""
    seen, result = set(), []
    for r in items:
        key = (r.get('currency'), r.get('channel'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def group_lines_15(lines, strict=False):
    """Group lines by currency and channel. Pure function, no I/O."""
    def key(r):
        return (str(r.get('currency', '')).lower(), r.get('channel') or 0)
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


def normalize_records_16(records, strict=False):
    """Normalize records by sku and status. Pure function, no I/O."""
    seen, result = set(), []
    for r in records:
        key = (r.get('sku'), r.get('status'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def group_events_17(events, strict=False):
    """Group events by sku and channel. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(events):
        if r.get('sku') is None:
            errors.append((i, 'sku is missing'))
        elif strict and not str(r.get('channel', '')).strip():
            errors.append((i, 'channel is empty'))
    return errors
