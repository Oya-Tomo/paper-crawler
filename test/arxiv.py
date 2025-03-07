import requests
import re
import xml.etree.ElementTree as ET
import pprint

base_url = "http://export.arxiv.org/api/query"
query = "search_query=all:electron"
response = requests.get(f"{base_url}?{query}")


def xml_to_json(xml: ET.Element):
    # Convert XML to JSON
    def expand_children(node: ET.Element):
        obj = {
            "tag": node.tag.split("}")[1],
            "tag_prefix": re.findall(r"{.*}", node.tag)[0][1:-1],
            "text": node.text,
            "children": [],
        }
        for child in node:
            obj["children"] = obj.get("children", []) + [expand_children(child)]
        return obj

    return expand_children(xml)


root = ET.fromstring(response.text)
json = xml_to_json(root)


pprint.pprint(json)
