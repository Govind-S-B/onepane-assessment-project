# COPY OF MAIN COMPATIBLE WITH OPENCHAT BASED MODELS
# starling-lm
# openchat:7b-v3.5-q4_K_M

import re
import sqlite3
import csv
import requests
import json

def table_creation(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hardware (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('CPU', 'GPU', 'RAM', 'SSD', 'Motherboard', 'Power Supply', 'Cooling System')),  -- Constrained hardware types
    model TEXT NOT NULL,
    cost INTEGER NOT NULL,
    num_buyers INTEGER NOT NULL,
    region TEXT NOT NULL CHECK(region IN ('Africa', 'Asia', 'Australia', 'Europe', 'Middle East', 'North America', 'South America')),
    brand TEXT NOT NULL
    )""")

def table_data_entry(cur):
    data = []
    with open("data.csv", 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]

    for row in data:
        cur.execute('''
            INSERT INTO hardware (type, model, cost, num_buyers, region, brand)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (row['Hardware'], row['Model'], row['Cost (USD)'], row['Number of Buyers'], row['Region'], row['Brand']))

def llm_inference(prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "openchat:7b-v3.5-q4_K_M",
        "prompt": prompt,
        "raw": True,
        "stream": False,
        "format": "json",
        "options":{
            "temperature":0
        }
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        response_data = json.loads(response.text)["response"]
        return response_data
    else:
        print(f"Request failed with status code {response.status_code}")
        pass

def execute_db_query(cur,query):
    cur.execute(query)
    rows = cur.fetchall()

    column_names = [description[0] for description in cur.description]

    result_str = ""
    for row in rows:
        result_str += ', '.join(str(value) for value in row) + '\n'

    if result_str == "":
        result_str = "None"

    return [column_names,result_str]

def qn_process_pipeline(cur,question):
    query_prompt = (
    """You are an expert SQL query generation model that analyzes any user question and creats appropriate queries when given the database schema.<|end_of_turn|>
    User : 
    For the given SQL database of schema : 

    CREATE TABLE IF NOT EXISTS hardware (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK(type IN ('CPU', 'GPU', 'RAM', 'SSD', 'Motherboard', 'Power Supply', 'Cooling System')),  -- Constrained hardware types
        model TEXT NOT NULL,
        cost INTEGER NOT NULL,
        num_buyers INTEGER NOT NULL,
        region TEXT NOT NULL CHECK(region IN ('Africa', 'Asia', 'Australia', 'Europe', 'Middle East', 'North America', 'South America')),
        brand TEXT NOT NULL )

    Form an SQL query answering the following user question :"""
    f"{question} "
    """

    The response should be just the SQL query and nothing else in the following json format

    {
    "reasoning" : how the query must be formed and thinking in step by step about what the question is asking
    "query" : the sql query to be made
    }

    <|end_of_turn|>
    Assistant :
    """)

    print(question)

    json_response = llm_inference(query_prompt)
    print(json_response)
    cleaned_json_string =  re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', json_response)
    print(cleaned_json_string)
    query = json.loads(cleaned_json_string)["query"]
    sql_response = execute_db_query(cur,query)
    print(sql_response)

    clean_up_prompt = (
    """You are an SQL expert and professional data analyst, you are also very good at reading sql query output and interpretting 
    them for the users and let them make sense of the data you get<|end_of_turn|>
    User : 
    For the following database schema
    ====
    CREATE TABLE IF NOT EXISTS hardware (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK(type IN ('CPU', 'GPU', 'RAM', 'SSD', 'Motherboard', 'Power Supply', 'Cooling System')),  -- Constrained hardware types
        model TEXT NOT NULL,
        cost INTEGER NOT NULL,
        num_buyers INTEGER NOT NULL,
        region TEXT NOT NULL CHECK(region IN ('Africa', 'Asia', 'Australia', 'Europe', 'Middle East', 'North America', 'South America')),
        brand TEXT NOT NULL )
    ====

    To answer the following question
    ===="""
    f" {question} "
    """====

    The following query was run
    ===="""
    f" {query} "
    """====

    The output of the query was
    ===="""
    f" {sql_response[1]} "
    """ ====

    Try and make sense of the data that was received and give output in common english. Dont make up any data and report as it is, if the data received is None report
    that there are currently no records in the database satisfying this specific query

    The response should be in the following json format containing reasoning and msg

    {
    "reasoning" : how the output from query makes sense for the question and thinking in step by step
    "msg" : a short concise answer for the users question from the reasoning done just now
    }

    <|end_of_turn|>
    Assistant : 
    """
    )
    
    json_response = llm_inference(clean_up_prompt)
    print(json_response)
    cleaned_json_string =  re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ',json_response)
    print(cleaned_json_string)
    user_msg = json.loads(cleaned_json_string)["msg"]

    print("===========================================================")
    return user_msg



con = sqlite3.connect("tutorial.db")
cur = con.cursor()
table_creation(cur)
table_data_entry(cur)

questions = [
    "What brand of GPU has the highest sales in Europe?",
    "Calculate the average cost of SSDs in the Asia region.",
    "Identify the total number of RAM units sold in North America and the corresponding brand.",
    "Determine the least expensive cooling system model and its most popular region.",
    "List the hardware types and brands that have a buyer count exceeding 200 in Africa.",
    "Rank the top three most sold hardware types in South America and their manufacturers."
]

for question in questions:
    qn_process_pipeline(cur,question)

con.commit()
con.close()