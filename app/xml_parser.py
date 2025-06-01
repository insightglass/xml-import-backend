import xml.etree.ElementTree as ET

def parse_xml_and_push_to_monday(xml_bytes, vendor: str, markup: float, job_number: str):
    tree = ET.ElementTree(ET.fromstring(xml_bytes))
    root = tree.getroot()
    root_tag = root.tag

    # Extract namespace
    ns_uri = root_tag.split('}')[0].strip('{') if '}' in root_tag else ''
    ns = {'ns': ns_uri} if ns_uri else {}

    product_tags = []
    items = []

    products = root.findall(".//ns:Product", ns) if ns else root.findall(".//Product")

    for product in products:
        try:
            quantity = int(product.findtext("ns:Qty", "0", namespaces=ns)) if ns else int(product.findtext("Qty", "0"))
            list_price = float(product.findtext("ns:ListPrice", "0.0", namespaces=ns)) if ns else float(product.findtext("ListPrice", "0.0"))
        except ValueError:
            quantity = 0
            list_price = 0.0

        product_code = product.findtext("ns:ProductCode", "", namespaces=ns) if ns else product.findtext("ProductCode", "")
        product_tags.append(product_code)

        items.append({
            "Item Name": product_code.strip(),
            "Supplier": vendor,
            "Model": product.findtext("ns:Model", "", namespaces=ns).strip() if ns else product.findtext("Model", "").strip(),
            "NetSize": product.findtext("ns:NetSize", "", namespaces=ns).strip() if ns else product.findtext("NetSize", "").strip(),
            "ItemDesc": product.findtext("ns:ItemDesc", "", namespaces=ns).strip() if ns else product.findtext("ItemDesc", "").strip(),
            "Room": product.findtext("ns:Room", "", namespaces=ns).strip() if ns else product.findtext("Room", "").strip(),
            "Quantity": quantity,
            "Unit Price (Markup)": round(list_price * markup, 2)
        })

    # Append fixed line items
    items.append({"Item Name": "Install Labor"})
    items.append({"Item Name": "Lock and Slide"})

    return {
        "items_parsed": len(items),
        "product_codes_found": product_tags,
        "xml_root_tag": root_tag,
        "xml_namespace_uri": ns_uri,
        "job_number": job_number,
        "vendor": vendor
    }
