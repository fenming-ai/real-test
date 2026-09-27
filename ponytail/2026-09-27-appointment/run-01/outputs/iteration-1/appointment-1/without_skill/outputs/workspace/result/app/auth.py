"""Synthetic identities for this local fixture only."""
ACTORS = {
    "north-organizer": {"tenant_id": "north", "role": "organizer"},
    "south-organizer": {"tenant_id": "south", "role": "organizer"},
    "north-viewer": {"tenant_id": "north", "role": "viewer"},
}


def authenticate(headers):
    token = headers.get("Authorization", "").removeprefix("Bearer ")
    if token not in ACTORS:
        raise PermissionError("Please select a valid account")
    return ACTORS[token]


def require_organizer(actor):
    if actor["role"] != "organizer":
        raise PermissionError("Organizer access required")
