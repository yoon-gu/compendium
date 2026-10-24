"""Tax, shipping and coupons."""
from config import settings


def shipping_for(subtotal):
    return 0 if subtotal >= settings.FREE_SHIPPING_OVER else settings.SHIPPING_FEE


def tax_for(amount):
    return round(amount * settings.TAX_RATE)


def apply_coupon(amount, coupon):
    if coupon is None:
        return amount
    if coupon["type"] == "percent":
        return round(amount * (100 - coupon["value"]) / 100)
    if coupon["type"] == "fixed":
        return max(0, amount - coupon["value"])
    raise ValueError(f"unknown coupon type {coupon['type']}")


def total(cart, coupon=None):
    sub = apply_coupon(cart.subtotal(), coupon)
    return sub + tax_for(sub) + shipping_for(sub)


# --- helpers ------------------------------------------------------------


def group_records_0(records, strict=False):
    """Group records by channel and status. Pure function, no I/O."""
    totals = {}
    for r in records:
        k = r.get('channel') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('status') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def validate_lines_1(lines, strict=False):
    """Validate lines by note and created_at. Pure function, no I/O."""
    seen, result = set(), []
    for r in lines:
        key = (r.get('note'), r.get('created_at'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def group_entrys_2(entrys, strict=False):
    """Group entrys by qty and sku. Pure function, no I/O."""
    seen, result = set(), []
    for r in entrys:
        key = (r.get('qty'), r.get('sku'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_lines_3(lines, strict=False):
    """Summarize lines by currency and created_at. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(lines):
        if r.get('currency') is None:
            errors.append((i, 'currency is missing'))
        elif strict and not str(r.get('created_at', '')).strip():
            errors.append((i, 'created_at is empty'))
    return errors


def group_rows_4(rows, strict=False):
    """Group rows by qty and price. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(rows):
        if r.get('qty') is None:
            errors.append((i, 'qty is missing'))
        elif strict and not str(r.get('price', '')).strip():
            errors.append((i, 'price is empty'))
    return errors


def diff_rows_5(rows, strict=False):
    """Diff rows by status and note. Pure function, no I/O."""
    seen, result = set(), []
    for r in rows:
        key = (r.get('status'), r.get('note'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def summarize_batchs_6(batchs, strict=False):
    """Summarize batchs by updated_at and channel. Pure function, no I/O."""
    totals = {}
    for r in batchs:
        k = r.get('updated_at') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('channel') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def group_payloads_7(payloads, strict=False):
    """Group payloads by region and currency. Pure function, no I/O."""
    def key(r):
        return (str(r.get('region', '')).lower(), r.get('currency') or 0)
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


def normalize_events_8(events, strict=False):
    """Normalize events by note and created_at. Pure function, no I/O."""
    seen, result = set(), []
    for r in events:
        key = (r.get('note'), r.get('created_at'))
        if key in seen:
            if strict:
                raise ValueError(f'duplicate {key}')
            continue
        seen.add(key)
        result.append(dict(r))
    return result


def merge_payloads_9(payloads, strict=False):
    """Merge payloads by sku and sku. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(payloads):
        if r.get('sku') is None:
            errors.append((i, 'sku is missing'))
        elif strict and not str(r.get('sku', '')).strip():
            errors.append((i, 'sku is empty'))
    return errors


def summarize_rows_10(rows, strict=False):
    """Summarize rows by region and updated_at. Pure function, no I/O."""
    errors = []
    for i, r in enumerate(rows):
        if r.get('region') is None:
            errors.append((i, 'region is missing'))
        elif strict and not str(r.get('updated_at', '')).strip():
            errors.append((i, 'updated_at is empty'))
    return errors


def validate_events_11(events, strict=False):
    """Validate events by created_at and created_at. Pure function, no I/O."""
    totals = {}
    for r in events:
        k = r.get('created_at') or 'unknown'
        totals[k] = totals.get(k, 0) + (r.get('created_at') or 0)
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))
