from pathlib import Path

import streamlit as st
from dotenv import dotenv_values
from supabase import create_client

# Load Supabase info
env_path = Path(__file__).resolve().parent / ".env"
config = dotenv_values(env_path)

supabase_url = config["SUPABASE_URL"]
supabase_key = config["SUPABASE_KEY"]

# Connect to Supabase
supabase = create_client(supabase_url, supabase_key)

# Get inventory
response = (
    supabase
    .table("inventory_items")
    .select("*")
    .execute()
)

items = response.data

# Page
st.title("Oceanus Inventory")

# Search bar
search = st.text_input(
    "Search inventory",
    placeholder="Thruster, electronics, Member A..."
)

if search:
    search = search.lower()

    items = [
        item for item in items
        if search in str(item["name"]).lower()
        or search in str(item["category"]).lower()
        or search in str(item["subsystem"]).lower()
        or search in str(item["location"]).lower()
    ]

# Filter options

subsystems = ["All"] + sorted(
    list(set(item["subsystem"] for item in items if item["subsystem"]))
)

categories = ["All"] + sorted(
    list(set(item["category"] for item in items if item["category"]))
)

locations = ["All"] + sorted(
    list(set(item["location"] for item in items if item["location"]))
)

# Filter dropdowns
col1, col2, col3 = st.columns(3)

with col1:
    category_filter = st.selectbox("Category", categories)

with col2:
    subsystem_filter = st.selectbox("Subsystem", subsystems)

with col3:
    location_filter = st.selectbox("Location", locations)

# Apply filters
if category_filter != "All":
    items = [
        item for item in items
        if item["category"] == category_filter
    ]

if subsystem_filter != "All":
    items = [
        item for item in items
        if item["subsystem"] == subsystem_filter
    ]

if location_filter != "All":
    items = [
        item for item in items
        if item["location"] == location_filter
    ]

# Table
st.dataframe(
    items,
    use_container_width=True
)