from pathlib import Path

import chromadb


BASE_DIR = Path(__file__).resolve().parents[3]
CHROMA_PATH = BASE_DIR / "chroma"

client = chromadb.PersistentClient(path=str(CHROMA_PATH))

collection = client.get_or_create_collection(name="authors")

print(CHROMA_PATH)
print(collection.count())
result = collection.peek(limit=5)
print(result["ids"])


def get_embedding(author_id: str):
    result = collection.get(
        ids=[author_id],
        include=["embeddings"],
    )

    embeddings = result.get("embeddings")

    if embeddings is None or len(embeddings) == 0:
        return None

    return embeddings[0]


def get_similar_authors(
    embedding,
    limit: int = 10,
):
    result = collection.query(
        query_embeddings=[embedding],
        n_results=limit,
    )

    authors = []

    ids = result["ids"][0]
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    for author_id, summary, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        authors.append(
            {
                "id": author_id,
                "author": metadata["author"],
                "summary": summary,
                "distance": distance,
            }
        )

    return authors