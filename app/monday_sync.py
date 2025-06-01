import os
import requests

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
API_URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

# Real board ID from user
SALES_QUOTES_BOARD_ID = 9273227645

# Subitem column IDs (update these if needed)
SUBITEMS_COLUMN_IDS = {
    "Item Name": "text",  # typically the default subitem title
    "Supplier": "supplier",
    "Model": "model",
    "NetSize": "netsize",
    "ItemDesc": "itemdesc",
    "Room": "room",
    "Quantity": "qty",
    "Unit Price (Markup)": "price"
}

# Job Number column ID (top-level item)
JOB_NUMBER_COLUMN_ID = "text_mkrgwwwh"

def create_sales_quote_item(job_number, vendor):
    query = """
    mutation ($boardId: Int!, $itemName: String!, $columnVals: JSON!) {
      create_item(board_id: $boardId, item_name: $itemName, column_values: $columnVals) {
        id
      }
    }
    """
    column_values = {JOB_NUMBER_COLUMN_ID: job_number}
    variables = {
        "boardId": SALES_QUOTES_BOARD_ID,
        "itemName": f"Quote from {vendor} ({job_number})",
        "columnVals": column_values
    }
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    data = response.json()
    return data["data"]["create_item"]["id"]

def create_subitem(parent_item_id, subitem_data):
    subitem_name = subitem_data.get("Item Name", "")
    column_values = {
        SUBITEMS_COLUMN_IDS[key]: str(subitem_data.get(key, "")) for key in SUBITEMS_COLUMN_IDS if key != "Item Name"
    }

    query = """
    mutation ($parentId: Int!, $itemName: String!, $columnVals: JSON!) {
      create_subitem(parent_item_id: $parentId, item_name: $itemName, column_values: $columnVals) {
        id
      }
    }
    """
    variables = {
        "parentId": int(parent_item_id),
        "itemName": subitem_name,
        "columnVals": column_values
    }
    requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)

def push_to_monday_quotes_board(parsed):
    job_number = parsed["job_number"]
    vendor = parsed["vendor"]
    items = parsed["items"]

    parent_item_id = create_sales_quote_item(job_number, vendor)

    for item in items:
        create_subitem(parent_item_id, item)
