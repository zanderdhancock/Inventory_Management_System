from datetime import datetime
from zoneinfo import ZoneInfo

from options import LEGACY_SUBTEAMS


DISPLAY_TIMEZONE = ZoneInfo("America/Chicago")

FIELD_LABELS = {
    "name": "name",
    "category": "category",
    "subsystem": "subteam",
    "location": "location",
    "quantity": "quantity",
    "type": "type",
    "status": "status",
    "notes": "notes",
    "minimum_quantity": "minimum",
    "project": "project",
    "condition": "condition",
    "last_maintenance": "last maintenance",
    "maintenance_notes": "maintenance notes"
}

# Columns added by supabase/2026-10-05_demo_features.sql.
EXTENDED_FIELDS = [
    "minimum_quantity",
    "project",
    "condition",
    "last_maintenance",
    "maintenance_notes"
]

REQUIRED_FIELDS = {
    "category": "Category",
    "subsystem": "Subteam",
    "location": "Location",
    "type": "Type",
    "status": "Status"
}


def search_inventory(items, search):
    if not search:
        return items

    search = search.lower()

    return [
        item for item in items
        if search in str(item["name"]).lower()
        or search in str(item["category"]).lower()
        or search in str(item["subsystem"]).lower()
        or search in str(item["location"]).lower()
    ]


def filter_inventory(
    items,
    category_filter,
    subsystem_filter,
    location_filter,
    status_filter="All",
    project_filter="All"
):
    if category_filter != "All":
        items = [
            item for item in items
            if item["category"] == category_filter
        ]

    if subsystem_filter != "All":
        items = [
            item for item in items
            if item["subsystem"] == subsystem_filter
        ]

    if location_filter != "All":
        items = [
            item for item in items
            if item["location"] == location_filter
        ]

    if status_filter != "All":
        items = [
            item for item in items
            if item["status"] == status_filter
        ]

    if project_filter != "All":
        items = [
            item for item in items
            if (item.get("project") or UNASSIGNED) == project_filter
        ]

    return items


def get_filter_options(items):
    categories = ["All"] + sorted(
        set(item["category"] for item in items if item["category"])
    )

    subsystems = ["All"] + sorted(
        set(item["subsystem"] for item in items if item["subsystem"])
    )

    locations = ["All"] + sorted(
        set(item["location"] for item in items if item["location"])
    )

    return categories, subsystems, locations


def apply_subteams(items):
    """Show rows still carrying an old subsystem under its new subteam."""
    return [
        {
            **item,
            "subsystem": LEGACY_SUBTEAMS.get(
                item["subsystem"],
                item["subsystem"]
            )
        }
        for item in items
    ]


UNASSIGNED = "Unassigned"


def auto_status(item):
    """Low/Out follow the minimum quantity when one is set.

    "In Use" is always a manual choice and is left alone.
    """
    minimum = item.get("minimum_quantity")
    status = item["status"]

    if minimum is None or status == "In Use":
        return status

    if item["quantity"] == 0:
        return "Out"

    if item["quantity"] <= minimum:
        return "Low"

    if status in ("Low", "Out"):
        return "Available"

    return status


def summarize_projects(items, projects):
    """Item count, units and low/out count per project, in list order."""
    names = list(projects)

    for item in items:
        project = item.get("project")

        if project and project not in names:
            names.append(project)

    names.append(UNASSIGNED)

    summary = []

    for name in names:
        members = [
            item for item in items
            if (item.get("project") or UNASSIGNED) == name
        ]

        if name == UNASSIGNED and not members:
            continue

        summary.append({
            "project": name,
            "items": len(members),
            "units": sum(int(item["quantity"] or 0) for item in members),
            "attention": sum(
                1 for item in members
                if item["status"] in ("Low", "Out")
            )
        })

    return summary


def count_usage(items, field, value):
    return sum(1 for item in items if item.get(field) == value)


def option_index(options, value):
    # Stored values that are no longer valid options (for example an old
    # subsystem name) leave the selectbox empty instead of crashing.
    if value in options:
        return options.index(value)

    return None


def validate_item(item):
    if not item["name"]:
        return "Item name is required."

    for field, label in REQUIRED_FIELDS.items():
        if not item.get(field):
            return f"{label} is required."

    return None


def _normalize(value):
    if value is None:
        return ""

    return value


def get_change_summary(old_item, updated_data):
    changes = []

    for field, new_value in updated_data.items():
        old_value = old_item.get(field)

        if _normalize(old_value) != _normalize(new_value):
            label = FIELD_LABELS.get(field, field)
            changes.append(
                f"{label}: {_normalize(old_value)} → {_normalize(new_value)}"
            )

    return ", ".join(changes)


def find_duplicate_item(items, new_item, exclude_id=None):
    new_name = new_item["name"].strip().lower()
    new_location = new_item["location"].strip().lower()

    for item in items:
        if exclude_id is not None and item["id"] == exclude_id:
            continue

        existing_name = str(item["name"]).strip().lower()
        existing_location = str(item["location"]).strip().lower()

        if (
            existing_name == new_name
            and existing_location == new_location
        ):
            return item

    return None


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

def parse_timestamp(value):
    if not value:
        return None

    try:
        timestamp = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except ValueError:
        return None

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=ZoneInfo("UTC"))

    return timestamp.astimezone(DISPLAY_TIMEZONE)


def format_timestamp(value):
    timestamp = parse_timestamp(value)

    if not timestamp:
        return ""

    return timestamp.strftime("%b %d, %Y %I:%M %p")


def filter_history(
    history,
    members=None,
    actions=None,
    search="",
    start_date=None,
    end_date=None,
    item_id=None
):
    results = []
    search = (search or "").strip().lower()

    for entry in history:
        if item_id is not None and entry["item_id"] != item_id:
            continue

        if members and entry["member"] not in members:
            continue

        if actions and entry["action"] not in actions:
            continue

        if search and not (
            search in str(entry["item_name"]).lower()
            or search in str(entry["details"] or "").lower()
        ):
            continue

        if start_date or end_date:
            timestamp = parse_timestamp(entry["created_at"])

            if not timestamp:
                continue

            if start_date and timestamp.date() < start_date:
                continue

            if end_date and timestamp.date() > end_date:
                continue

        results.append(entry)

    return results
