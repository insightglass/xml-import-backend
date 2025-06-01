import xml.etree.ElementTree as ET

def parse_xml_and_push_to_monday(xml_bytes, vendor: str, markup: float, job_number: str):
    tree = ET.ElementTree(ET.fromstring(xml_bytes))
    root = tree.getroot()
    items = []
    for item in root.findall(".//Item"):
        items.append({
            "Item Name": item.findtext("ProductCode"),
            "Supplier": vendor,
            "Model": item.findtext("Model"),
            "NetSize": item.findtext("NetSize"),
            "ItemDesc": item.findtext("ItemDesc"),
            "Room": item.findtext("Room"),
            "Quantity": int(item.findtext("Qty")),
            "Unit Price (Markup)": round(float(item.findtext("ListPrice")) * markup, 2)
        })
    items.append({"Item Name": "Install Labor"})
    items.append({"Item Name": "Lock and Slide"})

    # Placeholder for sending to Monday.com
    return {"items_parsed": len(items), "job_number": job_number, "vendor": vendor}
