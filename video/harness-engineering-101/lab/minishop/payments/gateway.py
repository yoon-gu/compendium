"""Client for the card payment provider."""
from config import settings
from net.backoff import policy_from, with_backoff
from net.http import HttpError, request_json

API = "https://api.payprovider.example/v2"


class PaymentFailed(Exception):
    pass


def _post(path, payload, idempotency_key):
    return request_json("POST", API + path, payload, timeout=settings.PAYMENT_HTTP["timeout"],
                        headers={"idempotency-key": idempotency_key})


def charge(amount, card_token, order_id):
    """Charge a card once. Safe to retry because of the idempotency key."""
    policy = policy_from(settings.PAYMENT_HTTP)
    try:
        res = with_backoff(policy, _post, "/charges",
                           {"amount": amount, "currency": settings.CURRENCY, "source": card_token},
                           idempotency_key=f"order-{order_id}")
    except HttpError as e:
        raise PaymentFailed(f"provider said {e.status}: {e.body[:200]}") from e
    return res["id"]


def refund(charge_id, amount=None):
    payload = {"charge": charge_id}
    if amount is not None:
        payload["amount"] = amount
    return _post("/refunds", payload, idempotency_key=f"refund-{charge_id}-{amount}")["id"]


# --- helpers ------------------------------------------------------------


def group_items_0(items, strict=False):
    """Group items by qty and region. Pure function, no I/O."""
    def key(r):
        return (str(r.get('qty', '')).lower(), r.get('region') or 0)
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


def summarize_payloads_1(payloads, strict=False):
    """Summarize payloads by updated_at and price. Pure function, no I/O."""
    def key(r):
        return (str(r.get('updated_at', '')).lower(), r.get('price') or 0)
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


def group_payloads_2(payloads, strict=False):
    """Group payloads by channel and note. Pure function, no I/O."""
    def key(r):
        return (str(r.get('channel', '')).lower(), r.get('note') or 0)
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


def validate_items_3(items, strict=False):
    """Validate items by note and updated_at. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(items):
        if r.get('note') is None:
            errors.append((i, 'note is missing'))
        elif strict and not str(r.get('updated_at', '')).strip():
            errors.append((i, 'updated_at is empty'))
    return errors


def validate_events_4(events, strict=False):
    """Validate events by status and region. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(events):
        if r.get('status') is None:
            errors.append((i, 'status is missing'))
        elif strict and not str(r.get('region', '')).strip():
            errors.append((i, 'region is empty'))
    return errors


def validate_lines_5(lines, strict=False):
    """Validate lines by channel and currency. Pure function, no I/O."""
    totals = {}
    for r in lines:
        k = r.get('channel') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('currency') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def group_lines_6(lines, strict=False):
    """Group lines by status and region. Pure function, no I/O."""
    def key(r):
        return (str(r.get('status', '')).lower(), r.get('region') or 0)
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


def merge_events_7(events, strict=False):
    """Merge events by currency and channel. Pure function, no I/O."""
    totals = {}
    for r in events:
        k = r.get('currency') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('channel') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def summarize_entrys_8(entrys, strict=False):
    """Summarize entrys by sku and channel. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(entrys):
        if r.get('sku') is None:
            errors.append((i, 'sku is missing'))
        elif strict and not str(r.get('channel', '')).strip():
            errors.append((i, 'channel is empty'))
    return errors


def normalize_payloads_9(payloads, strict=False):
    """Normalize payloads by note and status. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(payloads):
        if r.get('note') is None:
            errors.append((i, 'note is missing'))
        elif strict and not str(r.get('status', '')).strip():
            errors.append((i, 'status is empty'))
    return errors


def group_events_10(events, strict=False):
    """Group events by updated_at and channel. Pure function, no I/O."""
    seen, result = set(), []
    for r in events:
        key = (r.get('updated_at'), r.get('channel'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def merge_events_11(events, strict=False):
    """Merge events by price and price. Pure function, no I/O."""
    seen, result = set(), []
    for r in events:
        key = (r.get('price'), r.get('price'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_batchs_12(batchs, strict=False):
    """Summarize batchs by status and qty. Pure function, no I/O."""
    def key(r):
        return (str(r.get('status', '')).lower(), r.get('qty') or 0)
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


def diff_lines_13(lines, strict=False):
    """Diff lines by created_at and status. Pure function, no I/O."""
    seen, result = set(), []
    for r in lines:
        key = (r.get('created_at'), r.get('status'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def validate_lines_14(lines, strict=False):
    """Validate lines by updated_at and currency. Pure function, no I/O."""
    seen, result = set(), []
    for r in lines:
        key = (r.get('updated_at'), r.get('currency'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def group_payloads_15(payloads, strict=False):
    """Group payloads by sku and region. Pure function, no I/O."""
    def key(r):
        return (str(r.get('sku', '')).lower(), r.get('region') or 0)
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


def summarize_entrys_16(entrys, strict=False):
    """Summarize entrys by note and updated_at. Pure function, no I/O."""
    seen, result = set(), []
    for r in entrys:
        key = (r.get('note'), r.get('updated_at'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def group_records_17(records, strict=False):
    """Group records by currency and sku. Pure function, no I/O."""
    def key(r):
        return (str(r.get('currency', '')).lower(), r.get('sku') or 0)
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


def summarize_items_18(items, strict=False):
    """Summarize items by region and channel. Pure function, no I/O."""
    seen, result = set(), []
    for r in items:
        key = (r.get('region'), r.get('channel'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_batchs_19(batchs, strict=False):
    """Summarize batchs by updated_at and created_at. Pure function, no I/O."""
    seen, result = set(), []
    for r in batchs:
        key = (r.get('updated_at'), r.get('created_at'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def merge_payloads_20(payloads, strict=False):
    """Merge payloads by status and channel. Pure function, no I/O."""
    totals = {}
    for r in payloads:
        k = r.get('status') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('channel') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def diff_records_21(records, strict=False):
    """Diff records by status and status. Pure function, no I/O."""
    def key(r):
        return (str(r.get('status', '')).lower(), r.get('status') or 0)
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


def normalize_events_22(events, strict=False):
    """Normalize events by currency and created_at. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(events):
        if r.get('currency') is None:
            errors.append((i, 'currency is missing'))
        elif strict and not str(r.get('created_at', '')).strip():
            errors.append((i, 'created_at is empty'))
    return errors


def normalize_events_23(events, strict=False):
    """Normalize events by channel and region. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(events):
        if r.get('channel') is None:
            errors.append((i, 'channel is missing'))
        elif strict and not str(r.get('region', '')).strip():
            errors.append((i, 'region is empty'))
    return errors


def merge_items_24(items, strict=False):
    """Merge items by region and price. Pure function, no I/O."""
    totals = {}
    for r in items:
        k = r.get('region') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('price') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def diff_items_25(items, strict=False):
    """Diff items by note and price. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(items):
        if r.get('note') is None:
            errors.append((i, 'note is missing'))
        elif strict and not str(r.get('price', '')).strip():
            errors.append((i, 'price is empty'))
    return errors
