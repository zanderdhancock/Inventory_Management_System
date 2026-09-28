import streamlit as st

from options import (
    CATEGORIES,
    SUBSYSTEMS,
    ITEM_TYPES,
    STATUSES,
    LOCATIONS
)

def display_search():
    return st.text_input(
        "Search inventory",
        placeholder="Thruster, electronics, Member A..."
    )

def display_filters(categories, subsystems, locations):
    col1, col2, col3 = st.columns(3)

    with col1:
        category = st.selectbox(
            "Category",
            categories
        )

    with col2:
        subsystem = st.selectbox(
            "Subsystem",
            subsystems
        )

    with col3:
        location = st.selectbox(
            "Location",
            locations
        )

    return category, subsystem, location

def display_inventory(items):
    st.subheader("Inventory")

    if not items:
        st.info("No inventory items match your search.")
        return

    display_items = []

    for item in items:
        display_items.append({
            "Item": item["name"],
            "Category": item["category"],
            "Subsystem": item["subsystem"],
            "Location": item["location"],
            "Quantity": item["quantity"],
            "Type": item["type"],
            "Status": item["status"],
            "Notes": item["notes"]
        })

    st.dataframe(
        display_items,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Quantity": st.column_config.NumberColumn(
                "Quantity",
                format="%d"
            )
        }
    )

def display_add_item_form():
    with st.expander("Add Item"):
        with st.form("add_item_form", clear_on_submit=True):
            name = st.text_input("Item Name")
            category = st.selectbox("Category", CATEGORIES)
            subsystem = st.selectbox("Subsystem", SUBSYSTEMS)
            location = st.selectbox("Location", LOCATIONS)

            quantity = st.number_input(
                "Quantity",
                min_value=0,
                step=1
            )

            item_type = st.selectbox("Type", ITEM_TYPES)
            status = st.selectbox("Status", STATUSES)
            notes = st.text_area("Notes")

            submitted = st.form_submit_button("Add Item")

        if submitted:
            name = name.strip()

            if not name:
                st.error("Item name is required.")
                return None

            item = {
                "name": name,
                "category": category,
                "subsystem": subsystem,
                "location": location,
                "quantity": int(quantity),
                "type": item_type,
                "status": status,
                "notes": notes.strip()
            }

            return item

    return None

def display_edit_item_form(items):
    if not items:
        return None, None

    with st.expander("Edit Item"):

        item_options = {
            f"{item['name']} — {item['location']} — ID {item['id']}": item
            for item in items
        }

        selected_label = st.selectbox(
            "Select Item",
            list(item_options.keys()),
            key="edit_item_selector"
        )

        selected_item = item_options[selected_label]

        with st.form("edit_item_form"):

            name = st.text_input(
                "Item Name",
                value=selected_item["name"]
            )

            category = st.selectbox(
                "Category",
                CATEGORIES,
                index=CATEGORIES.index(selected_item["category"])
            )

            subsystem = st.selectbox(
                "Subsystem",
                SUBSYSTEMS,
                index=SUBSYSTEMS.index(selected_item["subsystem"])
            )

            location = st.selectbox(
                "Location",
                LOCATIONS,
                index=LOCATIONS.index(selected_item["location"])
            )

            quantity = st.number_input(
                "Quantity",
                min_value=0,
                value=int(selected_item["quantity"]),
                step=1
            )

            item_type = st.selectbox(
                "Type",
                ITEM_TYPES,
                index=ITEM_TYPES.index(selected_item["type"])
            )

            status = st.selectbox(
                "Status",
                STATUSES,
                index=STATUSES.index(selected_item["status"])
            )

            notes = st.text_area(
                "Notes",
                value=selected_item["notes"] or ""
            )

            submitted = st.form_submit_button("Save Changes")

        if submitted:
            name = name.strip()

            if not name:
                st.error("Item name is required.")
                return None, None

            updated_data = {
                "name": name,
                "category": category,
                "subsystem": subsystem,
                "location": location,
                "quantity": int(quantity),
                "type": item_type,
                "status": status,
                "notes": notes.strip()
            }

            return selected_item["id"], updated_data

    return None, None

def display_delete_item_form(items):
    if not items:
        return None, None

    with st.expander("Delete Item"):

        item_options = {
            f"{item['name']} — {item['location']} — ID {item['id']}": item
            for item in items
        }

        selected_label = st.selectbox(
            "Select Item to Delete",
            list(item_options.keys()),
            key="delete_item_selector"
        )

        selected_item = item_options[selected_label]

        with st.form("delete_item_form"):

            confirm = st.checkbox(
                f"I confirm I want to delete "
                f"{selected_item['name']}"
            )

            submitted = st.form_submit_button(
                "Delete Item"
            )

        if submitted:
            if confirm:
                return selected_item["id"], selected_item

            st.warning(
                "Confirm the deletion first."
            )

    return None, None

def display_dashboard(items):
    total_entries = len(items)

    total_quantity = sum(
        int(item["quantity"])
        for item in items
        if item["quantity"] is not None
    )

    low_stock = sum(
        1 for item in items
        if item["status"] == "Low"
    )

    in_use = sum(
        1 for item in items
        if item["status"] == "In Use"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Inventory Entries",
        total_entries
    )

    col2.metric(
        "Total Quantity",
        total_quantity
    )

    col3.metric(
        "Low Stock",
        low_stock
    )

    col4.metric(
        "In Use",
        in_use
    )

def display_history(history):
    st.subheader("Recent Activity")

    if not history:
        st.info("No inventory activity recorded yet.")
        return

    action_icons = {
        "ADD": "➕",
        "EDIT": "✏️",
        "DELETE": "🗑️"
    }

    for entry in history[:8]:

        icon = action_icons.get(
            entry["action"],
            "•"
        )

        with st.container(border=True):

            st.markdown(
                f"### {icon} {entry['item_name']}"
            )

            st.write(
                f"**{entry['member']}** • {entry['action']}"
            )

            if entry["details"]:
                st.caption(entry["details"])

            if entry["created_at"]:
                timestamp = (
                    entry["created_at"]
                    .replace("T", " ")
                    [:16]
                )

                st.caption(timestamp)