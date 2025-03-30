import requests
import pprint


result = requests.post(
    "http://0.0.0.0:8080/create",
    json={
        "id": "2503.21782",
        "src": "arxiv",
        "title": "Mobile-VideoGPT: Fast and Accurate Video Understanding Language Model",
        "abstract": "  Video understanding models often struggle with high computational\nrequirements, extensive parameter counts, and slow inference speed, making them\ninefficient for practical use. To tackle these challenges, we propose\nMobile-VideoGPT, an efficient multimodal framework designed to operate with\nfewer than a billion parameters. Unlike traditional video large multimodal\nmodels (LMMs), Mobile-VideoGPT consists of lightweight dual visual encoders,\nefficient projectors, and a small language model (SLM), enabling real-time\nthroughput. To further improve efficiency, we present an Attention-Based Frame\nScoring mechanism to select the key-frames, along with an efficient token\nprojector that prunes redundant visual tokens and preserves essential\ncontextual cues. We evaluate our model across well-established six video\nunderstanding benchmarks (e.g., MVBench, EgoSchema, NextQA, and PercepTest).\nOur results show that Mobile-VideoGPT-0.5B can generate up to 46 tokens per\nsecond while outperforming existing state-of-the-art 0.5B-parameter models by 6\npoints on average with 40% fewer parameters and more than 2x higher throughput.\nOur code and models are publicly available at:\nhttps://github.com/Amshaker/Mobile-VideoGPT.\n",
        "authors": [
            "Abdelrahman Shaker",
            "Muhammad Maaz",
            "Chenhui Gou",
            "Hamid Rezatofighi",
            "Salman Khan",
            "Fahad Shahbaz Khan",
        ],
        "organizations": [],
        "url": "http://arxiv.org/abs/2503.21782v1",
        "pdf": "http://arxiv.org/pdf/2503.21782v1",
        "journal": None,
        "doi": None,
        "published_at": "2025-03-27T17:59:58Z",
        "updated_at": "2025-03-27T17:59:58Z",
    },
)
pprint.pprint(result.json())

result = requests.get(
    "http://0.0.0.0:8080/get",
    json={
        "id": "2503.21782",
        "src": "arxiv",
    },
)

pprint.pprint(result.json())

result = requests.post(
    "http://0.0.0.0:8080/search",
    json={
        "queries": [
            {"column": "id", "value": "2503.21782"},
        ],
        "limit": 1,
        "offset": 0,
    },
)

pprint.pprint(result.json())

result = requests.put(
    "http://0.0.0.0:8080/update",
    json={
        "id": "2503.21782",
        "src": "arxiv",
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
    json={
        "id": "2503.21782",
        "src": "arxiv",
    },
)

pprint.pprint(result.json())

result = requests.delete(
    "http://0.0.0.0:8080/delete",
    json={
        "id": "2503.21782",
        "src": "arxiv",
    },
)
pprint.pprint(result.json())
