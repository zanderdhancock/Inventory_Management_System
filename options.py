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