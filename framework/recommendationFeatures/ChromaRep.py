import chromadb


class ChromaRep:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="./chroma"
        )

        self.collection = self.client.get_or_create_collection(
            name="authors"
        )
    
    def upsert(
        self,
        author_id: str,
        author_name: str,
        summary: str,
        embedding: list[float],
    ):
        self.collection.upsert(
            ids=[author_id],
            documents=[summary],
            embeddings=[embedding],
            metadatas=[
                {
                    "author": author_name,
                }
            ],
        )

    def similar(
        self,
        embedding: list[float],
        limit: int = 10,
    ):
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=limit,
        )

        ids = result["ids"][0]
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]

        return [
            {
                "id": author_id,
                "author": metadata["author"],
                "summary": document,
                "distance": distance,
            }
            for author_id, document, metadata, distance in zip(
                ids,
                documents,
                metadatas,
                distances,
            )
        ]
    
    def get(
        self,
        author_id: str,
    ):
        return self.collection.get(
            ids=[author_id],
            include=["embeddings", "documents", "metadatas"],
        )
    
    def delete(
        self,
        author_id: str,
    ):
        self.collection.delete(
            ids=[author_id]
        )

    def reset(self):
        self.client.delete_collection("authors")

        self.collection = self.client.get_or_create_collection(
            name="authors"
        )
    
    def get_embedding(
        self,
        author_id: str,
    ):
        result = self.collection.get(
            ids=[author_id],
            include=["embeddings"],
        )
        embeddings = result.get("embeddings")
        if embeddings is None or len(embeddings) == 0:   
            return None
        
        return embeddings[0]