import os
import requests

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
API_URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

SALES_QUOTES_BOARD_ID = 9273227645
JOB_NUMBERS_BOARD_ID = 9273230844

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

JOB_NUMBER_COLUMN_ID = "board_relation_mkrfcxnh"

def lookup_job_number_id(job_number):
    query = """
    query ($boardId: [Int]) {
      boards(ids: $boardId) {
        items {
          id
          name
        }
      }
    }
    """
    variables = {
        "boardId": [JOB_NUMBERS_BOARD_ID]
    }
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    try:
        data = response.json()
        if "data" not in data:
            print("❌ lookup_job_number_id: 'data' key missing")
            print("🔎 Full response:")
            print(response.text)
            return None
        for item in data["data"]["boards"][0]["items"]:
            if item["name"].strip().upper() == job_number.strip().upper():
                return int(item["id"])
    except Exception as e:
        print("❌ Exception during Job Number lookup:", str(e))
        print("🔎 Raw response:")
        print(response.text)
    return None

def create_sales_quote_item(job_number, vendor):
    job_id = lookup_job_number_id(job_number)
    if not job_id:
        print(f"❌ Job Number '{job_number}' not found in Job Numbers board.")
        return None

    column_values = {
        JOB_NUMBER_COLUMN_ID: {
            "linkedPulseIds": [{"linkedPulseId": job_id}]
        }
    }

    query = """
    mutation ($boardId: ID!, $itemName: String!, $columnVals: JSON!) {
      create_item(board_id: $boardId, item_name: $itemName, column_values: $columnVals) {
        id
      }
    }
    """
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
