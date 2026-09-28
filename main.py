import streamlit as st

st.set_page_config(
    page_title="Oceanus Inventory",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from options import MEMBERS

from database import get_inventory, add_inventory_item, update_inventory_item, add_history, get_history
from inventory import (
    search_inventory,
    filter_inventory,
    get_filter_options
)
from components import (
    display_search,
    display_filters,
    display_inventory,
    display_add_item_form,
    display_edit_item_form,
    display_dashboard,
    display_history
)

if "success_message" not in st.session_state:
    st.session_state.success_message = None

st.title("🌊 Oceanus Inventory")
st.caption("Inventory management for the Oceanus Underwater Robotics Team")


with st.sidebar:
    st.header("Oceanus")

    current_member = st.selectbox(
        "Current Member",
        MEMBERS
    )

    st.caption(
        "Your name is used to record inventory changes."
    )

st.session_state.current_member = current_member

if st.session_state.success_message:
    st.success(st.session_state.success_message)
    st.session_state.success_message = None

items = get_inventory()
history = get_history()
display_dashboard(items)


item_id, updated_data = display_edit_item_form(items)

if item_id:
    old_item = next(
        item for item in items
        if item["id"] == item_id
    )

    changes = get_change_summary(
        old_item,
        updated_data
    )

    update_inventory_item(
        item_id,
        updated_data
    )

    if changes:
        add_history(
            item_id,
            updated_data["name"],
            "EDIT",
            current_member,
            changes
        )

    st.session_state.success_message = (
        f"{updated_data['name']} updated successfully."
    )

    st.rerun()

new_item = display_add_item_form()

if new_item:
    added_items = add_inventory_item(new_item)
    added_item = added_items[0]

    add_history(
        added_item["id"],
        added_item["name"],
        "ADD",
        current_member,
        "Item added to inventory"
    )

    st.session_state.success_message = (
        f"{new_item['name']} added successfully."
    )

    st.rerun()

search = display_search()

items = search_inventory(items, search)

categories, subsystems, locations = get_filter_options(items)

category_filter, subsystem_filter, location_filter = display_filters(
    categories,
    subsystems,
    locations
)

items = filter_inventory(
    items,
    category_filter,
    subsystem_filter,
    location_filter
)

display_inventory(items)

st.divider()
display_history(history)