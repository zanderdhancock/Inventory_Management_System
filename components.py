import csv
import io
from html import escape

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


STATUS_BADGES = {
    "Available": "🟢 Available",
    "Low": "🟡 Low",
    "Out": "🔴 Out",
    "In Use": "🔵 In Use"
}

ACTION_ICONS = {
    "ADD": "➕",
    "EDIT": "✏️",
    "DELETE": "🗑️"
}

FILTER_KEYS = [
    "filter_category",
    "filter_subteam",
    "filter_location",
    "filter_status"
]


# --------------------------------------------------
# SEARCH / FILTERS
# --------------------------------------------------

def clear_filters():
    st.session_state.inventory_search = ""

    for key in FILTER_KEYS:
        st.session_state[key] = "All"


def display_search(can_edit):
    col1, col2 = st.columns(
        [5, 1],
        gap="small",
        vertical_alignment="bottom"
    )

    with col1:
        search = st.text_input(
            "Search Inventory",
            placeholder="Search by item, category, subteam, or location...",
            key="inventory_search",
            label_visibility="collapsed"
        )

    with col2:
        add_clicked = st.button(
            "Add Item",
            icon=":material/add:",
            type="primary",
            disabled=not can_edit,
            width="stretch"
        )

    return search, add_clicked


def display_filters(categories, subteams, locations):
    col1, col2, col3, col4, col5 = st.columns(
        [3, 3, 3, 3, 2],
        gap="small",
        vertical_alignment="bottom"
    )

    with col1:
        category = st.selectbox(
            "Category",
            categories,
            key="filter_category"
        )

    with col2:
        subteam = st.selectbox(
            "Subteam",
            subteams,
            key="filter_subteam"
        )

    with col3:
        location = st.selectbox(
            "Location",
            locations,
            key="filter_location"
        )

    with col4:
        status = st.selectbox(
            "Status",
            ["All"] + STATUSES,
            key="filter_status"
        )

    with col5:
        st.button(
            "Clear Filters",
            icon=":material/refresh:",
            on_click=clear_filters,
            width="stretch"
        )

    return category, subteam, location, status


# --------------------------------------------------
# INVENTORY LIST
# --------------------------------------------------

def display_inventory(items, table_key):
    """Show the inventory table and return the row the user selected."""
    if not items:
        st.info("No inventory items match the current search and filters.")
        return None

    display_items = []

    for item in items:
        display_items.append({
            "Item": item["name"],
            "Category": item["category"],
            "Subteam": item["subsystem"],
            "Location": item["location"],
            "Qty": item["quantity"],
            "Type": item["type"],
            "Status": STATUS_BADGES.get(item["status"], item["status"]),
            "Notes": item["notes"]
        })

    event = st.dataframe(
        display_items,
        width="stretch",
        hide_index=True,
        key=table_key,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "Item": st.column_config.TextColumn(
                "Item",
                width="medium"
            ),
            "Qty": st.column_config.NumberColumn(
                "Qty",
                width="small",
                format="%d"
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                width="small"
            ),
            "Notes": st.column_config.TextColumn(
                "Notes",
                width="large"
            )
        }
    )

    rows = event.selection.rows

    # A stale selection can point past the end after filters change.
    if not rows or rows[0] >= len(items):
        return None

    return items[rows[0]]


def display_row_actions(selected_item, can_edit):
    """Action bar for the selected table row. Returns the clicked action."""
    if not selected_item:
        st.caption(
            "Select a row to edit, delete, or view its history."
        )
        return None

    col1, col2, col3, col4 = st.columns(
        [4, 1, 1, 1],
        gap="small",
        vertical_alignment="center"
    )

    with col1:
        st.markdown(
            f"**{selected_item['name']}** · {selected_item['location']}"
        )

    with col2:
        if st.button(
            "Edit",
            icon=":material/edit:",
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
        "Item Name",
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


def _submit_buttons(label):
    col1, col2 = st.columns(2)

    with col1:
        cancelled = st.form_submit_button(
            "Cancel",
            width="stretch"
        )

    with col2:
        submitted = st.form_submit_button(
            label,
            type="primary",
            width="stretch"
        )

    return submitted, cancelled


def _finish(error):
    if error:
        st.error(error)
    else:
        st.rerun()


@st.dialog("Add Item", width="medium")
def add_item_dialog(on_save):
    with st.form("add_item_form", border=False):
        item = _item_fields()
        submitted, cancelled = _submit_buttons("Add Item")

    if cancelled:
        st.rerun()

    if submitted:
        _finish(on_save(item))


@st.dialog("Edit Item", width="medium")
def edit_item_dialog(item, on_save):
    if item["subsystem"] not in SUBTEAMS:
        st.info(
            f"This item is still filed under \"{item['subsystem']}\". "
            "Pick its subteam before saving."
        )

    with st.form("edit_item_form", border=False):
        updated = _item_fields(item)
        submitted, cancelled = _submit_buttons("Save Changes")

    if cancelled:
        st.rerun()

    if submitted:
        _finish(on_save(item, updated))


@st.dialog("Delete Item", width="small")
def delete_item_dialog(item, on_delete):
    st.markdown(
        f"**{item['name']}**  \n"
        f"{item['location']} · {item['subsystem']} · Qty {item['quantity']}"
    )

    st.warning(
        "This removes the item from inventory. "
        "Its history is kept."
    )

    with st.form("delete_item_form", border=False):
        confirm = st.checkbox(
            f"I confirm I want to delete {item['name']}"
        )
        submitted, cancelled = _submit_buttons("Delete Item")

    if cancelled:
        st.rerun()

    if submitted:
        if not confirm:
            st.warning("Confirm the deletion first.")
        else:
            _finish(on_delete(item))


def display_dashboard(items):
    total_entries = len(items)

    total_quantity = sum(
        int(item["quantity"])
        for item in items
        if item["quantity"] is not None
    )

    low_stock = sum(
        1
        for item in items
        if item["status"] == "Low"
    )

    in_use = sum(
        1
        for item in items
        if item["status"] == "In Use"
    )

    col1, col2, col3, col4 = st.columns(
        4,
        gap="small"
    )

    with col1:
        st.html(
            f"""
            <div class="metric-card">
                <div class="metric-label">Inventory Entries</div>
                <div class="metric-value">{total_entries}</div>
                <div class="metric-accent"></div>
            </div>
            """
        )

    with col2:
        st.html(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Quantity</div>
                <div class="metric-value">{total_quantity}</div>
                <div class="metric-accent"></div>
            </div>
            """
        )

    with col3:
        st.html(
            f"""
            <div class="metric-card">
                <div class="metric-label">Low Stock</div>
                <div class="metric-value">{low_stock}</div>
                <div class="metric-accent"></div>
            </div>
            """
        )

    with col4:
        st.html(
            f"""
            <div class="metric-card">
                <div class="metric-label">In Use</div>
                <div class="metric-value">{in_use}</div>
                <div class="metric-accent"></div>
            </div>
            """
        )


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

def display_history(history, limit=15):
    if not history:
        st.info("No inventory activity recorded yet.")
        return

    for entry in history[:limit]:
        icon = ACTION_ICONS.get(
            entry["action"],
            "•"
        )

        timestamp = format_timestamp(entry["created_at"])

        item_name = escape(str(entry["item_name"]))
        member = escape(str(entry["member"]))
        action = escape(str(entry["action"]))
        details = escape(str(entry["details"] or ""))

        details_html = ""

        if entry["details"]:
            details_html = f"""
                <div class="activity-details">
                    {details}
                </div>
            """

        st.html(
            f"""
            <div class="activity-card">
                <div class="activity-top">

                    <div class="activity-item">
                        {icon} {item_name}
                    </div>

                    <div class="activity-action">
                        {action}
                    </div>

                </div>

                <div class="activity-meta">
                    {member} • {timestamp}
                </div>

                {details_html}

            </div>
            """
        )


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


@st.dialog("Activity History", width="large")
def history_dialog(history, item=None):
    if item:
        st.caption(f"Showing history for **{item['name']}**")

    members = sorted(
        set(entry["member"] for entry in history if entry["member"])
    )
    actions = sorted(
        set(entry["action"] for entry in history if entry["action"])
    )

    col1, col2 = st.columns(2)

    with col1:
        member_filter = st.multiselect(
            "Member",
            members,
            placeholder="All members"
        )

        search = st.text_input(
            "Search",
            placeholder="Item name or change details..."
        )

    with col2:
        action_filter = st.multiselect(
            "Action",
            actions,
            placeholder="All actions"
        )

        date_range = st.date_input(
            "Date range",
            value=[],
            format="MM/DD/YYYY"
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

    counts = {
        action: sum(1 for entry in entries if entry["action"] == action)
        for action in ["ADD", "EDIT", "DELETE"]
    }

    st.caption(
        f"{len(entries)} records · "
        f"{counts['ADD']} added · "
        f"{counts['EDIT']} edited · "
        f"{counts['DELETE']} deleted"
    )

    if not entries:
        st.info("No activity matches these filters.")
        return

    st.dataframe(
        [
            {
                "Time": format_timestamp(entry["created_at"]),
                "Action": f"{ACTION_ICONS.get(entry['action'], '•')} {entry['action']}",
                "Item": entry["item_name"],
                "Member": entry["member"],
                "Details": entry["details"] or ""
            }
            for entry in entries
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "Details": st.column_config.TextColumn(
                "Details",
                width="large"
            )
        }
    )

    st.download_button(
        "Download CSV",
        data=_history_csv(entries),
        file_name="oceanus_inventory_history.csv",
        mime="text/csv",
        icon=":material/download:"
    )
