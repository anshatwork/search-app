import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import requests

import ollama
from langchain_community.llms import Ollama

indexName = "hkdata1"

rasa_server_url = "http://localhost:5005/webhooks/rest/webhook"


def parse_response(response):
    # Split the response into the search query part and the information part
    parts = response.split("kramer")
    
    if len(parts) < 2:
        return "Invalid response format"
    
    search_query = parts[0].strip()
    info_part = parts[1].strip()
    
    brand_match = ""
    category_match = ""
    
    # Split the info part into words
    words = [word.strip() for word in info_part.split() if word.strip()]
    
    # Extract brand and category
    for i in range(len(words)):
        if words[i] == 'brand':
            i += 1
            while i < len(words) and words[i] != 'and':
                brand_match += words[i] + " "
                i += 1
        if i < len(words) and words[i] == 'category':
            i += 1
            while i < len(words):
                category_match += words[i] + " "
                i += 1
    
    brand_match = brand_match.strip()
    category_match = category_match.strip()
    
    # Return the parsed results
    return search_query, brand_match, category_match

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



def get_es_connection():
    try:
        es = Elasticsearch("http://localhost:9200/")
        if es.ping():
            st.session_state.es = es
            print('successfully connected to es')
        else:
            print("Oops! Cannot connect to Elasticsearch!")
    except ConnectionError as e:
        print(f"Connection Error: {e}")

# Ensure Elasticsearch connection is stored in session state
if 'es' not in st.session_state:
    get_es_connection()

# Example usage of the Elasticsearch connection
if 'es' in st.session_state:
    es = st.session_state.es
    # Example operation using the ES connection
    try:
        info = es.info()
        
    except Exception as e:
        st.error(f"Error fetching Elasticsearch info: {e}")


def printres(results,brand,category,N):
    count = 0
    if brand and category:
        for result in results:
            
            if count == N : break
            if( result['_source']['secondary_category'].lower()!=category.lower().strip() or result['_source']['br_nm'].lower()!=brand.lower().strip()): continue
            count += 1
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
            
            if(result['_source']['br_nm'].lower()!=brand.lower().strip()): continue
            if count == N : break
            count +=1
            if result['_source']['fullName']:

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
                
                
    if category:
        for result in results:
            
            if(result['_source']['secondary_category'].lower()!=category.lower().strip()): continue
            if count == N : break
            count +=1
            if result['_source']['fullName']:
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
                
                
    for result in results:
        if count == N : break
        count +=1
        if result['_source']['fullName']:
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
                


def removekaro(input_string):
    return input_string.replace(",", "")

def parse_search_results(input_string: str,results) -> list:
    # print(results)
    colon_index = input_string.rfind(":")

    if colon_index != -1:
        names_string = input_string[colon_index + 1:]
    else:
        names_string = input_string

    names = [name.strip() for name in names_string.split(",")]

    results_list = names[:20]
    
    res = []

    for result in results_list:
        res.append(results[result])

    return res

def context_search(input_keyword):
    
    model = SentenceTransformer('all-mpnet-base-v2')
    vector_of_input_keyword = model.encode(input_keyword)

    
    query = {
            "field": "embeddings",
            "query_vector": vector_of_input_keyword,
            "k": 100,
            "num_candidates": 1000,
            
        }
    res = es.knn_search(index="hkdata1"
                            , knn=query 
                            , source=["fullName","search_text","br_nm","secondary_category","_id"]
                            )
    results = res["hits"]["hits"]

    data_for_llama3 = {}
    appended_string = ""

    for hit in results:
        full_name = removekaro(hit["_source"]["fullName"])
        full_name = full_name.strip()
        data_for_llama3[str(hit["_id"])] = hit
        appended_string += full_name + " " + hit["_id"] + ", " 

    appended_string = appended_string[:-2]  

    llama3_prompt = f"Select the 20 best options from the given options to the question '{input_keyword}':\n{appended_string} just give out the ID which is mentioned just before a comma give them out in a single separated by commas"
    # print(llama3_prompt)
    llm = Ollama(model="llama3")
    res = llm.invoke(llama3_prompt)
    # print(res)
    ans = parse_search_results(res,data_for_llama3)
    # print(ans)
    return ans



def filter(results):
    values = []
    for result in results:
        values.append(result['_id'])
    query = {
  "query": {
    "bool": {
      
      "must": [
        { "ids": { "values":values } }
      ]
    }
  }
}
    res = es.search(index="hkdata1", body=query, size=10)
    ans = res["hits"]["hits"]
    print("Displayed LLM results")
    return ans

def printllm(data):
    st.subheader("Search Results")
    for result in data:
                with st.container():
                    if '_source' in result:
                        try:
                            st.header(f"{result['_source']['fullName']}")
                        except Exception as e:
                            print(e)
                        
                        try:
                            st.write(f"Description: {result['_source']['br_nm']}")
                        except Exception as e:
                            print(e)
                        st.divider()

def search(input_keyword, page):

    query = {
        "query": {
            "multi_match": {
                "query": input_keyword,
                "fields": ["fullName", "search_text", "br_nm"],
                "minimum_should_match": "90%"
            }
        },
        "from" : page*10,
        "size" : 10
    }
    
    res = es.search(index="hkdata1", body=query)
    results = res["hits"]["hits"]
    print("ran query with page no " + str(page) + " for the query " + input_keyword)
    return results



def search_count(input_keyword):

    query = {
        "query": {
            "multi_match": {
                "query": input_keyword,
                "fields": ["fullName", "search_text", "br_nm"],
                "minimum_should_match": "90%"
            }
        },
        
        "size" : 40
    }
    
    res = es.search(index="hkdata1", body=query)
    results = res["hits"]["hits"]
    return results

def fuzzy_search(input_keyword, page):

    query = {
        "query": {
            "multi_match": {
                "query": input_keyword,
                "fields": ["fullName", "search_text", "br_nm"],
                
                "fuzziness" : 2
            }
        },
        "from" : page*10,
        "size" : 10
    }
    
    res = es.search(index="hkdata1", body=query)
    results = res["hits"]["hits"]
    print("ran fuzzy_query with page no " + str(page) + " for the query " + input_keyword)
    return results

def fuzzy_search_count(input_keyword):

    query = {
        "query": {
            "multi_match": {
                "query": input_keyword,
                "fields": ["fullName", "search_text", "br_nm"],
                "minimum_should_match": "80%",
                "fuzziness" : 2
            }
        },
        
        "size" : 40
    }
    
    res = es.search(index="hkdata1", body=query)
    results = res["hits"]["hits"]
    return results



def main():
    st.title("Search at HealthKart")

    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'text' not in st.session_state:
            st.session_state.text = ""
    if 'brand' not in st.session_state:
            st.session_state.brand = None
            st.session_state.categiry = None
    search_query = st.text_input("Enter your search query")
    
    if st.button("Search"):
        st.session_state.search_query = search_query
        
        st.session_state.text = entity(st.session_state.search_query)
        st.session_state.flag = False
        
        st.session_state.search_query,st.session_state.brand,st.session_state.category = parse_response(st.session_state.text) 
        
        

        if st.session_state.brand == 'on ' or st.session_state.brand == 'on':
            st.session_state.search_query += ' optimum nutrition'
        if st.session_state.category == 'category' or st.session_state.category == 'category ' : 
            st.session_state.category = 'proteins'
        if st.session_state.brand == 'optimum nutrition' or st.session_state.brand == 'optimum nutrition ' :
            st.session_state.brand = 'on'

        print(st.session_state.search_query + " " + st.session_state.category)


        st.session_state.page_number = 0  
        st.session_state.total = len(search_count(st.session_state.search_query))
        if st.session_state.total == 0:
            st.session_state.total = len(fuzzy_search_count(st.session_state.search_query))
            st.session_state.flag = True
        st.session_state.search_results = context_search(st.session_state.search_query)

        
    if st.session_state.search_query:
        
        
        N = 10
        
        last_page =  2+(st.session_state.total//N) 
        
        prev, _ ,next = st.columns([5, 10, 5])

        st.session_state.check = 0

        if st.session_state.page_number < last_page :
            if next.button("Next"):
                st.session_state.page_number += 1

        if st.session_state.page_number > 0 :
            if prev.button("Previous"):          
                st.session_state.page_number -= 1

        if st.session_state.page_number > last_page -3:
            st.subheader("LLM results")
            if st.session_state.page_number == last_page -2:
                printllm(filter(st.session_state.search_results[:N+st.session_state.check]))
            else : printllm(filter(st.session_state.search_results[N + st.session_state.check:]))

        
        else :
            if not st.session_state.flag :
                results = search(st.session_state.search_query,st.session_state.page_number)
            else : results = fuzzy_search(st.session_state.search_query,st.session_state.page_number)
            data = results
            if len(results) < N:
                st.session_state.check = N - len(results)
                printres(data,st.session_state.brand,st.session_state.category,N)
                data = filter(st.session_state.search_results[:st.session_state.check])
                printllm(data)
            else : printres(data,st.session_state.brand,st.session_state.category,N)
                    
if __name__ == "__main__":
    main()
