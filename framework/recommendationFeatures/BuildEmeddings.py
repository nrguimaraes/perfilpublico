class BuildEmbeddings:

    def __init__(
        self,
        author_collection,
        article_fetcher,
        summarizer,
        mistral,
        repository,
    ):
        self.author_collection = author_collection
        self.article_fetcher = article_fetcher
        self.summarizer = summarizer
        self.mistral = mistral
        self.repository = repository


    def build(self):
        authors = self.author_collection.find(
            {},
            {
                "_id": 1,
                "Name": 1,
            },
        )

        for author in authors:
            print(f"{author['Name']}")
            try:
                self._build_author(author)
            except Exception as e:
                print(f"Erro em {author['Name']}: {e}")


    def _build_author(self, author):
        author_id = str(author["_id"])
        author_name = author["Name"]

        print(f"Generating {author_name}")
        
        articles = self.article_fetcher.fetch(
            author_name,
            limit=30,
        )

        if not articles:
            return

        prompt = self.summarizer.build(
            author_name,
            articles,
        )

        summary = self.mistral.generate(prompt)

        embedding = self.mistral.embed(summary)

        self.repository.upsert(
            author_id=author_id,
            author_name=author_name,
            summary=summary,
            embedding=embedding,
        )

