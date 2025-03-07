import requests
import xml.etree.ElementTree as ET

base_url = "http://export.arxiv.org/api/query"
query = "search_query=all:electron"
response = requests.get(f"{base_url}?{query}")
print(response.text)


def expand_children(node: ET.Element):
    for child in node:
        print(child.tag, child.attrib, child.text)
        expand_children(child)


root = ET.fromstring(response.text)
expand_children(root)
