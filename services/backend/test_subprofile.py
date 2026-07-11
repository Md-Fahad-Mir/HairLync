"""
Test Script: Sub-Profile (Salon Employee) Creation Flow
========================================================
API Base: http://127.0.0.1:8000/api/v1/

Steps:
  1. Create verified salon owner directly in DB (bypasses OTP email)
  2. Login via  POST /api/v1/auth/login/
  3. Create salon profile via POST /api/v1/profiles/salon/
  4. Create sub-profile employee via POST /api/v1/profiles/salon/employees/
  5. List employees via GET /api/v1/profiles/salon/employees/
  6. Login as the auto-generated employee to confirm credentials work
"""
import os
import sys
import django
import json
import requests

# --- Django setup so we can use the ORM directly ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from Apps.profiles.models import SalonProfile

User = get_user_model()

BASE = "http://127.0.0.1:8000/api/v1"
SALON_EMAIL    = "testsalon_owner@hairlync.test"
SALON_PASSWORD = "TestSalon@2024"


def pretty(data):
    print(json.dumps(data, indent=4))


def section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# ──────────────────────────────────────────────────────────────
# STEP 1: Create Salon Owner directly in DB (skip OTP email)
# ──────────────────────────────────────────────────────────────
section("STEP 1 — Create salon owner in DB (bypass OTP)")

User.objects.filter(email=SALON_EMAIL).delete()

salon_owner = User.objects.create_user(
    email=SALON_EMAIL,
    password=SALON_PASSWORD,
    full_name="Glamour Salon",
    role="salon",
    is_active=True,
    is_verified=True,
    is_sub_profile=False,
)
print(f"  ✅ id={salon_owner.id}  email={salon_owner.email}")
print(f"     role={salon_owner.role}  is_sub_profile={salon_owner.is_sub_profile}")


# ──────────────────────────────────────────────────────────────
# STEP 2: Login → get JWT access token
# ──────────────────────────────────────────────────────────────
section("STEP 2 — POST /api/v1/auth/login/")

resp = requests.post(f"{BASE}/auth/login/", json={
    "email": SALON_EMAIL,
    "password": SALON_PASSWORD,
})
print(f"  HTTP {resp.status_code}")
login_data = resp.json()
pretty(login_data)

assert resp.status_code == 200, "Login failed"
access_token = login_data["access"]
AUTH = {"Authorization": f"Bearer {access_token}"}
print(f"\n  ✅ JWT token acquired.")


# ──────────────────────────────────────────────────────────────
# STEP 3: Create Salon Profile
# ──────────────────────────────────────────────────────────────
section("STEP 3 — POST /api/v1/profiles/salon/")

resp = requests.post(f"{BASE}/profiles/salon/", headers=AUTH, json={
    "business_name": "Glamour Hair Salon",
    "bio": "Premium hair care for every style and texture.",
    "city": "New York",
    "address": "123 Fifth Ave, New York, NY 10001",
    "phone_number": "+1-212-555-0199",
    "experience_years": 7,
    "experience_range": "5-10",
})
print(f"  HTTP {resp.status_code}")
pretty(resp.json())
assert resp.status_code in (200, 201), "Salon profile creation failed"
print("  ✅ Salon profile created.")


# ──────────────────────────────────────────────────────────────
# STEP 4: Create Sub-Profile Employee  ← MAIN GOAL
# ──────────────────────────────────────────────────────────────
section("STEP 4 — POST /api/v1/profiles/salon/employees/  (CREATE SUB-PROFILE)")

employee_request_body = {
    "full_name": "Maria Johnson",
    "position": "Senior Hair Stylist",
    "role_title": "Hair Stylist",
}
print(f"\n  REQUEST BODY:")
pretty(employee_request_body)

resp = requests.post(f"{BASE}/profiles/salon/employees/", headers=AUTH, json=employee_request_body)
print(f"\n  HTTP {resp.status_code}")
emp_data = resp.json()
pretty(emp_data)
assert resp.status_code in (200, 201), "Sub-profile creation failed"
print("  ✅ Sub-profile employee created.")

emp = emp_data.get("data", {})
gen_email    = emp.get("generated_email")
gen_password = emp.get("generated_password")


# ──────────────────────────────────────────────────────────────
# STEP 5: List all Employees
# ──────────────────────────────────────────────────────────────
section("STEP 5 — GET /api/v1/profiles/salon/employees/  (LIST)")

resp = requests.get(f"{BASE}/profiles/salon/employees/", headers=AUTH)
print(f"  HTTP {resp.status_code}")
pretty(resp.json())


# ──────────────────────────────────────────────────────────────
# STEP 6: Employee logs in with auto-generated credentials
# ──────────────────────────────────────────────────────────────
section("STEP 6 — POST /api/v1/auth/login/  (EMPLOYEE LOGIN TEST)")

print(f"  Employee email    : {gen_email}")
print(f"  Employee password : {gen_password}\n")

resp = requests.post(f"{BASE}/auth/login/", json={
    "email": gen_email,
    "password": gen_password,
})
print(f"  HTTP {resp.status_code}")
pretty(resp.json())

if resp.status_code == 200:
    print("\n  ✅ Employee can log in with auto-generated credentials!")
else:
    print("\n  ❌ Employee login failed.")


# ──────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ──────────────────────────────────────────────────────────────
section("FINAL SUMMARY — CREDENTIALS")
print(f"""
  ┌─ SALON OWNER ──────────────────────────────────────────┐
  │  Email    : {SALON_EMAIL:<40} │
  │  Password : {SALON_PASSWORD:<40} │
  └────────────────────────────────────────────────────────┘

  ┌─ SUB-PROFILE EMPLOYEE (auto-generated) ────────────────┐
  │  Email    : {str(gen_email):<40} │
  │  Password : {str(gen_password):<40} │
  └────────────────────────────────────────────────────────┘
""")
