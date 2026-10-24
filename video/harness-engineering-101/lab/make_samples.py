#!/usr/bin/env python3
"""2편 실습 재료를 만든다. 몇 번을 돌려도 같은 결과(시드 고정).

    python3 make_samples.py          # sample-project2/ (+ logs/build.log, 약 2.3MB) 와 minishop/

- sample-project2/: 1편 pager(버그 그대로) + README 오타 둘 + 30초 걸리는 test_slow.py + 큰 빌드 로그(약 2.3MB, 하이쿠 입력 한도 1M 토큰을 넘는다).
  로그의 진짜 원인(ModuleNotFoundError)은 한가운데쯤에 묻어 둔다. 머리·꼬리만 남기면 보이지 않게.
- minishop/: 파일 열두 개짜리 작은 가게 코드. 결제 재시도 횟수·간격은 세 파일(설정·정책·호출부)을 이어 읽어야 나온다.
build.log 는 커서 커밋하지 않는다(.gitignore). 이 스크립트로 다시 만든다.
"""
import random
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.lstrip("\n"), encoding="utf-8")


# ------------------------------------------------------------ sample-project2
def sample_project2():
    root = HERE / "sample-project2"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir()
    for f in ("pager.py", "test_pager.py"):
        shutil.copy(HERE / "sample-project" / f, root / f)
    write(root / "README.md", """
# pager

Tiny pagination helper used in the hands-on lessons. Run `python3 -m unittest test_pager` for the fast tests
and `python3 -m unittest test_slow` for the slow integration test (it takes about thirty seconds).

The pacakge has no dependencies. Pages are numbered from one, and the last page may be shorter than the others.
If you change `page_count`, run both test files before you comitt.
""")
    write(root / "test_slow.py", """
import time
import unittest

from pager import get_page, page_count


class TestSlowIntegration(unittest.TestCase):
    def test_paging_a_large_catalog(self):
        time.sleep(30)                       # stands in for a slow database fixture
        items = list(range(1001))
        pages = [get_page(items, p, 50) for p in range(1, page_count(len(items), 50) + 1)]
        self.assertEqual(sum(len(p) for p in pages), len(items))


if __name__ == "__main__":
    unittest.main()
""")
    build_log(root / "logs" / "build.log")


def build_log(path, target_bytes=2_300_000):
    rng = random.Random(7)
    mods = [f"{a}_{b}" for a in ("core", "net", "ui", "store", "auth", "report", "sync", "cache", "search", "billing")
            for b in ("models", "views", "utils", "tasks", "api", "schema", "jobs", "hooks")]
    lines, size, t = [], 0, 9 * 3600 + 14 * 60
    t0 = t
    def stamp():
        nonlocal t
        t += rng.choice((0, 0, 0, 1))
        return f"2026-10-20 {t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"
    head = [f"[{stamp()}] [INFO] build #4182 started on runner ci-07 (python 3.12.4)",
            f"[{stamp()}] [INFO] step 1/4 'install': resolving 214 packages"]
    lines += head
    cause_at = target_bytes // 2
    caused = False
    step = 1
    while size < target_bytes:
        r = rng.random()
        m = rng.choice(mods)
        if r < 0.55:
            ln = f"[{stamp()}] [INFO] compiling {m}/{rng.choice(('__init__', 'base', 'main', 'helpers'))}.py ({rng.randint(40, 900)} lines)"
        elif r < 0.8:
            ln = f"[{stamp()}] [DEBUG] cache hit {m} key=sha256:{rng.getrandbits(64):016x}"
        elif r < 0.93:
            ln = f"[{stamp()}] [INFO] test {m}::test_{rng.choice(('create', 'update', 'delete', 'list', 'sync'))}_{rng.randint(1, 99)} PASSED ({rng.randint(1, 400)}ms)"
        else:
            ln = f"[{stamp()}] [WARN] {m}: DeprecationWarning: datetime.utcnow() is deprecated"
        if not caused and size > cause_at:                     # 진짜 원인: 한가운데
            step = 3
            lines += [f"[{stamp()}] [INFO] step 3/4 'package': collecting modules",
                      f"[{stamp()}] [ERROR] Traceback (most recent call last):",
                      '  File "build/steps/package.py", line 41, in <module>',
                      "    from pager_utils import chunk_pages",
                      "ModuleNotFoundError: No module named 'pager_utils'",
                      f"[{stamp()}] [INFO] step 3/4 'package': continuing with remaining targets (fail-late mode)"]
            caused = True
        lines.append(ln)
        size += len(ln) + 1
    lines += [f"[{stamp()}] [INFO] step 4/4 'publish': skipped because an earlier step failed",
              f"[{stamp()}] [ERROR] step 'package' failed (exit 1), see errors above",
              f"[{stamp()}] [INFO] BUILD FAILED in {(t - t0) // 3600}h {(t - t0) % 3600 // 60:02d}m {(t - t0) % 60:02d}s"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{path.relative_to(HERE)}: {path.stat().st_size:,} bytes, {len(lines):,} lines")


# ------------------------------------------------------------------ minishop
MINISHOP = {
    "README.md": """
# minishop

A small online shop backend used in the hands-on lessons. Modules:

- `catalog/` products and search
- `cart/` the shopping cart and pricing rules
- `orders/` order lifecycle
- `payments/` the payment gateway client
- `net/` shared HTTP helpers
- `config/` settings
""",
    "config/__init__.py": "",
    "config/settings.py": '''
"""Settings for every environment. Values here are read once at import."""

ENV = "production"
CURRENCY = "KRW"
TAX_RATE = 0.10
FREE_SHIPPING_OVER = 50_000
SHIPPING_FEE = 3_000

DB_URL = "postgresql://shop@db.internal/minishop"
SEARCH_URL = "http://search.internal:9200"

# Outbound calls. Each entry is turned into a RetryPolicy by net.backoff.policy_from().
CATALOG_HTTP = {"timeout": 2.0, "attempts": 2, "base_delay": 0.2}
SEARCH_HTTP = {"timeout": 1.5, "attempts": 1, "base_delay": 0.0}
PAYMENT_HTTP = {"timeout": 8.0, "attempts": 4, "base_delay": 0.5, "max_delay": 4.0}
WEBHOOK_HTTP = {"timeout": 5.0, "attempts": 6, "base_delay": 1.0, "max_delay": 30.0}
WAREHOUSE_HTTP = {"timeout": 3.0, "attempts": 3, "base_delay": 0.3}

FEATURE_FLAGS = {
    "new_checkout": True,
    "saved_carts": False,
    "gift_cards": True,
}
''',
    "net/__init__.py": "",
    "net/http.py": '''
"""Thin wrapper around urllib with JSON in and out."""
import json
import urllib.request


class HttpError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}")
        self.status = status
        self.body = body

    @property
    def retryable(self):
        return self.status in (408, 429) or self.status >= 500


def request_json(method, url, payload=None, timeout=5.0, headers=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"content-type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as e:
        raise HttpError(e.code, e.read().decode(errors="replace")) from e
''',
    "net/backoff.py": '''
"""Exponential backoff shared by every outbound client."""
import random
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3          # total tries, including the first one
    base_delay: float = 0.25   # seconds before the 2nd try; doubles each time
    max_delay: float = 10.0
    jitter: float = 0.1        # +/- 10% so clients don't retry in lockstep


def policy_from(cfg):
    """Build a policy from a settings dict such as settings.PAYMENT_HTTP."""
    return RetryPolicy(attempts=cfg.get("attempts", 3), base_delay=cfg.get("base_delay", 0.25),
                       max_delay=cfg.get("max_delay", 10.0))


def delays(policy):
    """Sleep lengths between tries: base, 2*base, 4*base ... capped at max_delay."""
    d = policy.base_delay
    for _ in range(policy.attempts - 1):
        yield min(d, policy.max_delay)
        d *= 2


def with_backoff(policy, fn, *args, retry_if=lambda e: getattr(e, "retryable", False), **kwargs):
    last = None
    waits = list(delays(policy)) + [None]
    for wait in waits:
        try:
            return fn(*args, **kwargs)
        except Exception as e:  # noqa: BLE001
            if not retry_if(e) or wait is None:
                raise
            last = e
            time.sleep(wait * random.uniform(1 - policy.jitter, 1 + policy.jitter))
    raise last
''',
    "catalog/__init__.py": "",
    "catalog/products.py": '''
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
''',
    "catalog/search.py": '''
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
''',
    "cart/__init__.py": "",
    "cart/cart.py": '''
"""The shopping cart. A cart is a dict of sku -> quantity."""
from catalog.products import in_stock, price_of


class Cart:
    def __init__(self):
        self.lines = {}

    def add(self, sku, qty=1):
        if not in_stock(sku, self.lines.get(sku, 0) + qty):
            raise ValueError(f"not enough stock for {sku}")
        self.lines[sku] = self.lines.get(sku, 0) + qty

    def remove(self, sku):
        self.lines.pop(sku, None)

    def subtotal(self):
        return sum(price_of(sku) * qty for sku, qty in self.lines.items())

    def is_empty(self):
        return not self.lines
''',
    "cart/pricing.py": '''
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
''',
    "orders/__init__.py": "",
    "orders/orders.py": '''
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
''',
    "orders/webhooks.py": '''
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
''',
    "payments/__init__.py": "",
    "payments/gateway.py": '''
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
''',
    "inventory/__init__.py": "",
    "inventory/warehouse.py": '''
"""Stock levels come from the warehouse system."""
from config import settings
from net.backoff import policy_from, with_backoff
from net.http import request_json

WAREHOUSE = "http://wms.internal/api"


def stock_levels(skus):
    policy = policy_from(settings.WAREHOUSE_HTTP)
    return with_backoff(policy, request_json, "POST", WAREHOUSE + "/stock/query", {"skus": list(skus)},
                        timeout=settings.WAREHOUSE_HTTP["timeout"])
''',
    "reports/__init__.py": "",
    "reports/export.py": '''
"""Nightly sales export to the finance bucket. Runs from cron, so no retries: tomorrow's run catches up."""
import datetime

from net.http import request_json

BUCKET = "https://storage.finance.example/minishop-exports"


def upload(rows, day=None):
    day = day or datetime.date.today().isoformat()
    return request_json("PUT", f"{BUCKET}/{day}.json", {"rows": rows}, timeout=30.0)
''',
    "tests/__init__.py": "",
    "tests/test_pricing.py": '''
import unittest

from cart.pricing import apply_coupon, shipping_for


class TestPricing(unittest.TestCase):
    def test_free_shipping(self):
        self.assertEqual(shipping_for(60_000), 0)

    def test_percent_coupon(self):
        self.assertEqual(apply_coupon(10_000, {"type": "percent", "value": 10}), 9_000)


if __name__ == "__main__":
    unittest.main()
''',
}


def changelog(path):
    """긴 변경 이력. 재시도 이야기가 여러 번 나오지만 다 옛날 값이라 코드를 읽어야 지금 값을 안다."""
    rng = random.Random(11)
    areas = ["catalog", "cart", "orders", "payments", "search", "webhooks", "config", "net"]
    verbs = ["Fix", "Add", "Refactor", "Speed up", "Document", "Rename", "Remove", "Harden"]
    things = ["cache expiry", "coupon rounding", "stock check", "currency formatting", "timeout handling",
              "logging", "idempotency keys", "error messages", "pagination", "settings loading"]
    out = ["# Changelog", ""]
    old_retry = {41: "payments: retry card charges up to 3 times (fixed 1s delay)",
                 77: "payments: raise charge retries to 5 after provider outage",
                 118: "net: move retry logic into a shared helper; payments now uses 6 attempts",
                 160: "payments: temporarily disable retries during provider migration"}
    for i in range(200, 0, -1):
        out.append(f"## 1.{i // 10}.{i % 10}")
        if i in old_retry:
            out.append(f"- {old_retry[i]}")
        for _ in range(rng.randint(2, 4)):
            out.append(f"- {rng.choice(areas)}: {rng.choice(verbs).lower()} {rng.choice(things)} "
                       f"(#{rng.randint(100, 2000)})")
        out.append("")
    write(path, "\n".join(out) + "\n")


PADDED = {"catalog/products.py": 24, "catalog/search.py": 14, "payments/gateway.py": 26, "orders/webhooks.py": 18,
          "inventory/warehouse.py": 22, "reports/export.py": 22, "orders/orders.py": 16, "cart/pricing.py": 12}


def helpers(rel, n):
    """실제 모듈처럼 보이는 도우미 함수들. 외부 호출은 하나도 없다(탐색할 분량만 늘린다)."""
    rng = random.Random(rel)
    nouns = ["record", "row", "item", "entry", "line", "event", "batch", "payload"]
    fields = ["sku", "qty", "price", "currency", "status", "created_at", "updated_at", "region", "channel", "note"]
    out = ["", "", "# --- helpers " + "-" * 60]
    for i in range(n):
        noun, a, b = rng.choice(nouns), rng.choice(fields), rng.choice(fields)
        kind = rng.randrange(4)
        name = f"{rng.choice(['normalize', 'validate', 'summarize', 'merge', 'diff', 'group'])}_{noun}s_{i}"
        out += ["", "", f"def {name}({noun}s, strict=False):",
                f'    """{name.split("_")[0].capitalize()} {noun}s by {a} and {b}. Pure function, no I/O."""']
        if kind == 0:
            out += [f"    seen, result = set(), []", f"    for r in {noun}s:", f"        key = (r.get('{a}'), r.get('{b}'))",
                    "        if key in seen:", "            if strict:", f"                raise ValueError(f'duplicate {{key}}')",
                    "            continue", "        seen.add(key)", "        result.append(dict(r))", "    return result"]
        elif kind == 1:
            out += ["    totals = {}", f"    for r in {noun}s:", f"        k = r.get('{a}') or 'unknown'",
                    f"        totals[k] = totals.get(k, 0) + (r.get('{b}') or 0)",
                    "    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))"]
        elif kind == 2:
            out += ["    errors = []", f"    for i, r in enumerate({noun}s):", f"        if r.get('{a}') is None:",
                    f"            errors.append((i, '{a} is missing'))", f"        elif strict and not str(r.get('{b}', '')).strip():",
                    f"            errors.append((i, '{b} is empty'))", "    return errors"]
        else:
            out += ["    def key(r):", f"        return (str(r.get('{a}', '')).lower(), r.get('{b}') or 0)",
                    f"    ordered = sorted({noun}s, key=key)", "    groups, cur, last = [], [], None",
                    "    for r in ordered:", f"        if last is not None and key(r)[0] != last:",
                    "            groups.append(cur)", "            cur = []", "        cur.append(r)", "        last = key(r)[0]",
                    "    if cur:", "        groups.append(cur)", "    return groups"]
    return "\n".join(out) + "\n"


def minishop():
    root = HERE / "minishop"
    if root.exists():
        shutil.rmtree(root)
    for rel, text in MINISHOP.items():
        write(root / rel, text + (helpers(rel, PADDED[rel]) if rel in PADDED else ""))
    changelog(root / "docs" / "CHANGELOG.md")
    n = sum(1 for p in root.rglob("*.py") if p.stat().st_size)
    print(f"minishop/: 파이썬 파일 {n}개(빈 __init__ 제외), {sum(p.stat().st_size for p in root.rglob('*') if p.is_file()):,} bytes")


if __name__ == "__main__":
    sample_project2()
    minishop()
