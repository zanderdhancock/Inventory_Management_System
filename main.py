import streamlit as st
import hmac
from pathlib import Path
from dotenv import dotenv_values
from styles import apply_styles
from components import LOGO_SVG, display_topbar

st.set_page_config(
    page_title="Oceanus Inventory",
    page_icon=":material/inventory_2:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_styles()

# --------------------------------------------------
# APP ACCESS
# --------------------------------------------------

env_path = Path(__file__).resolve().parent / ".env"
config = dotenv_values(env_path)

app_access_code = (
    config.get("APP_ACCESS_CODE")
    or st.secrets["APP_ACCESS_CODE"]
)


def read_optional_secret(name):
    try:
        return config.get(name) or st.secrets.get(name)
    except Exception:
        return None


# Leaders-only code for the Admin tab. Without it, the tab stays locked.
admin_access_code = read_optional_secret("ADMIN_ACCESS_CODE")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "admin_unlocked" not in st.session_state:
    st.session_state.admin_unlocked = False

if not st.session_state.authenticated:
    display_topbar()

    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.html(
            f"""
            <div class="access-header">
                {LOGO_SVG}
                <div class="page-title">Oceanus Inventory</div>
                <div class="page-subtitle">Enter the team access code to continue.</div>
            </div>
            """
        )

        with st.form("access_form"):
            entered_code = st.text_input(
                "Access code",
                type="password"
            )

            submitted = st.form_submit_button(
                "Continue",
                type="primary",
                width="stretch"
            )

    if submitted:
        if hmac.compare_digest(
            entered_code,
            app_access_code
        ):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect access code.")

    st.stop()

import options

from database import (
    get_inventory,
    add_inventory_item,
    update_inventory_item,
    delete_inventory_item,
    add_history,
    get_history,
    supports_extended_fields,
    get_options,
    add_options,
    remove_option
)

from inventory import (
    search_inventory,
    filter_inventory,
    get_filter_options,
    get_change_summary,
    find_duplicate_item,
    validate_item,
    apply_subteams,
    UNASSIGNED
)

from components import (
    display_header,
    display_summary,
    display_toolbar,
    display_inventory,
    display_selection_bar,
    display_history,
    add_item_dialog,
    edit_item_dialog,
    delete_item_dialog,
    item_history_dialog,
    display_projects,
    display_admin,
    display_admin_gate,
    display_footer,
    FEATURES
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "success_message" not in st.session_state:
    st.session_state.success_message = None

# Bumped after every change so the table drops its row selection.
if "table_version" not in st.session_state:
    st.session_state.table_version = 0

if "status_choice" not in st.session_state:
    st.session_state.status_choice = "All"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:
    stored_items = get_inventory()
    items = apply_subteams(stored_items)
    history = get_history()
    option_rows = get_options()
    extended = supports_extended_fields()
except Exception as error:
    print(f"Failed to load inventory: {error!r}")
    st.error("Unable to load inventory. Please refresh and try again.")
    st.stop()

# None means the inventory_options table hasn't been created yet.
options.load(option_rows)
FEATURES["extended"] = extended



# --------------------------------------------------
# HEADER
# --------------------------------------------------

current_member = display_header(options.get("members"))

if st.session_state.success_message:
    st.toast(
        st.session_state.success_message,
        icon=":material/check_circle:"
    )

    st.session_state.success_message = None


# --------------------------------------------------
# CHANGE HANDLERS
# Each returns an error message for the modal, or None on success.
# --------------------------------------------------

def finish_change(message):
    st.session_state.success_message = message
    st.session_state.table_version += 1


def save_new_item(new_item):
    error = validate_item(new_item)

    if error:
        return error

    duplicate = find_duplicate_item(
        items,
        new_item
    )

    if duplicate:
        return (
            f"{duplicate['name']} already exists at "
            f"{duplicate['location']}. "
            "Edit the existing item instead of creating a duplicate."
        )

    try:
        added_item = add_inventory_item(
            new_item
        )[0]

        add_history(
            added_item["id"],
            added_item["name"],
            "ADD",
            current_member,
            f"Added {added_item['quantity']} at {added_item['location']}"
        )
    except Exception as error:
        print(f"Failed to add item: {error!r}")
        return "Unable to add item. Please try again."

    finish_change(
        f"{new_item['name']} added successfully."
    )

    return None


def save_item_changes(old_item, updated_data):
    error = validate_item(updated_data)

    if error:
        return error

    duplicate = find_duplicate_item(
        items,
        updated_data,
        exclude_id=old_item["id"]
    )

    if duplicate:
        return (
            f"{duplicate['name']} already exists at "
            f"{duplicate['location']}."
        )

    stored_item = next(
        item
        for item in stored_items
        if item["id"] == old_item["id"]
    )

    changes = get_change_summary(
        stored_item,
        updated_data
    )

    if not changes:
        return "No changes to save."

    try:
        update_inventory_item(
            old_item["id"],
            updated_data
        )

        add_history(
            old_item["id"],
            updated_data["name"],
            "EDIT",
            current_member,
            changes
        )
    except Exception as error:
        print(f"Failed to update item: {error!r}")
        return "Unable to update inventory. Please try again."

    finish_change(
        f"{updated_data['name']} updated successfully."
    )

    return None


def remove_item(item):
    try:
        delete_inventory_item(
            item["id"]
        )

        add_history(
            item["id"],
            item["name"],
            "DELETE",
            current_member,
            f"Deleted {item['quantity']} from {item['location']} "
            f"({item['category']}, {item['subsystem']})"
        )
    except Exception as error:
        print(f"Failed to delete item: {error!r}")
        return "Unable to delete item. Please try again."

    finish_change(
        f"{item['name']} deleted."
    )

    return None


def add_list_value(list_name, value):
    value = (value or "").strip()

    if not value:
        return "Enter a value to add."

    current = options.get(list_name)

    if value.lower() in (existing.lower() for existing in current):
        return f"{value} is already on the list."

    if value == UNASSIGNED:
        return f"{UNASSIGNED} is reserved."

    stored = {
        row["value"]
        for row in option_rows or []
        if row["list_name"] == list_name
    }

    # A list still running on defaults gets them saved alongside the new value.
    rows = [
        {"list_name": list_name, "value": existing, "position": position}
        for position, existing in enumerate(current)
        if existing not in stored
    ]

    rows.append({
        "list_name": list_name,
        "value": value,
        "position": len(current)
    })

    try:
        add_options(rows)
    except Exception as error:
        print(f"Failed to add option: {error!r}")
        return "Unable to save. Please try again."

    st.session_state.success_message = f"Added {value}."

    return None


def remove_list_value(list_name, value):
    try:
        remove_option(list_name, value)
    except Exception as error:
        print(f"Failed to remove option: {error!r}")
        st.session_state.success_message = "Unable to remove. Please try again."
        return

    st.session_state.success_message = f"Removed {value}."


# --------------------------------------------------
# PAGE
# --------------------------------------------------

display_summary(items)

can_edit = current_member is not None

inventory_tab, projects_tab, activity_tab, admin_tab = st.tabs(
    ["Inventory", "Projects", "Activity", "Admin"]
)

with inventory_tab, st.container(border=True, key="inventory_card"):

    categories, subteams, locations = get_filter_options(
        items
    )

    projects = ["All"] + options.get("projects") + [UNASSIGNED]

    search, filters, add_clicked = display_toolbar(
        can_edit,
        categories,
        subteams,
        locations,
        projects
    )

    (
        category_filter,
        subteam_filter,
        location_filter,
        status_filter,
        project_filter
    ) = filters

    if add_clicked:
        add_item_dialog(save_new_item)

    filtered_items = filter_inventory(
        search_inventory(items, search),
        category_filter,
        subteam_filter,
        location_filter,
        status_filter,
        project_filter
    )

    # The table renders after the bar, so read its selection from state.
    table_key = f"inventory_table_{st.session_state.table_version}"
    selection_bar = st.container()

    selected_item = display_inventory(
        filtered_items,
        table_key
    )

    with selection_bar:
        action = display_selection_bar(
            selected_item,
            can_edit,
            len(filtered_items),
            len(items)
        )

    if action == "edit":
        edit_item_dialog(selected_item, save_item_changes)
    elif action == "delete":
        delete_item_dialog(selected_item, remove_item)
    elif action == "history":
        item_history_dialog(history, selected_item)

with activity_tab, st.container(border=True, key="activity_card"):

    display_history(history)

with projects_tab, st.container(border=True, key="projects_card"):

    display_projects(items)

with admin_tab, st.container(border=True, key="admin_card"):

    if not st.session_state.admin_unlocked:
        entered_admin_code = display_admin_gate(admin_access_code is not None)

        if entered_admin_code is not None:
            if hmac.compare_digest(entered_admin_code, admin_access_code):
                st.session_state.admin_unlocked = True
                st.rerun()
            else:
                st.error("Incorrect admin code.")
    else:
        display_admin(
            items,
            can_edit,
            option_rows is not None,
            add_list_value,
            remove_list_value
        )

display_footer()
