import streamlit as st
import hmac
from pathlib import Path
from dotenv import dotenv_values
from styles import apply_styles

st.set_page_config(
    page_title="Oceanus Inventory",
    page_icon="🌊",
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

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.html(
        """
        <div class="access-shell">
            <div class="access-kicker">
                OCEANUS • UNDERWATER ROBOTICS
            </div>

            <div class="access-title">
                Inventory System
            </div>

            <div class="access-subtitle">
                Authorized team access
            </div>
        </div>
        """
    )

    with st.form("access_form"):
        entered_code = st.text_input(
            "Team Access Code",
            type="password"
        )

        submitted = st.form_submit_button(
            "Enter Inventory System"
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

from options import MEMBERS

from database import (
    get_inventory,
    add_inventory_item,
    update_inventory_item,
    add_history,
    get_history
)

from inventory import (
    search_inventory,
    filter_inventory,
    get_filter_options,
    get_change_summary,
    find_duplicate_item
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


# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------


st.html(
    """
    <div class="oceanus-hero">
        <div class="oceanus-kicker">
            OCEANUS • UNDERWATER ROBOTICS
        </div>

        <div class="oceanus-title">
            Inventory System
        </div>

        <div class="oceanus-subtitle">
            Equipment, materials, and inventory operations
        </div>
    </div>
    """
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "success_message" not in st.session_state:
    st.session_state.success_message = None


# --------------------------------------------------
# MEMBER SELECTION
# --------------------------------------------------

with st.container(border=True):

    st.markdown(
    "#### Who are you?",
    anchors=False
    )

    current_member = st.selectbox(
        "Select your name before making inventory changes",
        MEMBERS,
        index=None,
        placeholder="Select your name..."
    )

    st.caption(
        "Your name will be recorded when you add or edit inventory."
    )


st.session_state.current_member = current_member


# --------------------------------------------------
# SUCCESS MESSAGES
# --------------------------------------------------

if st.session_state.success_message:

    st.success(
        st.session_state.success_message
    )

    st.session_state.success_message = None


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

items = get_inventory()

history = get_history()


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

display_dashboard(items)


# --------------------------------------------------
# INVENTORY CHANGES
# --------------------------------------------------

if current_member:

    # ------------------------------
    # EDIT ITEM
    # ------------------------------

    st.markdown(
        """
        <div style="
            margin-top: 1.4rem;
            margin-bottom: 0.6rem;
            color: #8FAFC1;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.14em;
        ">
            INVENTORY OPERATIONS
        </div>
        """,
        unsafe_allow_html=True
    )

    item_id, updated_data = display_edit_item_form(items)

    if item_id:

        old_item = next(
            item
            for item in items
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


    # ------------------------------
    # ADD ITEM
    # ------------------------------

    new_item = display_add_item_form()

    if new_item:

        duplicate = find_duplicate_item(
            items,
            new_item
        )

        if duplicate:

            st.warning(
                f"{duplicate['name']} already exists at "
                f"{duplicate['location']}. "
                "Edit the existing item instead of creating a duplicate."
            )

        else:

            added_items = add_inventory_item(
                new_item
            )

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


else:

    st.info(
        "Select your name above to add or edit inventory."
    )


# --------------------------------------------------
# SEARCH
# --------------------------------------------------

st.html(
    """
    <div class="inventory-section-label">
        INVENTORY DATABASE
    </div>
    """
)

search = display_search()

filtered_items = search_inventory(
    items,
    search
)


# --------------------------------------------------
# FILTER OPTIONS
# --------------------------------------------------

categories, subsystems, locations = get_filter_options(
    filtered_items
)

category_filter, subsystem_filter, location_filter = display_filters(
    categories,
    subsystems,
    locations
)


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_items = filter_inventory(
    filtered_items,
    category_filter,
    subsystem_filter,
    location_filter
)


# --------------------------------------------------
# INVENTORY DISPLAY
# --------------------------------------------------

display_inventory(
    filtered_items
)


# --------------------------------------------------
# HISTORY
# --------------------------------------------------


st.html(
    """
    <div class="activity-section-label">
        RECENT ACTIVITY
    </div>
    """
)

display_history(
    history
)