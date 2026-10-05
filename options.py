# Defaults for every list. Members, locations, categories, subteams and
# projects can be edited on the Admin tab once the inventory_options table
# exists; until then these defaults are used.

CATEGORIES = [
    "Fasteners",
    "Electronics",
    "Connectors",
    "Sensors",
    "Motors/Thrusters",
    "Raw Materials",
    "Tools",
    "Waterproofing",
    "Fabricated Parts",
    "Misc."
]

# Stored in the inventory_items.subsystem column.
SUBTEAMS = [
    "F-P",
    "EPS",
    "TMS",
    "GNC",
    "C-C"
]

# Old subsystem names still stored on existing rows, and the subteam each
# one now belongs to. Rows without a match keep their value until edited.
LEGACY_SUBTEAMS = {
    "Mechanical": "F-P",
    "Propulsion": "F-P",
    "Manipulator": "F-P",
    "Waterproofing": "F-P",
    "Electrical": "EPS",
    "Tether": "TMS",
    "Controls": "GNC",
    "Cameras/Sensors": "C-C"
}

ITEM_TYPES = [
    "Asset",
    "Consumable"
]

STATUSES = [
    "Available",
    "Low",
    "Out",
    "In Use"
]

LOCATIONS = [
    "Member A",
    "Member B",
    "Member C",
    "Member D",
    "Club Storage"
]

MEMBERS = [
    "Member A",
    "Member B",
    "Member C",
    "Member D"
]

PROJECTS = [
    "ROV build",
    "Competition",
    "Pool testing",
    "Training",
    "Spares"
]



# --------------------------------------------------
# EDITABLE LISTS
# --------------------------------------------------

EDITABLE_LISTS = {
    "members": "Members",
    "locations": "Locations",
    "categories": "Categories",
    "subteams": "Subteams",
    "projects": "Projects"
}

# The inventory_items column each list's values are stored in.
LIST_FIELDS = {
    "locations": "location",
    "categories": "category",
    "subteams": "subsystem",
    "projects": "project"
}

DEFAULTS = {
    "members": MEMBERS,
    "locations": LOCATIONS,
    "categories": CATEGORIES,
    "subteams": SUBTEAMS,
    "projects": PROJECTS
}

_active = {name: list(values) for name, values in DEFAULTS.items()}


def load(rows):
    """Replace defaults with lists stored in Supabase, where present."""
    stored = {}

    for row in sorted(rows or [], key=lambda r: (r["position"], r["value"])):
        stored.setdefault(row["list_name"], []).append(row["value"])

    for name, defaults in DEFAULTS.items():
        _active[name] = stored.get(name) or list(defaults)


def get(name):
    return _active[name]
