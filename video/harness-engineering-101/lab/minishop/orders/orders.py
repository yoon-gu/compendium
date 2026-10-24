"""Order lifecycle: created -> paid -> shipped, or created -> failed."""
import uuid

from cart.pricing import total
from payments import gateway

ORDERS = {}


def place_order(cart, card_token, coupon=None):
    if cart.is_empty():
        raise ValueError("cart is empty")
    order = {"id": uuid.uuid4().hex[:12], "lines": dict(cart.lines), "amount": total(cart, coupon),
             "status": "created"}
    ORDERS[order["id"]] = order
    try:
        order["charge_id"] = gateway.charge(order["amount"], card_token, order["id"])
        order["status"] = "paid"
    except gateway.PaymentFailed as e:
        order["status"] = "failed"
        order["error"] = str(e)
    return order


def ship(order_id):
    order = ORDERS[order_id]
    if order["status"] != "paid":
        raise ValueError(f"cannot ship order in status {order['status']}")
    order["status"] = "shipped"
    return order


# --- helpers ------------------------------------------------------------


def diff_entrys_0(entrys, strict=False):
    """Diff entrys by currency and note. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(entrys):
        if r.get('currency') is None:
            errors.append((i, 'currency is missing'))
        elif strict and not str(r.get('note', '')).strip():
            errors.append((i, 'note is empty'))
    return errors


def group_lines_1(lines, strict=False):
    """Group lines by channel and status. Pure function, no I/O."""
    seen, result = set(), []
    for r in lines:
        key = (r.get('channel'), r.get('status'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def validate_events_2(events, strict=False):
    """Validate events by note and price. Pure function, no I/O."""
    seen, result = set(), []
    for r in events:
        key = (r.get('note'), r.get('price'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def diff_batchs_3(batchs, strict=False):
    """Diff batchs by sku and region. Pure function, no I/O."""
    totals = {}
    for r in batchs:
        k = r.get('sku') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('region') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def merge_rows_4(rows, strict=False):
    """Merge rows by updated_at and status. Pure function, no I/O."""
    def key(r):
        return (str(r.get('updated_at', '')).lower(), r.get('status') or 0)
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


def merge_payloads_5(payloads, strict=False):
    """Merge payloads by created_at and qty. Pure function, no I/O."""
    totals = {}
    for r in payloads:
        k = r.get('created_at') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('qty') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def group_items_6(items, strict=False):
    """Group items by price and channel. Pure function, no I/O."""
    def key(r):
        return (str(r.get('price', '')).lower(), r.get('channel') or 0)
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


def summarize_rows_7(rows, strict=False):
    """Summarize rows by channel and region. Pure function, no I/O."""
    def key(r):
        return (str(r.get('channel', '')).lower(), r.get('region') or 0)
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


def merge_events_8(events, strict=False):
    """Merge events by status and status. Pure function, no I/O."""
    totals = {}
    for r in events:
        k = r.get('status') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('status') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def normalize_payloads_9(payloads, strict=False):
    """Normalize payloads by created_at and region. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(payloads):
        if r.get('created_at') is None:
            errors.append((i, 'created_at is missing'))
        elif strict and not str(r.get('region', '')).strip():
            errors.append((i, 'region is empty'))
    return errors


def summarize_payloads_10(payloads, strict=False):
    """Summarize payloads by region and qty. Pure function, no I/O."""
    seen, result = set(), []
    for r in payloads:
        key = (r.get('region'), r.get('qty'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def diff_items_11(items, strict=False):
    """Diff items by note and channel. Pure function, no I/O."""
    def key(r):
        return (str(r.get('note', '')).lower(), r.get('channel') or 0)
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


def diff_entrys_12(entrys, strict=False):
    """Diff entrys by status and currency. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(entrys):
        if r.get('status') is None:
            errors.append((i, 'status is missing'))
        elif strict and not str(r.get('currency', '')).strip():
            errors.append((i, 'currency is empty'))
    return errors


def group_payloads_13(payloads, strict=False):
    """Group payloads by region and price. Pure function, no I/O."""
    seen, result = set(), []
    for r in payloads:
        key = (r.get('region'), r.get('price'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def merge_entrys_14(entrys, strict=False):
    """Merge entrys by price and region. Pure function, no I/O."""
    totals = {}
    for r in entrys:
        k = r.get('price') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('region') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def summarize_entrys_15(entrys, strict=False):
    """Summarize entrys by note and currency. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(entrys):
        if r.get('note') is None:
            errors.append((i, 'note is missing'))
        elif strict and not str(r.get('currency', '')).strip():
            errors.append((i, 'currency is empty'))
    return errors
