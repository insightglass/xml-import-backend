import xml.etree.ElementTree as ET

def parse_xml_and_push_to_monday(xml_bytes, vendor: str, markup: float, job_number: str):
    tree = ET.ElementTree(ET.fromstring(xml_bytes.decode("utf-8", errors="ignore")))
    root = tree.getroot()
    items = []

    for lineitem in root.findall(".//lineitem"):
        # NetSize
        frame_width = lineitem.find("FrameWidth").get("Value", "").strip() if lineitem.find("FrameWidth") is not None else ""
        frame_height = lineitem.find("FrameHeight").get("Value", "").strip() if lineitem.find("FrameHeight") is not None else ""
        net_size = f"{frame_width} x {frame_height}" if frame_width and frame_height else ""

        # Basic fields
        qty = lineitem.find("quantity").get("Value", "").strip() if lineitem.find("quantity") is not None else "0"
        list_price = lineitem.find("listprice").get("Value", "").strip() if lineitem.find("listprice") is not None else "0.0"
        model = lineitem.find("category1").get("Value", "").strip() if lineitem.find("category1") is not None else ""
        item_desc = lineitem.findtext("description", "").strip()
        room = lineitem.findtext("room", "").strip()

        # Product codes
        product_codes = [
            w.findtext("productcode", "").strip()
            for w in lineitem.findall(".//extradata/windows/window")
        ]
        product_code_str = ", ".join(filter(None, product_codes))

        try:
            quantity_val = int(qty)
            list_price_val = float(list_price)
        except ValueError:
            quantity_val = 0
            list_price_val = 0.0

        items.append({
            "Item Name": product_code_str,
            "Supplier": vendor,
            "Model": model,
            "NetSize": net_size,
            "ItemDesc": item_desc,
            "Room": room,
            "Quantity": quantity_val,
            "Unit Price (Markup)": round(list_price_val * markup, 2)
        })

    # Append final line items
    items.append({"Item Name": "Install Labor Amsco"})
    items.append({"Item Name": "Lock and Slide Amsco"})

    return {
        "items_parsed": len(items),
        "items": items,
        "job_number": job_number,
        "vendor": vendor
    }
