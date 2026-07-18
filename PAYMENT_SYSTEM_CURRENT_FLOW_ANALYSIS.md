# HairLync Payment System — Current Flow Analysis

**Audit type:** Read-only technical audit
**Scope:** Full repository (`/home/fahad-mindmatrix/Desktop/Fahad/JUNE WORK/HairLync`)
**Restriction:** No code, migrations, dependencies, environment variables, or tests were modified during this audit. Nothing was committed or pushed.

Labels used throughout: ✅ VERIFIED · ⚠️ PROBLEM / GAP · 🔐 SECURITY RISK · ℹ️ CURRENT BEHAVIOR · 💡 FUTURE RECOMMENDATION · ❓ OPEN DECISION

---

## 1. Executive summary

✅ VERIFIED: The HairLync repository contains **no Apple App Store / StoreKit integration, no Google Play Billing integration, and no Stripe integration anywhere** — not in the backend, the admin dashboard, or the landing page. There is also **no mobile application source code in this repository**.

The entire "payment system" that exists today is a single Django app, `Apps.subscriptions`, implementing a **manual, self-service subscription record with no real payment processor behind it**. A barber user calls one API endpoint, supplies a free-text `payment_reference`/`payment_method`, and the subscription is **auto-activated immediately server-side** — there is no charge, no receipt, no token, and no verification of any kind. The code itself acknowledges this directly:

- `Apps/subscriptions/models.py:81` — comment: `# Payment tracking (integration-ready)`
- `Apps/subscriptions/views.py:45` — swagger docstring: `"Subscribe to a plan. Payment integration ready."`
- `Apps/subscriptions/views.py:76` — comment: `# Auto-activate (in production, this would happen after payment confirmation)`

This is a **deliberate stub**, not a broken integration — there is nothing to "fix" because Apple, Google, and Stripe processing were never built. This materially changes the nature of the upcoming Stripe work: it is not "add a third payment channel alongside two working ones," it is "build the first real payment channel," while preserving the existing manual-activation contract that mobile/admin clients currently rely on.

The user-facing entitlement model (`CustomUserModel.paid_user` / `current_plan` / `current_period_start` / `current_period_end`, and `is_subscribed()`) is reasonably well-factored and platform-agnostic — it does **not** hard-code Apple or Google concepts, which is a genuine strength for a future multi-channel (Apple + Google + Stripe) design.

---

## 2. Scope and restrictions

Per the task brief: no files were edited, created, or deleted; no migrations were generated or applied; no dependencies were installed/removed; no env vars, deployment config, or API contracts were changed; nothing was committed or pushed. The only executable actions taken were read-only `grep`/`find` searches and a single **safe** run of the existing Django test suite for the subscriptions-adjacent tests, which uses Django's ephemeral in-memory SQLite test database (created and destroyed automatically, no effect on any persisted file) — see §18.

---

## 3. Files inspected

### Backend (Django — `services/backend/`)

| File | Responsibility | Status |
|---|---|---|
| `Apps/subscriptions/models.py` | `SubscriptionPlan` + `Subscription` models; `activate()`/`cancel()`/`expire()` state transitions | ✅ Active, but stub payment logic |
| `Apps/subscriptions/views.py` | 5 REST endpoints: list plans, admin-create plan, subscribe, get/cancel current subscription, history | ✅ Active |
| `Apps/subscriptions/serializers.py` | `SubscriptionPlanSerializer`, `SubscriptionSerializer`, `SubscriptionCreateSerializer` | ✅ Active |
| `Apps/subscriptions/urls.py` | Routes under `api/v1/subscriptions/` | ✅ Active |
| `Apps/subscriptions/admin.py` | Django admin registration for both models | ✅ Active |
| `Apps/subscriptions/migrations/0001_initial.py`, `0002_initial.py` | Schema creation | ✅ Active |
| `Apps/subscriptions/apps.py`, `__init__.py` | App boilerplate | ✅ Active |
| `Apps/users/models.py` | `CustomUserModel` — holds `paid_user`, `current_plan`, `current_period_start/end`, `is_subscribed()`, `get_subscription_period()` | ✅ Active — this is the entitlement source of truth for API/permission checks |
| `Apps/users/permissions.py` | `IsSubscribedBarber` permission class (subscription-gated access) | ⚠️ Defined but **never applied** to any view (dead code) |
| `Apps/users/serializers.py` | Exposes `paid_user`, `current_plan`, `is_subscribed` on user payloads | ✅ Active |
| `Apps/users/admin.py` | Displays/filters users by `paid_user`, `current_plan` | ✅ Active |
| `Apps/users/tests.py` | `UserModelTests.test_subscription_check` | ✅ Active |
| `Apps/education/views.py` | Only app that actually **enforces** `is_subscribed()` — gates premium educational content | ✅ Active |
| `Apps/bookings/tests.py` | Contains `SubscriptionTests` (subscribe + cancel API tests) | ✅ Active |
| `Apps/services/views.py`, `Apps/profiles/views.py`, `Apps/recommendations/views.py` | Import `IsSubscribedBarber` but never use it | ⚠️ Dead/unused import |
| `core/settings.py` | `Apps.subscriptions` registered in `INSTALLED_APPS`; JWT auth config; no payment-related settings | ✅ Active |
| `core/urls.py` | Mounts `api/v1/subscriptions/` | ✅ Active |
| `pyproject.toml` | Dependency manifest — **no payment SDK of any kind** | ✅ Verified absence |
| `.env.example` (backend) | Only email/SMTP vars — no payment vars | ✅ Verified absence |

No `Apps/payments`, `Apps/billing`, `Apps/webhooks`, or similar app exists. No signals, Celery tasks, or management commands related to subscriptions exist anywhere in the backend (confirmed by repo-wide search — see §11–§12).

### Mobile application

❓ **Not present in this repository.** An exhaustive repo-wide search for Apple/StoreKit/Google Play/IAP terms found no mobile project directory, no `ios/`, `android/`, React Native, or Flutter code. This audit **cannot verify** any mobile-side purchase flow, because no mobile source exists here. Any statement about "how the mobile app initiates a purchase" is therefore an **open/unverifiable item**, not a documented fact — flagged throughout as ❓.

### Landing page (`services/landing/` — Vite + React 19)

| File | Responsibility | Status |
|---|---|---|
| `src/App.jsx` | Composes the single-page marketing site (Hero, Features, Unlock, Plans, Mission, Testimonial, Freetrial, Footer) | ✅ Active |
| `src/components/Plans.jsx` | **Static, hard-coded** 4-tier pricing UI ($0 / $25 / $75 / $18-yearly) with buttons that have **no `onClick` handlers** | ⚠️ Display-only, not wired to backend |
| `src/components/Freetrial.jsx` | "Start your free scan" CTA button, no handler | ⚠️ Display-only |
| `src/components/Banner.jsx`, `Hero.jsx`, `Mission.jsx`, `Mission2.jsx` | Contain Apple App Store / Google Play **badge images** (marketing download links), unrelated to in-app payments | ℹ️ Not payment code |
| `src/assets/images.jsx` | Imports the Google Play / App Store badge SVGs | ℹ️ Not payment code |
| `package.json` | Dependencies: React, framer-motion, tailwind, lucide-react — **no `axios`, no fetch wrapper, no router, no Stripe.js** | ✅ Verified absence |

No API client exists anywhere in `services/landing/src` (`grep` for `axios|fetch(|import.meta.env` returned zero matches). The landing page currently makes **zero network calls** to the backend.

### Admin dashboard (`services/admin/` — Next.js 14)

| File | Responsibility | Status |
|---|---|---|
| `src/app/page.js` (1391 lines) | Entire admin UI, including a "Subscription tier" field per user | ⚠️ **100% hard-coded mock data array** (lines 9–15); zero `fetch`/`axios` calls found in the file |
| `src/app/layout.js` | Next.js root layout | ✅ Active |
| `package.json` | `next`, `react`, `react-dom` only — no Stripe SDK | ✅ Verified absence |

### Deployment / environment configuration

| File | Relevance |
|---|---|
| `deployment/environments/backend.env.example` | No payment vars (Django secret, DB, SMTP, AWS S3/CloudFront, CORS only) |
| `deployment/environments/landing.env.example` | `NEXT_PUBLIC_BASE_URL`, `NEXT_PUBLIC_API_URL` — ⚠️ these are **Next.js-style** variable names in a **Vite** project's env template; Vite requires a `VITE_` prefix to expose vars to client code, so this template does not currently match the landing app's actual build tool. Neither variable is referenced anywhere in `services/landing/src` today. |
| `deployment/environments/admin.env.example` | `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_AI_URL`, `NEXT_PUBLIC_SKIP_AUTH` — correctly Next.js-style, but unused since `page.js` makes no network calls |
| `deployment/compose/*.yml`, `deployment/monitoring/*` | No payment-related services, env vars, or webhook routes |
| `.github/workflows/deploy.yml`, `pr-checks.yml`, `staging-deploy.yml` | No payment-related steps or secrets (the one keyword hit, `appleboy/ssh-action`, is a GitHub Action name for SSH deploys — unrelated to Apple payments) |
| `infrastructure/terraform`, `infrastructure/iam`, `infrastructure/ansible` | No payment-related resources found |

### Tests

| File | Test class / method | Coverage |
|---|---|---|
| `Apps/bookings/tests.py:989-1015` | `SubscriptionTests.test_subscribe`, `test_cancel_subscription` | Manual subscribe API call, cancel API call |
| `Apps/users/tests.py` | `UserModelTests.test_subscription_check` | `is_subscribed()` true/false transitions on `paid_user` |

No Apple, Google, Stripe, webhook, refund, renewal, duplicate-transaction, or concurrency tests exist — none of that code exists to test.

### Documentation

`docs/` contains 8 files (deployment, DR, infra, admin dashboard guide, CloudFront/media, DevOps walkthroughs). ✅ Verified: **none mention payments, billing, subscriptions, Apple, Google, or Stripe.** The subscription system is currently undocumented outside of the code itself.

---

## 4. Current payment architecture

ℹ️ CURRENT BEHAVIOR — there is one architecture today, and it is manual/self-service, not platform-processed:

```text
Authenticated barber user (any client: mobile app, Postman, curl, etc.)
    → POST /api/v1/subscriptions/subscribe/  { plan_id, payment_reference?, payment_method? }
    → Apps.subscriptions.views.SubscriptionCreateView
    → Checks: does the user already have an active Subscription row? (dynamic check)
    → Creates Subscription(status='pending', payment_reference=<client-supplied string>)
    → Subscription.activate() is called immediately, unconditionally
        → sets Subscription.status='active', start_date=now, end_date=now+30d or +365d
        → sets User.paid_user=True, User.current_plan, User.current_period_start/end
    → 201 response with the new subscription
```

- **Which component starts a purchase:** the API client itself, by calling `subscribe/` — there is no external checkout, no payment form, no redirect to any processor.
- **Which platform processes the money:** **none.** No money changes hands in this flow. `amount_paid` is stored (copied from `plan.price`) but never actually charged anywhere.
- **Which component verifies the purchase:** none exists. `payment_reference`/`payment_method` are arbitrary strings accepted at face value.
- **Which component stores transaction information:** `Apps.subscriptions.models.Subscription` (one row per subscription attempt).
- **Which component activates entitlement:** `Subscription.activate()`, which also updates the four subscription fields on `CustomUserModel`.
- **Which component handles renewals:** none — `auto_renew` is a stored boolean but nothing reads it; no scheduled job re-activates or extends a subscription at period end.
- **Which component handles cancellation:** `Subscription.cancel()`, called from `SubscriptionDetailView.delete()`. It marks the subscription `cancelled` but deliberately leaves `User.paid_user`/`current_period_end` untouched, so access continues until the stored period end (see §9).
- **Which component handles expiration:** `Subscription.expire()` exists and correctly clears the user's paid fields — **but nothing in the codebase ever calls it** (§9, ⚠️ GAP). No cron, Celery task, or management command exists anywhere in the repo (verified: no `Apps/*/management/` directory exists, no `celery` references anywhere in `services/backend`).
- **Which component receives platform notifications:** none — there is no webhook endpoint of any kind in this repository.
- **Which component provides subscription status to the client:** `SubscriptionDetailView` (`GET /api/v1/subscriptions/my/`) and the user serializer's `is_subscribed` field (`Apps/users/serializers.py:123`).
- **Source of truth:** the HairLync Postgres/SQLite database itself — specifically `Subscription.end_date` / `CustomUserModel.current_period_end`, evaluated **dynamically at request time** against `timezone.now()` (not a cached/stale flag) for the actual access decision. This live-comparison pattern is a genuine strength to preserve.

```text
Actual verified architecture (manual subscription, no processor):

API client (role=barber, authenticated)
    → POST /api/v1/subscriptions/subscribe/
    → SubscriptionCreateView (no payment verification)
    → Subscription record created + immediately activated
    → CustomUserModel.paid_user / current_plan / current_period_* updated
    → is_subscribed() / is_active_subscription evaluated live on every check
    → No renewal, no webhook, no expiration job
```

---

## 5. Apple App Store payment flow

❓ **No Apple integration exists in this repository.** Point-by-point against the requested checklist:

1. Apple product/subscription IDs configured — ❌ not found anywhere (no `.storekit` config, no product ID constants, no env vars).
2. Mobile purchase initiation — ❓ unverifiable; no mobile source in this repo.
3. Apple SDK/library — ❌ none (no StoreKit references in any dependency manifest).
4. Purchase data returned to app — ❓ unverifiable, no mobile code.
5. Data sent to backend — ❌ no backend endpoint accepts Apple-shaped data (no `original_transaction_id`, `signed_transaction`, or `receipt` field anywhere in any serializer or model).
6. Backend endpoint for Apple data — ❌ does not exist.
7. Backend verification of purchase — ❌ does not exist.
8. StoreKit 1 vs 2 — ❌ n/a, neither is used.
9. App Store Server API — ❌ not used; not a dependency.
10. Signed transaction verification — ❌ not implemented.
11. Receipt verification — ❌ not implemented.
12. Original transaction ID storage — ❌ no such field exists on `Subscription` or anywhere else.
13. Product ID → internal plan mapping — ❌ no mapping table/field exists.
14. Access activation on purchase — n/a (no Apple purchase path exists to activate from).
15. Renewals — ❌ not handled.
16. Cancellations — ❌ not handled (Apple-side).
17. Expirations — ❌ not handled (Apple-side).
18. Refunds/revocations — ❌ not handled.
19. App Store Server Notifications — ❌ no webhook endpoint exists.
20. Webhook authenticity verification — n/a, no webhook exists.
21. Duplicate transaction prevention — n/a, no transaction identifier field exists to de-duplicate on.
22. Purchase restoration — ❌ not implemented.
23. Sandbox vs production separation — ❌ not implemented/not applicable.
24. Apple purchase tests — ❌ none exist.

**Everything in this section is ❌ MISSING**, not partially implemented. There is no assumption to make here beyond: this must be designed and built from scratch (outside the scope of this audit).

---

## 6. Google Play payment flow

❓ Same conclusion as §5, verified by the same repo-wide search — **no Google Play Billing / Google Play Developer API integration exists.**

1. Google product/subscription IDs configured — ❌ not found.
2. Mobile purchase initiation — ❓ unverifiable, no mobile source.
3. Google Billing library — ❌ not a dependency anywhere.
4. Purchase token returned — ❓ unverifiable.
5. Data sent to backend — ❌ no `purchase_token`/`package_name`/`product_id` (Google-shaped) field exists anywhere in the backend.
6. Backend endpoint — ❌ does not exist.
7. Token verification — ❌ not implemented.
8. Google Play Developer API usage — ❌ not a dependency (`google-api-python-client`, `google-auth` are absent from `pyproject.toml`).
9. Service-account credentials — ❌ none configured/referenced.
10. Package name / product ID validation — ❌ not implemented.
11. Access activation — n/a.
12. Subscription acknowledgement — ❌ not implemented.
13. Renewals — ❌ not handled.
14. Cancellations — ❌ not handled (Google-side).
15. Expirations — ❌ not handled (Google-side).
16. Refunds/revocations — ❌ not handled.
17. Real-time Developer Notifications — ❌ no webhook exists.
18. Google Cloud Pub/Sub — ❌ not configured anywhere (no `google-cloud-pubsub` dependency, no topic/subscription name in any env template).
19. Duplicate transaction prevention — n/a, no purchase-token field exists.
20. Purchase restoration — ❌ not implemented.
21. Test/production environment separation — ❌ not implemented.
22. Google purchase tests — ❌ none exist.

**Everything in this section is ❌ MISSING.**

---

## 7. Current payment and subscription models

### `SubscriptionPlan` — `Apps/subscriptions/models.py:10-45`

| Field | Type | Notes |
|---|---|---|
| `name` | `CharField(unique=True)` | Only unique constraint in the schema |
| `billing_cycle` | `CharField(choices=monthly/yearly)` | |
| `price` | `DecimalField(10,2)` | Internal price, single currency implied (no currency field) |
| `description` | `TextField` | |
| `features` | `JSONField(list)` | Free-text feature list, display-only |
| `max_employees`, `max_portfolio_images`, `max_services` | `PositiveIntegerField` | ⚠️ **Defined but never read anywhere outside `models.py`/`admin.py`** — no view, serializer logic, or permission enforces these limits (verified by repo-wide grep) |
| `has_ai_recommendations`, `has_educational_content`, `has_analytics` | `BooleanField` | ⚠️ **Same — stored, never enforced.** The one place that *does* gate premium content (`Apps/education/views.py`) checks the user-level `is_subscribed()` boolean, not `plan.has_educational_content` — i.e., access is currently "any paid plan unlocks everything," not tiered by these flags despite the schema supporting tiers |
| `is_active` | `BooleanField` | Used to filter the public plan list |
| `created_at` | auto | No `updated_at` |

No indexes beyond the implicit PK and the `name` unique constraint.

### `Subscription` — `Apps/subscriptions/models.py:51-143`

| Field | Type | Notes |
|---|---|---|
| `user` | FK → `AUTH_USER_MODEL`, `limit_choices_to={'role': 'barber'}`, `CASCADE`, related_name `subscriptions` | Not `unique=True` — a user **can** have multiple `Subscription` rows (by design, for history), but see ⚠️ below for a gap in keeping only one truly "active" |
| `plan` | FK → `SubscriptionPlan`, `PROTECT` | Prevents deleting a plan that has subscriptions |
| `status` | `CharField(choices)`: `active/expired/cancelled/pending` | ⚠️ Not automatically transitioned to `expired` — see §9 |
| `start_date`, `end_date` | `DateTimeField(null=True)` | Computed in `activate()`: `+30 days` (monthly) or `+365 days` (yearly), hard-coded, not driven by `plan.billing_cycle` lookup table |
| `payment_reference` | `CharField(255, blank)` | Free text, client-supplied, unverified — labelled "integration-ready" in a comment |
| `payment_method` | `CharField(50, blank)` | Free text, defaults to `'manual'` |
| `amount_paid` | `DecimalField(10,2, default=0)` | Copied from `plan.price` at creation time; **never actually charged** |
| `auto_renew` | `BooleanField(default=True)` | Stored, never acted upon |
| `cancelled_at` | `DateTimeField(null=True)` | |
| `created_at`, `updated_at` | auto | |

No unique constraints beyond PK. No index on `(user, status)` despite that being the most common query pattern (`Subscription.objects.filter(user=..., status='active')`).

### Answers to the required schema questions

- **Do Apple and Google use the same internal subscription model?** ❓ N/A today — there is no Apple/Google code, so no comparison exists yet. The existing `Subscription` model has **no platform discriminator field** at all (no `platform`/`source` choice of `apple`/`google`/`stripe`/`manual`) — this will need to be added.
- **Can one user have multiple active subscriptions?** ⚠️ At the **database level, yes** — nothing prevents two `Subscription` rows with `status='active'` for the same user (no unique constraint, no `select_for_update`). At the **application level**, `SubscriptionCreateView` does a best-effort check before creating a new one, but it is not atomic (race condition, see §12).
- **Are duplicate transactions prevented at the DB level?** ❌ No — there is no transaction/purchase-token identifier field to apply a uniqueness constraint to.
- **Is subscription history preserved?** ✅ Yes — `Subscription` rows are never deleted on cancel/expire, and `SubscriptionHistoryView` lists all of a user's rows ordered by `-created_at`.
- **Is platform-specific data mixed with generic subscription data?** N/A today (no platform-specific data exists yet) — but this is exactly the risk to watch when Stripe fields are added (see §19–20): a `customer_id`/`price_id`/`payment_intent_id` should not collide with a future `original_transaction_id`/`purchase_token`.
- **Can the current schema support Stripe safely?** 💡 Yes, **additively** — the model has no Apple/Google-specific fields to conflict with, and `payment_reference`/`payment_method` could hold a Stripe subscription ID as an interim measure, though dedicated fields would be cleaner. See §19.
- **Will adding Stripe require migrations?** 💡 Yes, at minimum: a `platform` field, Stripe-specific identifiers (`stripe_customer_id`, `stripe_subscription_id`, `stripe_price_id`), and ideally a `unique_together`/partial-unique constraint to prevent duplicate active subscriptions per user. This is a **forward-looking recommendation**, not something implemented in this audit.

---

## 8. Plans, products, and pricing

- **Do plans exist in the database?** ✅ Yes — `SubscriptionPlan` is a real, admin-manageable model (creatable via Django admin or `POST /api/v1/subscriptions/plans/create/`, admin-only).
- **Are plans hard-coded?** ⚠️ Partially — the backend plans are DB-driven, but the **landing page pricing UI is entirely hard-coded** in `Plans.jsx` (4 tiers: Free/$0, Professionals/$25, Business/$75, Yearly/$18-per-month) and is **not fetched from `GET /api/v1/subscriptions/plans/`**. There is no evidence these hard-coded landing prices match whatever plans currently exist in the database — they cannot be reconciled from code alone.
- **Are product IDs stored in env vars?** ❌ No Apple/Google product IDs exist anywhere (no such integration exists).
- **Do Apple and Google use identical products / map to one internal plan?** ❓ N/A — no such mapping exists.
- **Are prices stored internally?** ✅ Yes, `SubscriptionPlan.price` (single `Decimal` field).
- **Are currencies stored?** ❌ No currency field exists anywhere in the schema — single implied currency (USD, based on landing page `$` signs), not configurable per plan.
- **Are billing intervals stored?** ✅ Yes, `billing_cycle` (`monthly`/`yearly` only).
- **Do plans support monthly and yearly billing?** ✅ Yes, both choices exist and `activate()` branches on them.
- **Do trials exist?** ❌ No trial field/logic anywhere in the backend. (The landing page's `Freetrial.jsx` advertises "Start your Hairlync trial for 30 days" and a "Start your free scan" button with **no click handler and no backend endpoint** — purely aspirational marketing copy today.)
- **Discounts/promotional offers?** ❌ None in the backend. The landing page shows a static "Save 30%" badge on the yearly card — cosmetic only, not backed by any pricing logic.
- **One-time payments?** ❌ Not modeled — the schema is subscription-only (no `one_time` product type).
- **Do plans control user features?** ⚠️ Partially — `max_employees`/`max_services`/etc. and the `has_*` booleans exist on the model but are **not enforced anywhere** (§7). Only a coarse "paid vs free" gate is enforced (§9).
- **Does the landing page already display pricing?** ✅ Yes (`Plans.jsx`), but as static/disconnected UI only.

### Plan mapping table (as required by the task)

| Internal plan | Apple product ID | Google product ID | Billing period | Internal entitlement |
|---|---|---|---|---|
| *(whatever rows currently exist in `SubscriptionPlan`, unknown without a live DB dump — not inspected to avoid any state-mutating query)* | Not applicable — no Apple integration exists | Not applicable — no Google integration exists | `monthly` or `yearly` per plan | Binary via `User.is_subscribed()`; per-plan feature fields exist but are unused |

❓ **Open/unverifiable:** the exact current rows in `SubscriptionPlan` (names/prices actually seeded in the running database) were not queried, since doing so would require executing DB-reading code outside the safe, already-covered test run; this is not derivable from static source alone. Recommend the product owner or a `python manage.py shell` read-only query (outside this audit) to confirm current live plan data before designing Stripe price mapping.

---

## 9. Subscription and entitlement logic

**What happens after a successful "purchase" today** (`Subscription.activate()`, `Apps/subscriptions/models.py:104-122`):

1. `Subscription.status` → `'active'`, `start_date`/`end_date` set.
2. `User.paid_user` → `True`.
3. `User.current_plan` → the plan's `billing_cycle` string (`'monthly'`/`'yearly'`) — note this reuses the billing-cycle value as the "current plan" name, not the plan's actual `name`/id. This means the user model cannot currently distinguish *which* plan (e.g., "Professionals" vs "Business") a barber is on — only monthly-vs-yearly.
4. `User.current_period_start`/`current_period_end` set.
5. `user.save(update_fields=[...])` — partial save, four fields only.

**How active plan / access is determined:**
- ✅ **Dynamically, not from a cached flag alone.** `User.is_subscribed()` (`Apps/users/models.py:132-138`) re-checks `current_period_end < timezone.now()` on every call — so a subscription that has silently run past its `end_date` correctly reports `is_subscribed() == False` even though `paid_user` is still stored as `True` and even though the related `Subscription.status` is still stored as `'active'` (see the gap below). This means **API-level access enforcement is currently correct despite the missing expiration job** — the staleness only affects admin-facing display fields, not actual gating.

- ⚠️ **GAP — expiration is never actively enforced/reconciled.** `Subscription.expire()` (`Apps/subscriptions/models.py:131-142`) is the only code path that resets `paid_user=False`, `current_plan='free'`, and clears the period fields, and also flips `Subscription.status` to `'expired'`. **It is never called anywhere in the codebase** — no Celery task, cron, management command, signal, or admin action invokes it (confirmed: no `Apps/*/management/` directories exist; no `celery` reference anywhere in `services/backend`). Consequences:
  - `User.paid_user` and `Subscription.status='active'` become **stale/inaccurate** indefinitely after natural expiry (functionally harmless for gating, since `is_subscribed()`/`is_active_subscription` re-check the date, but **misleading for admin reporting** — `Apps/users/admin.py` filters on `paid_user` directly).
  - A user who lets a subscription lapse and then re-subscribes can end up with **two `Subscription` rows both showing `status='active'`** in the database (the duplicate-check in `SubscriptionCreateView` uses the dynamic `is_active_subscription` property, not the raw `status` field, to decide whether to block a new subscription — so it correctly allows a new one after expiry, but never cleans up the old row's status).

- **Feature access checks:** `IsSubscribedBarber` (`Apps/users/permissions.py:113-123`) is the only permission class that checks `is_subscribed()`, but it is **imported and unused** in `Apps/services/views.py`, `Apps/profiles/views.py`, and `Apps/recommendations/views.py` — none of those apps' `permission_classes` actually include it (verified: `grep` for `permission_classes.*Subscribed` across the repo returns zero matches). The only place subscription status is actually enforced is `Apps/education/views.py`, gating premium (`is_premium=True`) educational content, via a direct `request.user.is_subscribed()` call rather than the permission class.

- **Frontend/mobile status delivery:** `GET /api/v1/subscriptions/my/` and the `is_subscribed` field on the general user-detail serializer (`Apps/users/serializers.py:107,123-124`).

- **Admin manual override:** ✅ Yes — because `paid_user`/`current_plan`/`current_period_start`/`current_period_end` are plain editable fields on `CustomUserModel`, a Django admin/superuser can edit them directly via `/admin/` (`Apps/users/admin.py:17` exposes a "Subscription" fieldset). There is no dedicated "grant/revoke" admin action, just raw field editing.

- **Refund/revocation removing access:** N/A — no refund concept exists anywhere (no payment was ever taken).

- **Cancellation vs. immediate access removal:** ✅ VERIFIED — `Subscription.cancel()` does **not** touch the user's paid fields, so access correctly continues until `current_period_end`, matching the API's own response message ("You will retain access until the end of the billing period," `Apps/subscriptions/views.py:118`). This is the one piece of lifecycle logic that behaves exactly as documented.

---

## 10. Payment API endpoints

| Method | Endpoint | View | Auth | Platform | Purpose |
|---|---|---|---|---|---|
| GET | `/api/v1/subscriptions/plans/` | `SubscriptionPlanListView` | `AllowAny` | n/a | List active plans (public) |
| POST | `/api/v1/subscriptions/plans/create/` | `SubscriptionPlanAdminView` | `IsAdminUser` | n/a | Create a plan (admin only) |
| POST | `/api/v1/subscriptions/subscribe/` | `SubscriptionCreateView` | `IsAuthenticated`, `IsBarber` | Manual only | Create + auto-activate a subscription |
| GET | `/api/v1/subscriptions/my/` | `SubscriptionDetailView` | `IsAuthenticated`, `IsBarber` | Manual only | Get current (latest) subscription |
| DELETE | `/api/v1/subscriptions/my/` | `SubscriptionDetailView` | `IsAuthenticated`, `IsBarber` | Manual only | Cancel active subscription |
| GET | `/api/v1/subscriptions/history/` | `SubscriptionHistoryView` | `IsAuthenticated`, `IsBarber` | Manual only | List all of the user's subscription rows |

No webhook route, no checkout-session route, no billing-portal route exists.

### `POST /api/v1/subscriptions/subscribe/` — detail

**Request** (per `SubscriptionCreateSerializer`, `Apps/subscriptions/serializers.py:28-31`):
```json
{
  "plan_id": 3,
  "payment_reference": "",
  "payment_method": "manual"
}
```
`payment_reference` and `payment_method` are optional free-text strings with **no format validation, no relation to any real payment record**.

**Response 201** (per `SubscriptionSerializer`):
```json
{
  "success": true,
  "message": "Subscription activated successfully.",
  "data": {
    "id": 12,
    "plan_details": { "id": 3, "name": "Professionals Plan", "billing_cycle": "monthly", "price": "25.00", "...": "..." },
    "is_active": true,
    "user": 7,
    "status": "active",
    "start_date": "2026-07-16T10:00:00Z",
    "end_date": "2026-08-15T10:00:00Z",
    "payment_reference": "",
    "payment_method": "manual",
    "amount_paid": "25.00",
    "auto_renew": true,
    "cancelled_at": null,
    "created_at": "2026-07-16T10:00:00Z",
    "updated_at": "2026-07-16T10:00:00Z"
  }
}
```
(`success_response`/`error_response` wrapper per `Apps/users/utils.py`, used consistently across the API.)

**Errors:** `404` plan not found/inactive; `400` already has an active subscription.

**Idempotency:** ⚠️ None. Calling this endpoint twice quickly for the same user can, in principle, create two `Subscription` rows (see §12 race condition). There is no idempotency key parameter.

**Security risk:** 🔐 See §13 — this endpoint grants paid access on nothing more than an authenticated request; `payment_reference` is accepted but never checked against anything.

---

## 11. Webhooks and platform notifications

❌ **No webhook or notification endpoint of any kind exists in this repository** — confirmed by:
- No `urls.py` anywhere defines a `webhook`/`notify`/`callback` path.
- No view verifies a signature, JWS, or shared secret.
- No Apple App Store Server Notification handling (renewal/expiration/cancellation/refund/revocation/billing-retry/grace-period) exists.
- No Google Real-time Developer Notifications / Pub/Sub handling (renewal/cancellation/expiration/refund/revocation/account-hold/grace-period/pause-resume) exists.

This is a complete gap, to be built for Stripe (and eventually Apple/Google) rather than something to compare against existing behavior.

---

## 12. Idempotency and duplicate-payment protection

Assessed against each item requested:

- **Same Apple transaction processed twice:** n/a, no Apple transactions exist.
- **Same Google purchase token processed twice:** n/a, no Google tokens exist.
- **Activating the same subscription multiple times:** ⚠️ Possible — `activate()` has no guard against being called on an already-active subscription; nothing currently calls it twice, but no defensive check (e.g., `if self.status == 'active': return`) exists either.
- **Duplicate platform notifications:** n/a, no webhook exists to receive them.
- **Conflicting active subscriptions:** ⚠️ **Race condition identified.** `SubscriptionCreateView.post()` (`Apps/subscriptions/views.py:50-83`) does a plain `.filter(...).first()` read-then-write with **no `transaction.atomic()` block and no `select_for_update()`**. Two near-simultaneous `POST /subscribe/` requests from the same authenticated user (e.g., a double-tap on a mobile "Subscribe" button, or a retried request after a slow response) can both pass the "no active subscription" check before either has committed, resulting in two `Subscription` rows with `status='active'` for the same user and two separate `activate()` calls (each doing a `user.save()`), all inside the current transaction-less flow.
- **Replaying old payment requests:** ⚠️ Possible — nothing prevents resubmission of an old `payment_reference` value; it isn't checked against anything.
- **Two simultaneous verification requests:** n/a, there is no verification step at all today (nothing to race on other than the creation race above).

**Database-level protections:** none — no unique constraint, no partial unique index (e.g., "at most one `status='active'` row per user"), no idempotency-key table, no event-log/webhook-event table.

💡 This is the single most important structural gap to close **before or alongside** Stripe: Stripe webhooks are delivered at-least-once and can arrive out of order or duplicated, so an idempotency/event-log mechanism (e.g., a `WebhookEvent` table keyed by Stripe event ID, plus `transaction.atomic()` + `select_for_update()` around subscription creation/activation) will be needed regardless of platform. This is a recommendation, not something implemented here.

---

## 13. Security review

🔐 **Findings, most significant first:**

1. 🔐 **HIGH — Unverified self-service entitlement grant.** `POST /api/v1/subscriptions/subscribe/` grants `paid_user=True` and full paid access to *any* authenticated barber, based solely on a client-supplied `plan_id` and an unvalidated `payment_reference` string, with **no payment actually collected or verified**. `amount_paid` is recorded but not charged. *This is intentional stub behavior* (explicitly commented as such in the source), not a vulnerability introduced by a bug — but it means **today, in this codebase, "purchasing" a subscription costs nothing and requires no real payment step from any platform.** This must be explicitly closed off (removed or admin/internal-only gated) once a real processor (Stripe first) is wired in, or barbers will be able to activate paid tiers for free indefinitely through this endpoint.
2. 🔐 **MEDIUM — Race condition on subscription creation** (§12) — no atomicity/locking around the "check no active subscription, then create + activate" sequence.
3. 🔐 **LOW — Dead/inconsistent permission wiring.** `IsSubscribedBarber` is imported in 3 files (`services`, `profiles`, `recommendations` views) but never applied — this isn't exploitable today (those endpoints simply aren't subscription-gated, which may or may not be intentional), but it signals the access-control model is easy to silently under-enforce; worth an explicit audit of *which* endpoints are meant to require a paid plan before Stripe-gated features are added.
4. **Hard-coded secrets in source control:** ✅ None found related to payments (none exist to be hard-coded). General repo secret hygiene (`.env` files, Django secret key, DB password, email password) is handled via environment variables/`*.env.example` templates, consistent with the rest of the codebase; no plaintext credentials were observed committed in the files inspected during this audit. (`hairlync.pem` exists at the repo root but is unrelated to payments and outside this audit's scope — flagged only for completeness, not inspected further.)
5. **IDOR / cross-user purchase verification:** N/A today — `subscribe/`, `my/`, and `history/` all correctly scope to `request.user`; there is no endpoint that accepts another user's ID for a subscription action.
6. **Raw payment payloads in logs/API responses:** N/A — no receipts/tokens exist yet to leak.
7. **Currency/price manipulation:** ⚠️ Worth noting for Stripe design — `SubscriptionCreateView` trusts `plan.price` from the DB (not client input) for `amount_paid`, which is correct practice and should be preserved: **never let a client dictate the charged amount** when Stripe Checkout Sessions are built later (use server-side Stripe Price IDs, not client-submitted prices).
8. **Missing HTTPS / environment separation assumptions:** Django settings (`CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` in `backend.env.example`) reference `https://` production hosts and separate local ports — standard, not a payment-specific issue.

No secret **values** are reproduced anywhere in this report, per instructions.

---

## 14. Environment variables and third-party configuration

### Apple
❌ **None exist.** No bundle ID, issuer ID, key ID, private key, shared secret, or App Store environment variable appears anywhere in `.env.example`, `deployment/environments/*`, `deployment/compose/*`, `.github/workflows/*`, or Django `settings.py`.

### Google
❌ **None exist.** No package name, service-account credential path, GCP project ID, Pub/Sub topic/subscription name, or Play Billing environment variable appears anywhere.

### Stripe
❌ **None exist.** No `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`, price/product IDs, or any Stripe-prefixed variable appears in any env template, compose file, or workflow.

### What *does* exist today (for context, non-payment):

| Variable | Defined in | Used in | Notes |
|---|---|---|---|
| `DJANGO_SECRET_KEY`, `DB_*`, `EMAIL_*`, `AWS_*`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` | `deployment/environments/backend.env.example`, `services/backend/.env.example` | `core/settings.py` | Server-only, standard Django config, no payment relevance |
| `NEXT_PUBLIC_BASE_URL`, `NEXT_PUBLIC_API_URL` | `deployment/environments/landing.env.example` | ⚠️ **Not referenced anywhere in `services/landing/src`** — dead template entries for the current Vite-based landing app (Vite needs a `VITE_` prefix, not `NEXT_PUBLIC_`) | Flagged as a pre-existing inconsistency to resolve when adding any new client-exposed variable (e.g., a future Stripe publishable key) to the landing page |
| `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_AI_URL`, `NEXT_PUBLIC_SKIP_AUTH` | `deployment/environments/admin.env.example` | ⚠️ **Not referenced in `services/admin/src/app/page.js`** (which has zero `process.env` usage) — admin dashboard is fully mocked today | Correctly Next.js-shaped, just currently unused |

---

## 15. Payment dependencies

**Backend (`services/backend/pyproject.toml`):** Django, `django-cors-headers`, `django-filter`, `django-rest-framework`, `django-storages[boto3]`, `djangorestframework-simplejwt`, `drf-yasg`, `pillow`, `python-dotenv`, `requests`, `whitenoise`. ✅ **No `stripe`, no `google-auth`/`google-api-python-client`, no `pyjwt`/`cryptography` used for Apple JWS verification, no `celery`.**

**Landing (`services/landing/package.json`):** React 19, `framer-motion`, `tailwindcss`, `lucide-react`, Vite toolchain. ✅ **No `@stripe/stripe-js`, no `@stripe/react-stripe-js`, no `axios`.**

**Admin (`services/admin/package.json`):** Next.js 14, React 18. ✅ **No Stripe SDK, no HTTP client.**

**Mobile:** ❓ Not present in this repository — cannot be audited.

No Stripe SDK is installed anywhere. No outdated/duplicated payment-related packages exist because none exist at all.

---

## 16. Landing-page readiness

- **Framework:** Vite + React 19 (confirmed via `package.json`, `vite.config` toolchain), **not** Next.js despite the sibling admin app being Next.js.
- **Authentication from the landing page:** ❌ None. No login/signup form, no token storage (`localStorage`/cookies), no auth-related code found anywhere in `services/landing/src`.
- **Sign up / log in:** ❌ Not currently possible from the landing page.
- **Pricing shown:** ✅ Yes (`Plans.jsx`), but static/hard-coded, not fetched from the backend.
- **Plan-selection UI:** ⚠️ Visually present (4 cards with buttons) but **non-functional** — buttons have no `onClick` handlers.
- **Checkout button:** ❌ No real checkout button exists (the visual buttons do nothing).
- **Payment-related components:** ❌ None beyond the static pricing cards.
- **Communication with backend:** ❌ None — zero `fetch`/`axios` calls anywhere in the landing source.
- **API base URL configuration:** ⚠️ A `NEXT_PUBLIC_API_URL` var is templated in `deployment/environments/landing.env.example` but is unused by the actual Vite code (see §14).
- **Token storage:** N/A, no auth exists.
- **Logged-in vs logged-out checkout flows:** ❌ Neither is possible today — there is no logged-in state on the landing page at all.
- **Where would Stripe Checkout logically connect:** 💡 The `Plans.jsx` buttons (currently inert) are the natural insertion point for "Subscribe" → create-checkout-session calls.
- **Success/cancelled payment pages:** ❌ Neither exists.
- **Routing for checkout callbacks:** ❌ **No routing library is installed at all** (`react-router-dom` or equivalent is absent from `package.json`) — the entire app is a single unrouted page (`App.jsx` simply stacks all sections vertically). Any Stripe success/cancel redirect URLs would currently have nowhere to route to without first adding a router.
- **Deployment env var support:** ✅ The deployment pipeline (env templates + compose files) has an established pattern (`*.env.example` → `.env.local.*`/`.env.production.*` → compose) that could accommodate new variables like a Stripe publishable key, provided the Vite-vs-`NEXT_PUBLIC_` naming mismatch above is resolved first.

---

## 17. Cross-platform subscription behavior

The current schema and logic were evaluated against each requested scenario. Since Apple/Google/Stripe code does not exist yet, these are necessarily forward-looking assessments of what the *current* data model would/would not support, not descriptions of tested behavior:

| Scenario | Current verified behavior |
|---|---|
| User subscribes via a platform, later logs in elsewhere | ✅ Entitlement lives on `CustomUserModel` (`paid_user`/`current_plan`/`current_period_*`), not on a device or session — so **any** client reading `is_subscribed()` via the API would see consistent status, *once* a real platform integration actually writes to those fields the way `activate()` does today. |
| User has a subscription on one platform and attempts to purchase on another | ⚠️ **Not prevented today** — `SubscriptionCreateView`'s duplicate check only looks at `Subscription.objects.filter(user=..., status='active')`; it has no concept of "platform," so nothing today would stop a second `Subscription` row being created by a different channel while one is already active, once multiple channels exist. |
| User cancels on one platform | ℹ️ Only the generic `cancel()` behavior exists today (access continues until `current_period_end`) — there's no platform-specific cancellation handling to differentiate. |
| Refund | ❌ No refund concept exists anywhere. |
| Plan change | ❌ No "upgrade/downgrade" endpoint exists; only create-new/cancel-current. |
| Platform switch | ❌ Not modeled — no `platform` field exists on `Subscription` to even represent "which channel is this row from." |
| Same account, multiple payment records | ✅ Supported structurally (`Subscription` has no `unique=True` on `user`), consistent with preserving history. |
| Different accounts try to restore the same store purchase | N/A — no store purchase/restoration exists. |

❓ **All of the above are open items** requiring both a schema addition (a `platform`/`source` field at minimum) and explicit product decisions (§ below) before Stripe, Apple, and Google can safely coexist.

---

## 18. Existing tests and test results

**Test files/methods found:**

| File | Class.method | Covers |
|---|---|---|
| `Apps/bookings/tests.py:989-1006` | `SubscriptionTests.test_subscribe` | POST `/subscribe/` → 201, and confirms `barber.is_subscribed()` becomes `True` |
| `Apps/bookings/tests.py:1008-1015` | `SubscriptionTests.test_cancel_subscription` | Creates + activates a subscription directly, then DELETE `/my/` → 200 |
| `Apps/users/tests.py` | `UserModelTests.test_subscription_check` | Verifies `is_subscribed()` is `False` by default and `True` once `paid_user=True` |

**Command run (safe, read-only w.r.t. repository state — uses Django's ephemeral in-memory SQLite test DB, destroyed automatically):**
```bash
cd services/backend
uv run python manage.py test Apps.users.tests.UserModelTests Apps.bookings.tests.SubscriptionTests -v 2
```

**Result:**
```
test_create_superuser ... ok
test_create_user ... ok
test_subscription_check ... ok
test_user_roles ... ok
test_cancel_subscription ... ok
test_subscribe ... ok

Ran 6 tests in 1.176s
OK
```
✅ All 6 relevant tests pass against the current codebase, unmodified.

**Not tested (because the code doesn't exist):** valid/invalid Apple purchase, duplicate Apple transaction, Apple renewal/cancellation/refund, valid/invalid Google token, duplicate Google token, Google renewal/cancellation/refund, webhook verification, cross-user purchase attempts, concurrent verification requests, sandbox/production environment behavior. Also not tested by the existing suite: subscription expiration (no test calls `expire()` or asserts stale-access cleanup), and the race condition identified in §12.

`Apps/subscriptions/` itself has **no `tests.py`** — all its coverage lives in `Apps/bookings/tests.py` instead, which is somewhat unconventional (worth normalizing later, not urgent).

---

## 19. Stripe integration impact areas

*(Impact analysis only — no implementation performed or proposed in detail.)*

### Backend

| Area | Why it would need to change | Risk to Apple/Google | Additive? |
|---|---|---|---|
| `Apps/subscriptions/models.py` | Add a `platform` discriminator and Stripe identifiers (`stripe_customer_id`, `stripe_subscription_id`, `stripe_price_id`) to `Subscription`/`SubscriptionPlan` | Low, if fields are added rather than existing ones repurposed | ✅ Additive |
| New migration(s) | Required for the fields above | Low | ✅ Additive |
| `Apps/subscriptions/serializers.py`, `views.py`, `urls.py` | New endpoints: create Stripe Checkout Session, Stripe billing portal, Stripe webhook receiver | None to existing manual-flow endpoints, if they remain untouched | ✅ Additive |
| New Stripe service layer (e.g., `Apps/subscriptions/services/stripe_service.py`) | Isolate Stripe SDK calls from views | None | ✅ Additive |
| Webhook handling + idempotency (event-log table) | Required for safe, at-least-once Stripe event delivery | None directly, but the underlying race condition (§12) affects *all* channels, so fixing it benefits Apple/Google too | ✅ Additive (new table) |
| `Apps/subscriptions/admin.py` | Surface Stripe fields in Django admin | None | ✅ Additive |
| `core/settings.py` | Add `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` reads | None | ✅ Additive |
| `pyproject.toml` | Add `stripe` SDK dependency | None | ✅ Additive |
| Tests | New `Apps/subscriptions/tests.py` (currently missing entirely) for Stripe flows | None | ✅ Additive |

### Landing page

| Area | Why it would need to change | Risk | Additive? |
|---|---|---|---|
| `src/components/Plans.jsx` | Wire the currently-inert buttons to a real checkout call; ideally fetch plans from `GET /api/v1/subscriptions/plans/` instead of hard-coded prices | None to backend | ✅ Additive |
| Authentication | Landing page has none today — a checkout flow needs to know *who* is buying (new user vs. existing) | None | New capability, not a change to existing behavior |
| New success/cancel pages + a router | `react-router-dom` (or similar) isn't installed at all today | None | ✅ Additive |
| API client | No `fetch`/`axios` wrapper exists — needs to be introduced | None | ✅ Additive |
| Env vars | Needs a `VITE_`-prefixed API URL and Stripe publishable key; the existing `NEXT_PUBLIC_*` template for landing is currently unused dead config that should be reconciled, not blindly extended | Low — just naming cleanup | ✅ Additive once corrected |

### Deployment

| Area | Why | Risk | Additive? |
|---|---|---|---|
| `deployment/environments/backend.env.example` / `.env.production.backend` etc. | Add `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Secrets handling only, no existing var touched | ✅ Additive |
| `deployment/environments/landing.env.example` | Add Stripe publishable key + correct `VITE_` prefix | None | ✅ Additive (with a naming fix) |
| New public webhook route exposure (nginx/ALB config in `deployment/nginx`, `infrastructure/terraform`) | Stripe needs a reachable HTTPS webhook URL | Must not accidentally expose other internal routes | ✅ Additive, but needs care |
| CI/CD (`deploy.yml`, `staging-deploy.yml`) | Inject new secrets into the deploy pipeline | None to existing Apple/Google steps (none exist) | ✅ Additive |

---

## 20. Backward-compatibility assessment

Because Apple and Google integrations **do not exist yet**, "preserving the existing Apple/Google flow" is, today, equivalent to **preserving the existing manual-subscription flow and its data**:

Must be preserved:
- `POST /api/v1/subscriptions/subscribe/`, `GET/DELETE /api/v1/subscriptions/my/`, `GET /api/v1/subscriptions/history/`, `GET /api/v1/subscriptions/plans/` request/response shapes, since any existing client (mobile app or otherwise) may already depend on them.
- The `CustomUserModel.paid_user`/`current_plan`/`current_period_start`/`current_period_end` contract — this is the field set every existing permission/serializer check reads; a Stripe integration should **populate these same fields** (via the same `activate()`/`expire()` pattern or an equivalent) rather than introduce a parallel, disconnected entitlement source.
- Existing `Subscription`/`SubscriptionPlan` rows and the cancellation semantics ("access continues until period end").
- The dynamic, live-date-comparison pattern in `is_subscribed()`/`is_active_subscription` — this is what makes expiration correct today *despite* the missing cron job; any Stripe-driven expiration path should keep using/updating the same `current_period_end` field rather than only flipping a separate boolean.

**Code paths where adding Stripe could accidentally break the existing flow:**
- If `Subscription.activate()`/`cancel()`/`expire()` are refactored to take a `platform` argument or new required fields, the existing manual `SubscriptionCreateView` call site must be updated in lockstep, or it will break.
- If new Stripe-specific required fields are added to `Subscription` without defaults, the existing manual-flow `Subscription.objects.create(...)` call (`Apps/subscriptions/views.py:68-74`, no platform-specific args today) would fail on `IntegrityError`/`ValidationError`.
- If a `platform` discriminator is added and the duplicate-active-subscription check in `SubscriptionCreateView` is changed to be platform-aware, care must be taken not to silently allow the exact race condition in §12 to get worse (e.g., "one active manual + one active Stripe" simultaneously, if that's not an intended business rule — see open decisions below).
- Since there is currently no `Apps/subscriptions/tests.py`, there's no existing automated regression net specifically for this app beyond the two `bookings/tests.py` tests and the one `users/tests.py` test — any Stripe change should extend, not assume, coverage.

---

## 21. Open business and technical decisions

❓ These cannot be answered from code and must come from the product owner:

1. Is Stripe a one-time payment or a recurring subscription on the landing page?
2. Should billing be monthly, yearly, or both (mirroring the existing `billing_cycle` choices)?
3. Which specific plans (of whatever currently exists in `SubscriptionPlan`) are sold via Stripe on the landing page — all of them, or a curated subset?
4. Should Stripe pricing match Apple/Google pricing exactly, and who owns keeping them in sync?
5. Which currencies are supported (the schema currently has no currency field at all)?
6. Should a user be prevented from holding simultaneous active subscriptions across Apple, Google, and Stripe, or is that acceptable?
7. If a user switches platforms, how should the transition work (immediate switch vs. wait for the old one to lapse)?
8. Should Stripe customers get a self-service billing portal (Stripe's hosted portal makes this easy, but it's a decision, not a given)?
9. How should a Stripe refund affect `paid_user`/`current_period_end` — immediate revocation, or same "access until period end" behavior as the current manual cancellation?
10. Which system is the ultimate source of truth for entitlement once three channels exist — is it still `CustomUserModel` fields updated by each channel's webhook (recommended, since it's what every existing permission check already reads), or something else?
11. Should the currently-unenforced per-plan feature flags (`max_employees`, `has_ai_recommendations`, etc.) finally be enforced as part of this work, or left as-is?
12. Should the dead `IsSubscribedBarber` permission actually be wired into `services`/`profiles`/`recommendations` views, or was that intentionally left unenforced?

None of these are decided in this document; they are listed so implementation work isn't blocked guessing at them.

---

## 22. Recommended implementation direction

💡 (Recommendation only — not implemented here, per the task's restrictions.)

1. Fix the structural gaps that affect *all* channels first, since they'll otherwise undermine Stripe too: wrap subscription creation/activation in `transaction.atomic()` + `select_for_update()` (§12), and either wire up a real expiration job or accept/document that live date-comparison is the permanent design (§9) — worth an explicit decision either way.
2. Add a `platform` field to `Subscription` (`manual`/`stripe`/`apple`/`google`) before or alongside the Stripe work, so the schema doesn't need a second migration wave when Apple/Google eventually follow.
3. Build Stripe additively: new fields, new endpoints, new webhook handler, new service module — without modifying the request/response shape of the four existing manual endpoints unless a decision (§21) explicitly calls for retiring the manual path.
4. Reuse the existing `CustomUserModel` fields as the entitlement sink for Stripe (same fields `activate()` already writes), so every existing permission check (`is_subscribed()`, `IsSubscribedBarber`, the education-app gate) keeps working unchanged.
5. Resolve the `NEXT_PUBLIC_*`-vs-Vite mismatch in `deployment/environments/landing.env.example` before adding a Stripe publishable key there, and add a router to the landing app before building success/cancel pages.

---

## 23. Final verified flow diagrams

### Apple — current flow (nothing implemented)
```text
User
→ Mobile app                [❓ not present in this repository]
→ Apple App Store            ❌ not integrated
→ Purchase result            ❌ no code receives this
→ Backend verification       ❌ does not exist
→ Payment/subscription record ❌ no Apple-specific fields exist
→ User access                ❌ no Apple-driven activation path exists
```

### Google — current flow (nothing implemented)
```text
User
→ Mobile app                 [❓ not present in this repository]
→ Google Play                ❌ not integrated
→ Purchase token              ❌ no code receives this
→ Backend verification        ❌ does not exist
→ Payment/subscription record ❌ no Google-specific fields exist
→ User access                 ❌ no Google-driven activation path exists
```

### Actual current flow (manual/stub — what really runs today)
```text
Authenticated barber (any client)
→ POST /api/v1/subscriptions/subscribe/  (plan_id, free-text payment_reference/method)
→ SubscriptionCreateView            [no payment verification of any kind]
→ Subscription.objects.create(status='pending', ...)
→ Subscription.activate()           [called unconditionally]
→ CustomUserModel.paid_user=True, current_plan, current_period_start/end set
→ is_subscribed() / IsSubscribedBarber / education-app checks read these fields dynamically
```

### Planned conceptual diagram — NOT IMPLEMENTED
```text
Landing-page user
→ Select plan
→ HairLync backend
→ Stripe Checkout
→ Stripe webhook
→ Payment/subscription record
→ Shared HairLync entitlement (same CustomUserModel fields used today)
```

---

## 24. Final summary requirements

### Current implementation summary
Apple and Google payments **do not work today** — no code for either exists anywhere in this repository. What exists is a manual, self-service Django subscription system (`Apps.subscriptions` + `CustomUserModel` fields) that a client activates by calling one API endpoint with an unverified free-text payment reference; the backend immediately grants paid access with no money collected or checked.

### Existing strengths
- Entitlement is centralized on `CustomUserModel` and evaluated **dynamically** (live date comparison), not from a stale cached flag — a solid foundation to build multi-channel entitlement on.
- Clean separation of `SubscriptionPlan` (catalog) vs. `Subscription` (record), with history preserved (no deletion on cancel).
- Cancellation-until-period-end semantics work correctly and match their own documented behavior.
- Existing tests for the manual flow pass cleanly (6/6).
- No hard-coded payment secrets anywhere, since no payment secrets exist yet.
- The schema has no Apple/Google-specific baggage to work around — it's a genuinely clean slate for additive Stripe fields.

### Missing or incomplete behavior
- No Apple, Google, or Stripe integration of any kind.
- No webhook infrastructure at all.
- Subscription expiration is never actively reconciled (`expire()` is dead code) — dynamic checks mask this for access control, but stored fields (`paid_user`, `Subscription.status`) go stale.
- No atomicity/locking around subscription creation — a real race condition exists.
- `IsSubscribedBarber` and per-plan feature limits (`max_employees`, `has_ai_recommendations`, etc.) are defined but never enforced.
- Landing page pricing/checkout UI is entirely static and disconnected from the backend; no router, no API client, no auth.
- Admin dashboard subscription display is 100% mock data, not live.

### Security findings
- **Critical:** none (no real payment processor exists to compromise).
- **High:** unverified self-service entitlement grant via `subscribe/` — must be closed off once a real processor exists, so it can't be used to bypass Stripe payment.
- **Medium:** subscription-creation race condition (no atomic/locking).
- **Low:** dead permission-class wiring (`IsSubscribedBarber` unused), stale `paid_user`/`status` fields after natural expiry.

### Stripe readiness
💡 The current architecture can support Stripe **additively** — new fields, new endpoints, new webhook handler, no restructuring of the existing manual flow or its data required, provided the platform-discriminator field and idempotency/locking gaps (§12) are addressed as part of (or just before) the Stripe work.

### Expected Stripe impact
See §19 for the full file-by-file list; in short: `Apps/subscriptions/{models,serializers,views,urls,admin}.py` + new migration + new webhook/service module on the backend; `Plans.jsx` + a new router + new success/cancel pages + a new API client on the landing page; new env vars + a new public webhook route in deployment.

### Backward-compatibility risks
Adding required non-nullable Stripe-specific fields to `Subscription` without defaults would break the existing manual `Subscription.objects.create(...)` call; refactoring `activate()`/`cancel()`/`expire()` signatures without updating the existing manual call site would break it too. Otherwise, additive changes carry low risk since there is no live Apple/Google behavior to disturb.

### Open decisions required from the product owner
See the numbered list in §21.
