import xml.etree.ElementTree as ET

def strip_namespace(tree_root):
    for elem in tree_root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]
    return tree_root

def parse_xml_and_push_to_monday(xml_bytes, vendor: str, markup: float, job_number: str):
    xml_string = xml_bytes.decode("utf-8")
    root = strip_namespace(ET.fromstring(xml_string))
    items = []

    for product in root.findall(".//Product"):
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
    items.append({"Item Name": "Install Labor5"})
    items.append({"Item Name": "Lock and Slide5"})

    return {
        "items_parsed": len(items),
        "items": items,
        "job_number": job_number,
        "vendor": vendor
    }
