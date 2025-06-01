import xml.etree.ElementTree as ET

def parse_xml_and_push_to_monday(xml_bytes, vendor: str, markup: float, job_number: str):
    tree = ET.ElementTree(ET.fromstring(xml_bytes))
    root = tree.getroot()
    items = []

    products = root.findall(".//Product")

    for product in products:
        try:
            quantity = int(product.findtext("Qty", "0"))
            list_price = float(product.findtext("ListPrice", "0.0"))
        except ValueError:
            quantity = 0
            list_price = 0.0

        items.append({
            "Item Name": product.findtext("ProductCode", "").strip(),
            "Supplier": vendor,
            "Model": product.findtext("Model", "").strip(),
            "NetSize": product.findtext("NetSize", "").strip(),
            "ItemDesc": product.findtext("ItemDesc", "").strip(),
            "Room": product.findtext("Room", "").strip(),
            "Quantity": quantity,
            "Unit Price (Markup)": round(list_price * markup, 2)
        })

    # Append fixed line items
    items.append({"Item Name": "Install Labor2"})
    items.append({"Item Name": "Lock and Slide2"})

    return {
        "items_parsed": len(items),
        "items": items,
        "job_number": job_number,
        "vendor": vendor
    }
