from elasticsearch import Elasticsearch
import pandas as pd
from mapp import indexMapping
from sentence_transformers import SentenceTransformer

es = Elasticsearch(
    "https://localhost:9200"
)
es.ping()

df = pd.read_csv("data.csv")
df.head()
df.fillna("None", inplace=True)

model = SentenceTransformer('all-mpnet-base-v2')

df["embeddings"] = df["_source.search_text"].apply(lambda x: model.encode(x))

df.head()

es.indices.create(index="all_products", mappings=indexMapping)

record_list = df.to_dict("records")
for record in record_list:
    try:
        es.index(index="all_products", document=record, id=record["_idx"])
    except Exception as e:
        print(e)

es.count(index="all_products")