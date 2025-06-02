import os
import json
import requests

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

SALES_QUOTES_BOARD_ID = 9273227645
JOB_NUMBERS_BOARD_ID = 9273226835

EXPECTED_TITLES = {
    "Supplier",
    "Model",
    "NetSize",
    "ItemDesc",
    "Room",
    "Quantity",
    "Unit Price (Markup)"
}

JOB_NUMBER_COLUMN_ID = "board_relation_mkrfcxnh"

def lookup_job_number_id(job_number):
    query = f"""
    query {{
      boards(ids: [{JOB_NUMBERS_BOARD_ID}]) {{
        items_page(limit: 200) {{
          items {{
            id
            name
          }}
        }}
      }}
    }}
    """
    response = requests.post(API_URL, json={"query": query}, headers=HEADERS)
    try:
        data = response.json()
        for item in data["data"]["boards"][0]["items_page"]["items"]:
            if item["name"].strip().upper() == job_number.strip().upper():
                return int(item["id"])
    except Exception as e:
        print("❌ Exception during job number lookup:", e)
        print(response.text)
    return None

def create_sales_quote_item(job_number, vendor):
    job_id = lookup_job_number_id(job_number)
    if not job_id:
        print(f"❌ Job Number '{job_number}' not found.")
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
        "boardId": SALES_QUOTES_BOARD_ID,
        "itemName": f"Quote from {vendor} ({job_number})",
        "columnVals": json.dumps(column_values)
    }

    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    try:
        data = response.json()
        return int(data["data"]["create_item"]["id"])
    except Exception as e:
        print("❌ Failed to create main item:", e)
        print(response.text)
        return None

def fetch_column_id_map(subitem_id):
    query = f"""
    query {{
      items(ids: [{subitem_id}]) {{
        column_values {{
          id
          title
        }}
      }}
    }}
    """
    response = requests.post(API_URL, json={"query": query}, headers=HEADERS)
    data = response.json()
    try:
        mapping = {}
        for col in data["data"]["items"][0]["column_values"]:
            title = col["title"].strip()
            if title in EXPECTED_TITLES:
                mapping[title] = col["id"]
        return mapping
    except Exception as e:
        print(f"❌ Failed to parse column map for subitem {subitem_id}:", e)
        print(response.text)
        return {}

def create_subitem(parent_item_id, subitem_data):
    subitem_name = subitem_data.get("Item Name", "")

    mutation = """
    mutation ($parentId: Int!, $itemName: String!) {
      create_subitem(parent_id: $parentId, item_name: $itemName) {
        id
      }
    }
    """
    variables = {
        "parentId": parent_item_id,
        "itemName": subitem_name
    }

    response = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
    try:
        data = response.json()
        subitem_id = data["data"]["create_subitem"]["id"]
        print(f"🟢 Created subitem '{subitem_name}' (ID: {subitem_id})")
    except Exception as e:
        print(f"❌ Failed to create subitem '{subitem_name}':", e)
        print(response.text)
        return

    column_map = fetch_column_id_map(subitem_id)

    for title, value in subitem_data.items():
        if title == "Item Name" or not value:
            continue
        column_id = column_map.get(title)
        if not column_id:
            print(f"⚠️ No column ID found for '{title}' in subitem '{subitem_name}'")
            continue

        mutation = """
        mutation ($itemId: Int!, $columnId: String!, $value: JSON!) {
          change_column_value(item_id: $itemId, column_id: $columnId, value: $value) {
            id
          }
        }
        """
        variables = {
            "itemId": int(subitem_id),
            "columnId": column_id,
            "value": json.dumps(str(value))
        }

        resp = requests.post(API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
        if "errors" in resp.text:
            print(f"❌ Error setting '{title}' on subitem '{subitem_name}'")
            print(resp.text)

def push_to_monday_quotes_board(parsed):
    job_number = parsed["job_number"]
    vendor = parsed["vendor"]
    items = parsed["items"]

    print(f"✅ Syncing to Monday: Job #{job_number}, Vendor: {vendor}, {len(items)} items")

    parent_item_id = create_sales_quote_item(job_number, vendor)
    if not parent_item_id:
        print("❌ Aborting subitem sync due to missing parent item.")
        return

    for item in items:
        create_subitem(parent_item_id, item)


