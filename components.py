import base64
from html import escape
import csv
import io

import pandas as pd
import streamlit as st

import options

from options import (
    ITEM_TYPES,
    STATUSES,
    EDITABLE_LISTS,
    LIST_FIELDS
)

from inventory import (
    UNASSIGNED,
    option_index,
    format_timestamp,
    filter_history,
    summarize_projects,
    count_usage,
    FIELD_LABELS,
    REQUIRED_FIELDS
)


# Set by main.py once it knows whether the extra columns exist in Supabase.
FEATURES = {"extended": False}


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
    "filter_project"
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


# The status filter's value lives in st.session_state.status_choice. Tiles
# change it and bump status_version, which gives the segmented control a
# fresh key so it picks the new value up.
def _show_status(status):
    st.session_state.status_choice = status or "All"
    st.session_state.status_version = st.session_state.get("status_version", 0) + 1


def _status_changed(key):
    st.session_state.status_choice = st.session_state.get(key) or "All"


def display_summary(items):
    """Summary tiles. Clicking one filters the inventory table."""
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

    with st.container(key="stats"):
        columns = st.columns(len(stats), gap="small")

        for column, (label, value, status) in zip(columns, stats):
            dot = ""

            if status:
                dot = (
                    f'<span class="dot" '
                    f'style="background:{STATUS_COLORS[status][0]}"></span>'
                )

            active = (
                status is not None
                and st.session_state.get("status_choice") == status
            )

            with column, st.container(key=f"tile_{label.replace(' ', '_')}"):
                st.html(
                    f"""
                    <div class="stat{' stat-active' if active else ''}">
                        <div class="stat-label">{dot}{label}</div>
                        <div class="stat-value">{value}</div>
                    </div>
                    """
                )

                st.button(
                    f"Show {label.lower()}",
                    key=f"stat_button_{label}",
                    on_click=_show_status,
                    args=(status,)
                )


# --------------------------------------------------
# SEARCH / FILTERS
# --------------------------------------------------

def clear_filters():
    st.session_state.inventory_search = ""

    for key in FILTER_KEYS:
        st.session_state[key] = "All"

    _show_status("All")


def filters_active():
    if st.session_state.get("inventory_search"):
        return True

    if st.session_state.get("status_choice", "All") != "All":
        return True

    return any(
        st.session_state.get(key, "All") != "All"
        for key in FILTER_KEYS
    )


def _active_filter_count():
    # Status has its own visible control, so the popover doesn't count it.
    return sum(
        1
        for key in FILTER_KEYS
        if st.session_state.get(key, "All") != "All"
    )


def display_toolbar(can_edit, categories, subteams, locations, projects):
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

            project = "All"

            if FEATURES["extended"]:
                project = st.selectbox(
                    "Project",
                    projects,
                    key="filter_project"
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

    # Status sits outside the popover so the summary tiles can set it.
    status_key = f"status_filter_{st.session_state.get('status_version', 0)}"

    st.segmented_control(
        "Status",
        ["All"] + STATUSES,
        default=st.session_state.get("status_choice", "All"),
        key=status_key,
        on_change=_status_changed,
        args=(status_key,),
        label_visibility="collapsed"
    )

    status = st.session_state.get("status_choice", "All")

    return search, (category, subteam, location, status, project), add_clicked


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

    rows = []

    for item in items:
        row = {
            "Item": item["name"],
            "Qty": item["quantity"],
            "Status": item["status"],
            "Location": item["location"],
            "Subteam": item["subsystem"]
        }

        if FEATURES["extended"]:
            row["Project"] = item.get("project") or ""

        row["Category"] = item["category"]
        row["Type"] = item["type"]
        row["Notes"] = item["notes"] or ""

        rows.append(row)

    table = pd.DataFrame(rows)

    event = st.dataframe(
        table.style.map(_status_style, subset=["Status"]),
        width="stretch",
        hide_index=True,
        key=table_key,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "Item": st.column_config.TextColumn("Item", width="medium", pinned=True),
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
                    hint = (
                        "Tick a row's checkbox to edit, delete, "
                        "or see its history."
                    )
                else:
                    hint = (
                        "Choose your name at the top to add, edit, "
                        "or delete items."
                    )

                st.html(f'<div class="bar-text">{hint}</div>')

            with col2:
                st.html(
                    f'<div class="row-count">{shown} of {total} items</div>'
                )

            return None

        col1, col2 = st.columns(
            [4, 3],
            gap="small",
            vertical_alignment="center"
        )

        with col1:
            st.html(
                f'<div class="bar-text"><strong>{escape(selected_item["name"])}</strong>'
                f' · {escape(selected_item["location"])}'
                f' · qty {selected_item["quantity"]}</div>'
            )

        # Render all three before returning, so none vanish while a modal is open.
        with col2, st.container(key="bar_actions"):
            edit_col, delete_col, history_col = st.columns(3, gap="small")

            with edit_col:
                edit = st.button(
                    "Edit",
                    icon=":material/edit:",
                    type="primary",
                    disabled=not can_edit,
                    width="stretch"
                )

            with delete_col:
                delete = st.button(
                    "Delete",
                    icon=":material/delete:",
                    disabled=not can_edit,
                    width="stretch"
                )

            with history_col:
                history = st.button(
                    "History",
                    icon=":material/history:",
                    width="stretch"
                )

    if edit:
        return "edit"

    if delete:
        return "delete"

    if history:
        return "history"

    return None


# --------------------------------------------------
# ITEM MODALS
# --------------------------------------------------

def _item_fields(item=None):
    item = item or {}
    categories = options.get("categories")
    subteams = options.get("subteams")
    locations = options.get("locations")
    projects = options.get("projects")
    extended = FEATURES["extended"]

    name = st.text_input(
        "Item name",
        value=item.get("name", "")
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "Category",
            categories,
            index=option_index(categories, item.get("category")),
            placeholder="Select a category"
        )

        location = st.selectbox(
            "Location",
            locations,
            index=option_index(locations, item.get("location")),
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
            subteams,
            index=option_index(subteams, item.get("subsystem")),
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

    data = {}

    if extended:
        project = st.selectbox(
            "Project",
            projects,
            index=option_index(projects, item.get("project")),
            placeholder=UNASSIGNED
        )

        data = {"project": project}

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
        "notes": notes.strip(),
        **data
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
    if item["subsystem"] and item["subsystem"] not in options.get("subteams"):
        st.info(
            f"This item is still filed under \"{item['subsystem']}\". "
            "Pick its subteam before saving."
        )

    cleared = [
        label.lower() for field, label in REQUIRED_FIELDS.items()
        if not item.get(field)
    ]

    if cleared:
        st.info(
            f"This item's {', '.join(cleared)} was cleared when it was "
            "removed from the list. Pick a new one before saving."
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


# --------------------------------------------------
# PROJECTS
# --------------------------------------------------

def _plural(count, word):
    return f"{count} {word}{'' if count == 1 else 's'}"


def display_projects(items):
    if not FEATURES["extended"]:
        _setup_notice("Project allocation", "2026-10-05_add_project_column.sql")
        return

    summary = summarize_projects(items, options.get("projects"))

    cards = ""

    for row in summary:
        attention = ""

        if row["attention"]:
            attention = (
                f'<div class="project-flag">{row["attention"]} low or out</div>'
            )

        cards += f"""
            <div class="project-card">
                <div class="project-name">{escape(row['project'])}</div>
                <div class="project-meta">
                    {_plural(row['items'], 'item')} · {_plural(row['units'], 'unit')}
                </div>
                {attention}
            </div>
        """

    st.html(f'<div class="project-grid">{cards}</div>')

    names = [row["project"] for row in summary]

    project = st.segmented_control(
        "Show items for",
        names,
        default=names[0] if names else None,
        key="project_view"
    )

    if not project:
        return

    members = [
        item for item in items
        if (item.get("project") or UNASSIGNED) == project
    ]

    if not members:
        st.caption("Nothing is allocated to this project yet.")
        return

    table = pd.DataFrame([
        {
            "Item": item["name"],
            "Qty": item["quantity"],
            "Status": item["status"],
            "Subteam": item["subsystem"],
            "Location": item["location"]
        }
        for item in members
    ])

    st.dataframe(
        table.style.map(_status_style, subset=["Status"]),
        width="stretch",
        hide_index=True,
        column_config={
            "Item": st.column_config.TextColumn("Item", width="medium", pinned=True),
            "Qty": st.column_config.NumberColumn("Qty", width="small", format="%d")
        }
    )

    st.caption(
        "To move an item between projects, edit it on the Inventory tab."
    )


# --------------------------------------------------
# ADMIN
# --------------------------------------------------

def _setup_notice(feature, script):
    st.info(
        f"{feature} turns on after the one-time database setup in "
        f"`supabase/{script}` has been run in Supabase."
    )


def _lock_admin():
    st.session_state.admin_unlocked = False


def display_admin_gate(configured):
    """Ask for the leaders' admin code. Returns the entered code on submit."""
    if not configured:
        st.info(
            "The Admin tab is locked. Add ADMIN_ACCESS_CODE to `.env` or "
            "Streamlit Secrets to let leaders unlock it."
        )
        return None

    st.caption("Team leaders can change members, locations, categories, subteams and projects here.")

    with st.form("admin_gate", border=False):
        col1, col2 = st.columns([5, 1], vertical_alignment="bottom")

        with col1:
            code = st.text_input("Admin code", type="password")

        with col2:
            submitted = st.form_submit_button("Unlock", width="stretch")

    return code if submitted else None


@st.dialog("Remove value", width="small")
def remove_value_dialog(list_name, value, used, on_remove):
    field_label = FIELD_LABELS[LIST_FIELDS[list_name]]
    items_word = f"{used} item{'s' if used != 1 else ''}"

    st.markdown(
        f"**{escape(value)}** is used by {items_word}. Removing it leaves "
        f"their {field_label} blank until someone picks a new one."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel", width="stretch"):
            st.rerun()

    with col2:
        if st.button("Remove", type="primary", width="stretch"):
            on_remove(list_name, value)
            st.rerun()


def display_admin(items, can_edit, enabled, on_add, on_remove):
    if not enabled:
        _setup_notice("Editing lists", "2026-10-05_admin_lists.sql")
        return

    st.button("Lock admin", key="lock_admin", type="tertiary", icon=":material/lock:", on_click=_lock_admin)

    if not can_edit:
        st.caption("Choose your name at the top to change these lists.")

    list_name = st.segmented_control(
        "List",
        list(EDITABLE_LISTS),
        format_func=EDITABLE_LISTS.get,
        default="members",
        key="admin_list"
    ) or "members"

    values = options.get(list_name)
    field = LIST_FIELDS.get(list_name)

    for value in values:
        used = count_usage(items, field, value) if field else 0

        col1, col2 = st.columns([5, 1], vertical_alignment="center")

        with col1:
            usage = f" · used by {used} item{'s' if used != 1 else ''}" if used else ""
            st.html(f"<div class='bar-text'>{escape(value)}<span class='muted'>{usage}</span></div>")

        with col2:
            reason = (
                "Each list needs at least one value"
                if len(values) == 1 else None
            )

            if st.button(
                "Remove",
                key=f"remove_{list_name}_{value}",
                type="tertiary",
                disabled=not can_edit or reason is not None,
                help=reason,
                width="stretch"
            ):
                if used:
                    remove_value_dialog(list_name, value, used, on_remove)
                else:
                    on_remove(list_name, value)
                    st.rerun()

    with st.form(f"add_{list_name}", border=False, clear_on_submit=True):
        col1, col2 = st.columns([5, 1], vertical_alignment="bottom")

        with col1:
            new_value = st.text_input(
                f"Add to {EDITABLE_LISTS[list_name].lower()}",
                max_chars=60
            )

        with col2:
            submitted = st.form_submit_button(
                "Add",
                disabled=not can_edit,
                width="stretch"
            )

    if submitted:
        error = on_add(list_name, new_value)

        if error:
            st.error(error)
        else:
            st.rerun()

    st.caption(
        "Removing a value that items use clears it from those items. "
        "To rename, add the new value, move items to it, then remove the old one."
    )


# --------------------------------------------------
# ABOUT
# --------------------------------------------------

REPO_URL = "https://github.com/zanderdhancock/Inventory_Management_System"


def display_footer():
    st.html(
        f"""
        <footer class="app-footer">
            <div class="footer-brand">
                {LOGO_SVG}
                <div>
                    <div class="footer-title">Oceanus Inventory</div>
                    <div class="footer-text">
                        Built for the Oceanus underwater robotics team at Texas A&amp;M.
                    </div>
                </div>
            </div>
            <div class="footer-credits">
                <div>
                    Designed and developed by
                    <a href="https://github.com/zanderdhancock" target="_blank">Zander</a>
                </div>
                <div class="footer-text">
                    Streamlit · Supabase ·
                    <a href="{REPO_URL}" target="_blank">Source on GitHub</a>
                </div>
            </div>
        </footer>
        """
    )
