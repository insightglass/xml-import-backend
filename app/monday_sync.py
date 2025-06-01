import os
import requests

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
API_URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

SALES_QUOTES_BOARD_ID = 9273227645

SUBITEMS_COLUMN_IDS = {
    "Item Name": "text",
    "Supplier": "supplier",
    "Model": "model",
    "NetSize": "netsize",
    "ItemDesc": "itemdesc",
    "Room": "room",
    "Quantity": "qty",
    "Unit Price (Markup)": "price"
}

JOB_NUMBER_COLUMN_ID = "text_mkrgwwwh"

def create_sales_quote_item(job_number, vendor):
    query = """
    mutation ($boardId: ID!, $itemName: String!, $columnVals: JSON!) {
      create_item(board_id: $boardId, item_name: $itemName, column_values: $columnVals) {
        id
      }
    }
    """
    column_values = {JOB_NUMBER_COLUMN_ID: job_number}
    variables = {
        "boardId": str(SALES_QUOTES_BOARD_ID),
        "itemName": f"Quote from {vendor} ({job_number})",
        "columnVals": column_values
    }
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    try:
        data = response.json()
        if "errors" in data:
            print("❌ Error creating main item:", data["errors"])
        return data["data"]["create_item"]["id"]
    except Exception as e:
        print("❌ Failed to parse response from create_item:", str(e))
        print(response.text)
        return None

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
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    try:
        data = response.json()
        if "errors" in data:
            print(f"❌ Error creating subitem '{subitem_name}':", data["errors"])
    except Exception as e:
        print(f"❌ Failed to parse response for subitem '{subitem_name}':", str(e))
        print(response.text)

def push_to_monday_quotes_board(parsed):
    job_number = parsed["job_number"]
    vendor = parsed["vendor"]
    items = parsed["items"]

    print(f"✅ Starting Monday.com sync for {job_number} ({vendor}) with {len(items)} subitems")

    parent_item_id = create_sales_quote_item(job_number, vendor)
    if not parent_item_id:
        print("❌ Failed to create parent item. Aborting subitem creation.")
        return

    for item in items:
        create_subitem(parent_item_id, item)
