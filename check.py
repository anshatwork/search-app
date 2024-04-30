from webbrowser import get
from elasticsearch import Elasticsearch
import warnings
import json
from sentence_transformers import SentenceTransformer
import os
# warnings.simplefilter('ignore')

# warnings.simplefilter('ignore')

# os.environ["CURL_CA_BUNDLE"]=''
# model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# text = 'hi rand'

# x = model.encode(text)
es = Elasticsearch(
    "http://localhost:9200/"
)
if not es.ping():
    raise BaseException("Connection failed")


if es.ping():
    print("Succesfully connected to ElasticSearch!!")
else:
    print("Oops!! Can not connect to Elasticsearch!")


index_name = 'index'
newIndex = 'data'
vectortext = '_source_search_text'

try:
  # Check connection
  if not es.ping():
    raise BaseException("Connection failed")

  # Get mappings for the existing index
  mappings = es.indices.get_mapping(index=index_name)

  # Extract the actual mapping definition (usually under 'properties')
  if index_name in mappings:
      index_mappings = mappings[index_name]["mappings"]
  else:
      raise ValueError(f"Index '{index_name}' not found!")

  # Write mappings to a new Python file
  with open("map.py", "w") as f:
      json.dump(index_mappings, f, indent=4)
      print(f"Mappings for index '{index_name}' written to mappings.py")
except Exception as e:
  print(f"Error retrieving mappings: {e}")