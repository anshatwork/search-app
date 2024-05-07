import re
import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import rasa 
import requests
from mapp import es
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')
nltk.download('stopwords')

@st.cache(allow_output_mutation=True)
def connect_to_elasticsearch():
  
  try:
    es = Elasticsearch(['http://localhost:9200'])
    print("Successfully connected to Elasticsearch.")
    return es
  except Exception as e:
    print(f"Failed to connect to Elasticsearch: {e}")
    return None
  
rasa_server_url = "http://localhost:5005/webhooks/rest/webhook"



def entity(query):
    payload_data = {
        "sender": "user123",
        "message": query
    }

    response = requests.post(rasa_server_url, json=payload_data)

    
    if response.status_code == 200:
        
        rasa_response = response.json()
        
        
        if rasa_response and len(rasa_response) > 0:
            bot_message = rasa_response[0].get('text', "No response received from Rasa.")

            print("Response from Rasa:", bot_message)
            return  bot_message
        else:
            print("No response received from Rasa.")
    else:
        print("Error:", response.status_code)

indexName = "hkdata1"






def search(input_keyword):
    
    es = connect_to_elasticsearch()
    model = SentenceTransformer('all-mpnet-base-v2')
    vector_of_input_keyword = model.encode(input_keyword)

    query = {
        "field": "embeddings",
        "query_vector": vector_of_input_keyword,
        "k": 500,
        "num_candidates": 1000
    }
    res = es.knn_search(index="hkdata1"
                        , knn=query 
                        , source=["fullName","search_text","br_nm","secondary_category"]
                        )
    results = res["hits"]["hits"]

    return results



def preprocess_text(text):
    # Lowercase the text
    text = text.lower()
    
    # Tokenize the text
    words = word_tokenize(text)
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    stop_words.add('best')
    stop_words.add('wanna')
    stop_words.remove('on')
    
    words = [word for word in words if word not in stop_words]
    
    return " ".join(words)


def main():
    st.title("Search at HealthKart")

    search_query = st.text_input("Enter your search query")
    

    if st.button("Search"):
        query = preprocess_text(search_query)

        text = entity(query)
        
        
        brand_match = ""
        category_match = ""

        words = [word.strip() for word in text.split() if word.strip()]

        # print(len(words))
        for i in range(len(words)):
            if i == len(words) : break
            if  words[i] == 'brand':
                i += 1
                while i<len(words) and words[i]!='and':
                    brand_match += words[i]+ " "
                    i+=1
            if i == len(words): break 
            if  words[i] == 'category':
                i += 1
                while i < len(words) :
                    category_match+=words[i]+ " "
                    i+=1
        
        

        
        brand = None
        category = None

        
        if brand_match and brand_match!='none':
            brand = brand_match
        if category_match and category_match!='none':
            category = category_match

        print(brand)
        print(category)  

        if(category == 'protein') : category = 'proteins'

        if brand : 
            query += " " + brand
        

        results = search(query)
           
        st.subheader("Search Results")
    
        myset = set()
        count = 0
        if brand and category:
            print('hey')
            for result in results:
                
                if count == 26 : break
                if( result['_source']['secondary_category'].lower()!=category.lower().strip() or result['_source']['br_nm'].lower()!=brand.lower().strip()): continue
                count += 1
                myset.add(result['_source']['fullName'])
                with st.container():
                        if '_source' in result:
                            try:
                                st.header(f"{result['_source']['fullName']}")
                            except Exception as e:
                                print(e)
                            
                            try:
                                st.write(f"Description: I am a result of filtering both brand and category")
                            except Exception as e:
                                print(e)
                            try:
                                st.write(f"Brand: {result['_source']['br_nm']}")
                            except Exception as e:
                                print(e)
                            try:
                                st.write(f"Category: {result['_source']['secondary_category']}")
                            except Exception as e:
                                print(e)
                            st.divider()
        if brand:
            for result in results:
                if count == 26 : break
                if(result['_source']['br_nm'].lower()!=brand.lower().strip()): continue
                
                if result['_source']['fullName'] not in myset:
                    with st.container():
                        if '_source' in result:
                            try:
                                st.header(f"{result['_source']['fullName']}")
                            except Exception as e:
                                print(e)
                            
                            try:
                                st.write(f"Description: I am a result of filtering  brand ")
                            except Exception as e:
                                print(e)
                            try:
                                st.write(f"Brand: {result['_source']['br_nm']}")
                            except Exception as e:
                                print(e)
                            try:
                                st.write(f"Category: {result['_source']['secondary_category']}")
                            except Exception as e:
                                print(e)
                            st.divider()
                    myset.add(result['_source']['fullName'])
                    count += 1
        if category:
            for result in results:
                if count == 26 : break
                if(result['_source']['secondary_category'].lower()!=category.lower().strip()): continue
                if result['_source']['fullName'] not in myset:
                    with st.container():
                        if '_source' in result:
                            try:
                                st.header(f"{result['_source']['fullName']}")
                            except Exception as e:
                                print(e)
                            
                            try:
                                st.write(f"Description: I am a result of filtering category ")
                            except Exception as e:
                                print(e)
                            try:
                                st.write(f"Brand: {result['_source']['br_nm']}")
                            except Exception as e:
                                print(e)
                            try:
                                st.write(f"Category: {result['_source']['secondary_category']}")
                            except Exception as e:
                                print(e)
                            st.divider()
                    myset.add(result['_source']['fullName'])
                    count += 1
        for result in results:
            if count == 26 : break 
            if result['_source']['fullName'] not in myset:
                    with st.container():
                        if '_source' in result:
                            try:
                                st.header(f"{result['_source']['fullName']}")
                            except Exception as e:
                                print(e)
                            
                            try:
                                st.write(f"Description: {result['_source']['search_text']}")
                            except Exception as e:
                                print(e)
                            try:
                                st.write(f"Brand: {result['_source']['br_nm']}")
                            except Exception as e:
                                print(e)
                            try:
                                st.write(f"Category: {result['_source']['secondary_category']}")
                            except Exception as e:
                                print(e)
                            st.divider()
                    myset.add(result['_source']['fullName'])
                    count += 1
                    
# Displyin the data on stream
               

    
if __name__ == "__main__":
    main()
