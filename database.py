from pathlib import Path

from dotenv import dotenv_values
from supabase import create_client


# Load Supabase connection information
env_path = Path(__file__).resolve().parent / ".env"
config = dotenv_values(env_path)

supabase_url = config["SUPABASE_URL"]
supabase_key = config["SUPABASE_KEY"]

supabase = create_client(supabase_url, supabase_key)


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


def add_history(item_id, item_name, action, member, details=""):
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


def get_history():
    response = (
        supabase
        .table("inventory_history")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data