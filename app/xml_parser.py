import xml.etree.ElementTree as ET

def strip_namespace(tree_root):
    for elem in tree_root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]
    return tree_root

def parse_xml_and_push_to_monday(xml_bytes, vendor: str, markup: float, job_number: str):
    xml_string = xml_bytes.decode("utf-8", errors="ignore")
    lines = xml_string.splitlines()

    try:
        root = strip_namespace(ET.fromstring(xml_string))
        root_tag = root.tag
        child_tags = [child.tag for child in root]
        product_count = len(root.findall(".//Product"))
    except Exception as e:
        return {"error": str(e), "xml_preview": lines[:30]}

    return {
        "status": "diagnostic",
        "job_number": job_number,
        "vendor": vendor,
        "xml_root_tag": root_tag,
        "xml_child_tags": child_tags,
        "product_elements_found": product_count,
        "xml_preview": lines[:30]
    }
