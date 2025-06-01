import xml.etree.ElementTree as ET

def parse_xml_and_push_to_monday(xml_bytes, vendor: str, markup: float, job_number: str):
    tree = ET.ElementTree(ET.fromstring(xml_bytes))
    root = tree.getroot()

    # Extract namespace
    ns = {'ns': root.tag.split('}')[0].strip('{')}
    items = []

    for product in root.findall(".//ns:Product", ns):
        try:
            quantity = int(product.findtext("ns:Qty", "0", namespaces=ns))
            list_price = float(product.findtext("ns:ListPrice", "0.0", namespaces=ns))
        except ValueError:
            quantity = 0
            list_price = 0.0

        items.append({
            "Item Name": product.findtext("ns:ProductCode", "", namespaces=ns).strip(),
            "Supplier": vendor,
            "Model": product.findtext("ns:Model", "", namespaces=ns).strip(),
            "NetSize": product.findtext("ns:NetSize", "", namespaces=ns).strip(),
            "ItemDesc": product.findtext("ns:ItemDesc", "", namespaces=ns).strip(),
            "Room": product.findtext("ns:Room", "", namespaces=ns).strip(),
            "Quantity": quantity,
            "Unit Price (Markup)": round(list_price * markup, 2)
        })

    # Append fixed line items
    items.append({"Item Name": "Install Labor"})
    items.append({"Item Name": "Lock and Slide"})

    return {
        "items_parsed": len(items),
        "items": items,
        "job_number": job_number,
        "vendor": vendor
    }
