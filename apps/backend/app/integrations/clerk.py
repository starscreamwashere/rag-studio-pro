"""Minimal Clerk Backend API client.

Session tokens don't carry the user's email by default, so we fetch profile
details from Clerk's Backend API when provisioning the local user record.
"""

import httpx

from app.core.config import settings

CLERK_API_BASE = "https://api.clerk.com/v1"


class ClerkUser:
    def __init__(self, clerk_user_id: str, email: str, full_name: str | None):
        self.clerk_user_id = clerk_user_id
        self.email = email
        self.full_name = full_name


async def fetch_clerk_user(clerk_user_id: str) -> ClerkUser:
    """Look up a Clerk user's primary email and name."""
    headers = {"Authorization": f"Bearer {settings.clerk_secret_key}"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{CLERK_API_BASE}/users/{clerk_user_id}", headers=headers)
        resp.raise_for_status()
        data = resp.json()

    primary_id = data.get("primary_email_address_id")
    email = ""
    for entry in data.get("email_addresses", []):
        if entry.get("id") == primary_id:
            email = entry.get("email_address", "")
            break
    if not email and data.get("email_addresses"):
        email = data["email_addresses"][0].get("email_address", "")

    first = data.get("first_name") or ""
    last = data.get("last_name") or ""
    full_name = f"{first} {last}".strip() or None

    return ClerkUser(clerk_user_id=clerk_user_id, email=email, full_name=full_name)
