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
    location_filter
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

def get_change_summary(old_item, updated_data):
    changes = []

    for field, new_value in updated_data.items():
        old_value = old_item.get(field)

        if old_value != new_value:
            changes.append(
                f"{field}: {old_value} → {new_value}"
            )

    return ", ".join(changes)

def find_duplicate_item(items, new_item):
    new_name = new_item["name"].strip().lower()
    new_location = new_item["location"].strip().lower()

    for item in items:
        existing_name = str(item["name"]).strip().lower()
        existing_location = str(item["location"]).strip().lower()

        if (
            existing_name == new_name
            and existing_location == new_location
        ):
            return item

    return None