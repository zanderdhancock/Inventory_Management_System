import base64
import csv
import io

import pandas as pd
import streamlit as st

from options import (
    CATEGORIES,
    SUBTEAMS,
    ITEM_TYPES,
    STATUSES,
    LOCATIONS
)

from inventory import (
    option_index,
    format_timestamp,
    filter_history
)


# (text, background) per status, for the table and summary dots.
STATUS_COLORS = {
    "Available": ("#62D6A2", "rgba(98, 214, 162, 0.12)"),
    "Low": ("#F3C55C", "rgba(243, 197, 92, 0.14)"),
    "Out": ("#FF8A80", "rgba(255, 138, 128, 0.14)"),
    "In Use": ("#7CC6FF", "rgba(124, 198, 255, 0.13)")
}

_LOGO = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none">'
    '<circle cx="16" cy="16" r="15" fill="#1C7DB8"/>'
    '<path d="M5 17.5c2.2 0 2.2-2 4.4-2s2.2 2 4.4 2 2.2-2 4.4-2 2.2 2 4.4 2 2.2-2 4.4-2" '
    'stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>'
    '<path d="M8 22c1.6 0 1.6-1.4 3.2-1.4s1.6 1.4 3.2 1.4 1.6-1.4 3.2-1.4 1.6 1.4 3.2 1.4 1.6-1.4 3.2-1.4" '
    'stroke="#8EC5F0" stroke-width="1.6" stroke-linecap="round"/>'
    '<circle cx="16" cy="10" r="2.2" fill="#FFFFFF"/>'
    '</svg>'
)

# st.html strips inline <svg>, so the logo goes in as an image.
LOGO_SVG = (
    '<img class="logo" alt="" src="data:image/svg+xml;base64,'
    + base64.b64encode(_LOGO.encode()).decode()
    + '">'
)

ACTION_LABELS = {
    "ADD": "Added",
    "EDIT": "Edited",
    "DELETE": "Deleted"
}

FILTER_KEYS = [
    "filter_category",
    "filter_subteam",
    "filter_location",
    "filter_status"
]


# --------------------------------------------------
# HEADER
# --------------------------------------------------

def display_topbar():
    st.html(
        f"""
        <div class="topbar">
            <div class="topbar-inner">
                {LOGO_SVG}
                <span class="brand-name">Oceanus</span>
                <span class="brand-divider"></span>
                <span class="brand-product">Inventory</span>
            </div>
        </div>
        """
    )


def display_header(members):
    display_topbar()

    col1, col2 = st.columns(
        [3, 1.4],
        vertical_alignment="bottom"
    )

    with col1:
        st.html(
            """
            <div class="page-heading">
                <div class="page-title">Team inventory</div>
                <div class="page-subtitle">
                    Parts, tools and materials across Oceanus subteams
                </div>
            </div>
            """
        )

    with col2:
        return st.selectbox(
            "Making changes as",
            members,
            index=None,
            placeholder="Choose your name",
            key="current_member"
        )


def display_summary(items):
    total_quantity = sum(
        int(item["quantity"])
        for item in items
        if item["quantity"] is not None
    )

    def count(status):
        return sum(1 for item in items if item["status"] == status)

    stats = [
        ("Items", len(items), None),
        ("Total units", total_quantity, None),
        ("Low stock", count("Low"), "Low"),
        ("Out of stock", count("Out"), "Out"),
        ("In use", count("In Use"), "In Use")
    ]

    cells = ""

    for label, value, status in stats:
        dot = ""

        if status:
            dot = (
                f'<span class="dot" '
                f'style="background:{STATUS_COLORS[status][0]}"></span>'
            )

        cells += f"""
            <div class="stat">
                <div class="stat-label">{dot}{label}</div>
                <div class="stat-value">{value}</div>
            </div>
        """

    st.html(f'<div class="stats">{cells}</div>')


# --------------------------------------------------
# SEARCH / FILTERS
# --------------------------------------------------

def clear_filters():
    st.session_state.inventory_search = ""

    for key in FILTER_KEYS:
        st.session_state[key] = "All"


def filters_active():
    if st.session_state.get("inventory_search"):
        return True

    return any(
        st.session_state.get(key, "All") != "All"
        for key in FILTER_KEYS
    )


def _active_filter_count():
    return sum(
        1
        for key in FILTER_KEYS
        if st.session_state.get(key, "All") != "All"
    )


def display_toolbar(can_edit, categories, subteams, locations):
    """Search, filters and Add item on one row."""
    col1, col2, col3 = st.columns(
        [6, 1.3, 1.3],
        gap="small",
        vertical_alignment="bottom"
    )

    with col1:
        search = st.text_input(
            "Search",
            placeholder="Search by item, category, subteam, or location",
            key="inventory_search",
            label_visibility="collapsed"
        )

    with col2:
        active = _active_filter_count()
        label = f"Filters · {active}" if active else "Filters"

        with st.popover(label, icon=":material/filter_list:", width="stretch"):
            category = st.selectbox(
                "Category",
                categories,
                key="filter_category"
            )

            subteam = st.selectbox(
                "Subteam",
                subteams,
                key="filter_subteam"
            )

            location = st.selectbox(
                "Location",
                locations,
                key="filter_location"
            )

            status = st.selectbox(
                "Status",
                ["All"] + STATUSES,
                key="filter_status"
            )

            st.button(
                "Clear filters",
                on_click=clear_filters,
                disabled=not filters_active(),
                type="tertiary"
            )

    with col3:
        add_clicked = st.button(
            "Add item",
            icon=":material/add:",
            type="primary",
            disabled=not can_edit,
            help=None if can_edit else "Choose your name first",
            width="stretch"
        )

    return search, (category, subteam, location, status), add_clicked


# --------------------------------------------------
# INVENTORY LIST
# --------------------------------------------------

def _status_style(value):
    colors = STATUS_COLORS.get(value)

    if not colors:
        return ""

    text, background = colors

    return (
        f"color: {text}; background-color: {background}; "
        "font-weight: 500;"
    )


def display_inventory(items, table_key):
    """Show the inventory table and return the row the user selected."""
    if not items:
        st.info("No items match your search and filters.")
        return None

    table = pd.DataFrame([
        {
            "Item": item["name"],
            "Qty": item["quantity"],
            "Status": item["status"],
            "Location": item["location"],
            "Subteam": item["subsystem"],
            "Category": item["category"],
            "Type": item["type"],
            "Notes": item["notes"] or ""
        }
        for item in items
    ])

    event = st.dataframe(
        table.style.map(_status_style, subset=["Status"]),
        width="stretch",
        hide_index=True,
        key=table_key,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "Item": st.column_config.TextColumn("Item", width="medium"),
            "Qty": st.column_config.NumberColumn("Qty", width="small", format="%d"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Notes": st.column_config.TextColumn("Notes", width="large")
        }
    )

    rows = event.selection.rows

    # A stale selection can point past the end after filters change.
    if not rows or rows[0] >= len(items):
        return None

    return items[rows[0]]


def display_selection_bar(selected_item, can_edit, shown, total):
    """Sits above the table. Returns the action the user clicked, if any."""
    with st.container(border=True, key="selection_bar"):
        if not selected_item:
            col1, col2 = st.columns([3, 1], vertical_alignment="center")

            with col1:
                if can_edit:
                    st.markdown(
                        "Click a row's checkbox to edit, delete, "
                        "or see its history."
                    )
                else:
                    st.markdown(
                        "Choose your name at the top to add, edit, "
                        "or delete items."
                    )

            with col2:
                st.html(
                    f'<div class="row-count">{shown} of {total} items</div>'
                )

            return None

        col1, col2, col3, col4 = st.columns(
            [4, 1, 1, 1],
            gap="small",
            vertical_alignment="center"
        )

        with col1:
            st.markdown(
                f"**{selected_item['name']}** · "
                f"{selected_item['location']} · "
                f"qty {selected_item['quantity']}"
            )

        with col2:
            if st.button(
                "Edit",
                icon=":material/edit:",
                type="primary",
                disabled=not can_edit,
                width="stretch"
            ):
                return "edit"

        with col3:
            if st.button(
                "Delete",
                icon=":material/delete:",
                disabled=not can_edit,
                width="stretch"
            ):
                return "delete"

        with col4:
            if st.button(
                "History",
                icon=":material/history:",
                width="stretch"
            ):
                return "history"

    return None


# --------------------------------------------------
# ITEM MODALS
# --------------------------------------------------

def _item_fields(item=None):
    item = item or {}

    name = st.text_input(
        "Item name",
        value=item.get("name", "")
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "Category",
            CATEGORIES,
            index=option_index(CATEGORIES, item.get("category")),
            placeholder="Select a category"
        )

        location = st.selectbox(
            "Location",
            LOCATIONS,
            index=option_index(LOCATIONS, item.get("location")),
            placeholder="Select a location"
        )

        status = st.selectbox(
            "Status",
            STATUSES,
            index=option_index(STATUSES, item.get("status", STATUSES[0]))
        )

    with col2:
        subteam = st.selectbox(
            "Subteam",
            SUBTEAMS,
            index=option_index(SUBTEAMS, item.get("subsystem")),
            placeholder="Select a subteam"
        )

        item_type = st.selectbox(
            "Type",
            ITEM_TYPES,
            index=option_index(ITEM_TYPES, item.get("type", ITEM_TYPES[0]))
        )

        quantity = st.number_input(
            "Quantity",
            min_value=0,
            value=int(item.get("quantity") or 0),
            step=1
        )

    notes = st.text_area(
        "Notes",
        value=item.get("notes") or "",
        max_chars=500
    )

    return {
        "name": name.strip(),
        "category": category,
        "subsystem": subteam,
        "location": location,
        "quantity": int(quantity),
        "type": item_type,
        "status": status,
        "notes": notes.strip()
    }


def _submit_buttons(label, danger=False):
    col1, col2 = st.columns(2)

    with col1:
        cancelled = st.form_submit_button(
            "Cancel",
            width="stretch"
        )

    with col2:
        submitted = st.form_submit_button(
            label,
            type="secondary" if danger else "primary",
            width="stretch"
        )

    return submitted, cancelled


def _finish(error):
    if error:
        st.error(error)
    else:
        st.rerun()


@st.dialog("Add item", width="medium")
def add_item_dialog(on_save):
    with st.form("add_item_form", border=False):
        item = _item_fields()
        submitted, cancelled = _submit_buttons("Add item")

    if cancelled:
        st.rerun()

    if submitted:
        _finish(on_save(item))


@st.dialog("Edit item", width="medium")
def edit_item_dialog(item, on_save):
    if item["subsystem"] not in SUBTEAMS:
        st.info(
            f"This item is still filed under \"{item['subsystem']}\". "
            "Pick its subteam before saving."
        )

    with st.form("edit_item_form", border=False):
        updated = _item_fields(item)
        submitted, cancelled = _submit_buttons("Save changes")

    if cancelled:
        st.rerun()

    if submitted:
        _finish(on_save(item, updated))


@st.dialog("Delete item", width="small")
def delete_item_dialog(item, on_delete):
    st.markdown(
        f"Delete **{item['name']}** "
        f"({item['quantity']} at {item['location']})?"
    )

    st.caption(
        "It disappears from the inventory list. "
        "Its history stays in the Activity tab."
    )

    with st.form("delete_item_form", border=False):
        confirm = st.checkbox(
            "Yes, delete this item"
        )
        submitted, cancelled = _submit_buttons("Delete", danger=True)

    if cancelled:
        st.rerun()

    if submitted:
        if not confirm:
            st.warning("Tick the box to confirm.")
        else:
            _finish(on_delete(item))


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

def _history_csv(entries):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Time", "Action", "Item", "Member", "Details"])

    for entry in entries:
        writer.writerow([
            format_timestamp(entry["created_at"]),
            entry["action"],
            entry["item_name"],
            entry["member"],
            entry["details"] or ""
        ])

    return buffer.getvalue()


def display_history(history, item=None, key="history"):
    if not history:
        st.info("No inventory activity recorded yet.")
        return

    members = sorted(
        set(entry["member"] for entry in history if entry["member"])
    )

    cols = st.columns(
        [3, 2, 2, 2],
        gap="small",
        vertical_alignment="bottom"
    )

    with cols[0]:
        search = st.text_input(
            "Search",
            placeholder="Item name or change details",
            key=f"{key}_search"
        )

    with cols[1]:
        member_filter = st.multiselect(
            "Member",
            members,
            placeholder="Anyone",
            key=f"{key}_members"
        )

    with cols[2]:
        action_filter = st.multiselect(
            "Action",
            list(ACTION_LABELS),
            format_func=ACTION_LABELS.get,
            placeholder="Any",
            key=f"{key}_actions"
        )

    with cols[3]:
        date_range = st.date_input(
            "Dates",
            value=[],
            format="MM/DD/YYYY",
            key=f"{key}_dates"
        )

    start_date = date_range[0] if len(date_range) > 0 else None
    end_date = date_range[1] if len(date_range) > 1 else start_date

    entries = filter_history(
        history,
        members=member_filter,
        actions=action_filter,
        search=search,
        start_date=start_date,
        end_date=end_date,
        item_id=item["id"] if item else None
    )

    if not entries:
        st.info("No activity matches these filters.")
        return

    st.dataframe(
        [
            {
                "When": format_timestamp(entry["created_at"]),
                "Item": entry["item_name"],
                "Action": ACTION_LABELS.get(entry["action"], entry["action"]),
                "By": entry["member"],
                "Details": entry["details"] or ""
            }
            for entry in entries
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "When": st.column_config.TextColumn("When", width="medium"),
            "Action": st.column_config.TextColumn("Action", width="small"),
            "Details": st.column_config.TextColumn("Details", width="large")
        }
    )

    col1, col2 = st.columns([3, 1], vertical_alignment="center")

    with col1:
        st.caption(f"{len(entries)} of {len(history)} records")

    with col2:
        st.download_button(
            "Export CSV",
            data=_history_csv(entries),
            file_name="oceanus_inventory_history.csv",
            mime="text/csv",
            icon=":material/download:",
            type="tertiary",
            key=f"{key}_export",
            width="stretch"
        )


@st.dialog("Item history", width="large")
def item_history_dialog(history, item):
    st.markdown(f"**{item['name']}** · {item['location']}")
    display_history(history, item=item, key="item_history")
