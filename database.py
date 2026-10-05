from pathlib import Path

import streamlit as st
from dotenv import dotenv_values
from supabase import create_client


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

env_path = Path(__file__).resolve().parent / ".env"
config = dotenv_values(env_path)

supabase_url = (
    config.get("SUPABASE_URL")
    or st.secrets["SUPABASE_URL"]
)

supabase_key = (
    config.get("SUPABASE_SECRET_KEY")
    or st.secrets["SUPABASE_SECRET_KEY"]
)

supabase = create_client(
    supabase_url,
    supabase_key
)


# --------------------------------------------------
# INVENTORY
# --------------------------------------------------

def get_inventory():
    response = (
        supabase
        .table("inventory_items")
        .select("*")
        .execute()
    )

    return response.data


def add_inventory_item(item):
    response = (
        supabase
        .table("inventory_items")
        .insert(item)
        .execute()
    )

    return response.data


def update_inventory_item(item_id, updated_data):
    response = (
        supabase
        .table("inventory_items")
        .update(updated_data)
        .eq("id", item_id)
        .execute()
    )

    return response.data


def delete_inventory_item(item_id):
    response = (
        supabase
        .table("inventory_items")
        .delete()
        .eq("id", item_id)
        .execute()
    )

    return response.data


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

def add_history(
    item_id,
    item_name,
    action,
    member,
    details=""
):
    response = (
        supabase
        .table("inventory_history")
        .insert({
            "item_id": item_id,
            "item_name": item_name,
            "action": action,
            "member": member,
            "details": details
        })
        .execute()
    )

    return response.data


def get_history(limit=None):
    query = (
        supabase
        .table("inventory_history")
        .select("*")
        .order("created_at", desc=True)
    )

    if limit:
        query = query.limit(limit)

    response = query.execute()

    return response.data

# --------------------------------------------------
# FEATURE DETECTION
# --------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)
def supports_extended_fields():
    """True once supabase/2026-10-05_add_project_column.sql has been run."""
    try:
        (
            supabase
            .table("inventory_items")
            .select("project")
            .limit(1)
            .execute()
        )
    except Exception:
        return False

    return True
