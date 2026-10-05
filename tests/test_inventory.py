from datetime import date

from inventory import (
    search_inventory,
    filter_inventory,
    get_change_summary,
    find_duplicate_item,
    option_index,
    validate_item,
    filter_history,
    format_timestamp,
    apply_subteams
)


ITEMS = [
    {
        "id": 1, "name": "T200 Thruster", "category": "Motors/Thrusters",
        "subsystem": "F-P", "location": "Member A", "quantity": 4,
        "type": "Asset", "status": "Available", "notes": None
    },
    {
        "id": 2, "name": "O-Ring Set", "category": "Waterproofing",
        "subsystem": "TMS", "location": "Club Storage", "quantity": 1,
        "type": "Consumable", "status": "Low", "notes": "Size 12"
    }
]

HISTORY = [
    {"item_id": 1, "item_name": "T200 Thruster", "action": "EDIT",
     "member": "Member A", "details": "quantity: 3 → 4",
     "created_at": "2026-09-29T15:42:00+00:00"},
    {"item_id": 2, "item_name": "O-Ring Set", "action": "ADD",
     "member": "Member B", "details": "Added 1 at Club Storage",
     "created_at": "2026-09-28T21:15:00+00:00"},
    {"item_id": 3, "item_name": "Depth Sensor", "action": "DELETE",
     "member": "Member A", "details": None,
     "created_at": "2026-09-27T14:20:00+00:00"}
]


def test_search_matches_name_and_subteam():
    assert [i["id"] for i in search_inventory(ITEMS, "thruster")] == [1]
    assert [i["id"] for i in search_inventory(ITEMS, "tms")] == [2]


def test_filter_by_subteam_and_status():
    assert filter_inventory(ITEMS, "All", "F-P", "All") == [ITEMS[0]]
    assert filter_inventory(ITEMS, "All", "All", "All", "Low") == [ITEMS[1]]


def test_change_summary_ignores_none_vs_empty_notes():
    updated = {**ITEMS[0], "notes": ""}
    del updated["id"]
    assert get_change_summary(ITEMS[0], updated) == ""


def test_change_summary_labels_subteam():
    summary = get_change_summary(ITEMS[0], {"subsystem": "EPS"})
    assert summary == "subteam: F-P → EPS"


def test_duplicate_is_case_insensitive():
    new = {"name": " t200 thruster ", "location": "member a"}
    assert find_duplicate_item(ITEMS, new)["id"] == 1


def test_duplicate_check_skips_item_being_edited():
    edited = {"name": "T200 Thruster", "location": "Member A"}
    assert find_duplicate_item(ITEMS, edited, exclude_id=1) is None


def test_option_index_tolerates_unknown_values():
    assert option_index(["F-P", "EPS"], "EPS") == 1
    assert option_index(["F-P", "EPS"], "Propulsion") is None


def test_validate_item_requires_subteam():
    item = {**ITEMS[0], "subsystem": None}
    assert validate_item(item) == "Subteam is required."
    assert validate_item({**ITEMS[0], "name": ""}) == "Item name is required."
    assert validate_item(ITEMS[0]) is None


def test_filter_history_by_member_action_and_search():
    assert len(filter_history(HISTORY, members=["Member A"])) == 2
    assert len(filter_history(HISTORY, actions=["DELETE"])) == 1
    assert len(filter_history(HISTORY, search="club storage")) == 1
    assert len(filter_history(HISTORY, item_id=2)) == 1


def test_filter_history_by_local_date():
    # 21:15 UTC on Sep 28 is still Sep 28 in Central time.
    results = filter_history(
        HISTORY,
        start_date=date(2026, 9, 28),
        end_date=date(2026, 9, 28)
    )
    assert [e["item_name"] for e in results] == ["O-Ring Set"]


def test_format_timestamp_uses_central_time():
    assert format_timestamp("2026-09-29T15:42:00+00:00") == "Sep 29, 2026 10:42 AM"


def test_apply_subteams_maps_old_subsystems():
    items = [
        {**ITEMS[0], "subsystem": "Propulsion"},
        {**ITEMS[1], "subsystem": "General"}
    ]
    assert [i["subsystem"] for i in apply_subteams(items)] == ["F-P", "General"]
    # The stored rows are left untouched.
    assert items[0]["subsystem"] == "Propulsion"
