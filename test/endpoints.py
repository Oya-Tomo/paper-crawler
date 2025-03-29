import requests
import pprint


result = requests.post(
    "http://0.0.0.0:8080/create",
    json={
        "id": "test_id",
        "title": "test_title",
        "abstract": "test_abstract",
        "authors": ["test_author"],
        "organizations": ["test_organization"],
        "url": "test_url",
        "pdf": "test_pdf",
        "journal": None,
        "doi": None,
        "published_at": "2023-10-01T00:00:00",
        "updated_at": "2023-10-01T00:00:00",
    },
)
pprint.pprint(result.json())

result = requests.get(
    "http://0.0.0.0:8080/get",
    json={"id": "test_id"},
)

pprint.pprint(result.json())

result = requests.post(
    "http://0.0.0.0:8080/search",
    json={
        "queries": [
            {"column": "id", "value": "test"},
        ],
        "limit": 1,
        "offset": 0,
    },
)

pprint.pprint(result.json())

result = requests.put(
    "http://0.0.0.0:8080/update",
    json={
        "id": "test_id",
        "title": "updated_title",
        "abstract": "updated_abstract",
        "authors": ["updated_author"],
        "organizations": ["updated_organization"],
        "url": "updated_url",
        "pdf": "updated_pdf",
        "journal": None,
        "doi": None,
        "published_at": "2023-10-01T00:00:00",
        "updated_at": "2023-10-01T00:00:00",
    },
)
pprint.pprint(result.json())

result = requests.get(
    "http://0.0.0.0:8080/get",
    json={"id": "test_id"},
)

pprint.pprint(result.json())

result = requests.delete(
    "http://0.0.0.0:8080/delete",
    json={"id": "test_id"},
)
pprint.pprint(result.json())
