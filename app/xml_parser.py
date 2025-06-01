import xml.etree.ElementTree as ET
import html

def parse_xml_and_push_to_monday(xml_bytes, vendor: str, markup: float, job_number: str):
    xml_string = xml_bytes.decode("utf-8", errors="ignore")
    root = ET.fromstring(xml_string)
    items = []

    # Extract and decode <quoteheader> CDATA
    quoteheader = root.find(".//quoteheader")
    if quoteheader is not None and quoteheader.text:
        try:
            # Double-unescape
            step1 = html.unescape(quoteheader.text.strip())
            step2 = html.unescape(step1)
            inner_root = ET.fromstring(step2)

            # Strip namespaces (if any)
            for elem in inner_root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]

            products = inner_root.findall(".//Product")

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

        except Exception as e:
            return {"error": f"Double unescape or inner XML parse failed: {str(e)}"}
    else:
        return {"error": "quoteheader CDATA not found or empty"}

    # Append fixed line items
    items.append({"Item Name": "Install Labor FINAL"})
    items.append({"Item Name": "Lock and Slide FINAL"})

    return {
        "items_parsed": len(items),
        "items": items,
        "job_number": job_number,
        "vendor": vendor
    }
