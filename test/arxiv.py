from dataclasses import dataclass
import requests
import re
import xml.etree.ElementTree as ET
import pprint
import json


def xml_to_json(xml: ET.Element):
    # Convert XML to JSON
    def expand_children(node: ET.Element):
        obj = {
            "tag": node.tag.split("}")[1],
            "tag_prefix": re.findall(r"{.*}", node.tag)[0][1:-1],
            "text": node.text,
            "attributes": node.attrib,
            "children": [],
        }

        for child in node:
            obj["children"] = obj.get("children", []) + [expand_children(child)]
        return obj

    return expand_children(xml)


def xml_to_arxiv_json(xml: ET.Element):
    data = xml_to_json(xml)

    if data["tag"] != "feed":
        raise ValueError("Expected root tag to be 'feed'")

    entries = []

    for child in data["children"]:
        if child["tag"] == "entry":
            entry = {
                "id": None,
                "title": None,
                "summary": None,
                "updated": None,
                "published": None,
                "authors": [],
                "pdf": None,
                "comment": None,
                "journal_ref": None,
                "doi": None,
                "primary_category": None,
                "categories": [],
            }
            for entry_child in child["children"]:
                if entry_child["tag"] == "id":
                    entry["id"] = entry_child["text"]
                elif entry_child["tag"] == "title":
                    entry["title"] = entry_child["text"]
                elif entry_child["tag"] == "summary":
                    entry["summary"] = entry_child["text"]
                elif entry_child["tag"] == "updated":
                    entry["updated"] = entry_child["text"]
                elif entry_child["tag"] == "published":
                    entry["published"] = entry_child["text"]
                elif entry_child["tag"] == "author":
                    author = {
                        "name": None,
                        "affiliation": None,
                    }
                    for author_child in entry_child["children"]:
                        if author_child["tag"] == "name":
                            author["name"] = author_child["text"]
                        elif author_child["tag"] == "affiliation":
                            author["affiliation"] = author_child["text"]
                    entry["authors"].append(author)
                elif entry_child["tag"] == "link":
                    if entry_child["attributes"].get("type", None) == "application/pdf":
                        entry["pdf"] = entry_child["attributes"]["href"]
                elif entry_child["tag"] == "comment":
                    entry["comment"] = entry_child["text"]
                elif entry_child["tag"] == "journal_ref":
                    entry["journal_ref"] = entry_child["text"]
                elif entry_child["tag"] == "doi":
                    entry["doi"] = entry_child["text"]
                elif entry_child["tag"] == "primary_category":
                    entry["primary_category"] = entry_child["attributes"]["term"]
                elif entry_child["tag"] == "category":
                    entry["categories"].append(entry_child["attributes"]["term"])
            entries.append(entry)
    return entries


def extract_arxiv_id(id: str):
    return re.match(r"^(http|https)://arxiv.org/abs/(.*)(v\d)", id).group(2)


if __name__ == "__main__":
    base_url = "http://export.arxiv.org/api/query"
    query = "search_query=all:electron"
    response = requests.get(f"{base_url}?{query}")

    pprint.pprint(xml_to_json(ET.fromstring(response.text)))
    pprint.pprint(xml_to_arxiv_json(ET.fromstring(response.text)))

    print(extract_arxiv_id("http://arxiv.org/abs/cond-mat/0310615v1"))
    print(extract_arxiv_id("http://arxiv.org/abs/2010.01066v1"))
