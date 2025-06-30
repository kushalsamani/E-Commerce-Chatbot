from groq import Groq
import os
import re
import sqlite3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()
GROQ_MODEL = os.getenv('GROQ_MODEL')
db_path = Path(__file__).parent / ("db.sqlite")
client_sql = Groq()

sql_prompt = """ You are an expert in understanding the database schema and generating SQL Queries for a natural language question
asked pertaining to the data you have. The schema is provided in the schema tags.

<schema>
table: product

fields: 
product_link - string (hyperlink to product)
title - string (name of the product)
brand - string (brand of the product)
price - integer (price of the product in Indian Rupees)
discount - float (discount on the product. 10 percent discount is represented as 0.1, 20 percent as 0.2)
avg_rating - float (average rating of the product. Range 0-5, 5 is the highest.)
total_ratings - integer (total number of ratings for the product)

</schema>
Make sure whenever you try to search for the brand name, the name can be in any case. So, make sure to use %LIKE to find the brand in condition.
You will be heavily penalized for writing inaccurate SQL queries. Never use "ILIKE".

Create a single SQL query for the question provided. 
The query should have all the fields in SELECT clause (i.e. SELECT *)
Just the SQL Query is needed, nothing more. 
Always provide the SQL in between the <SQL></SQL> tags.
"""

def generate_sql_query(question):

    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": sql_prompt,
            },
            {
                "role": "user",
                "content": question,
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature = 0.2,
        #max_tokens = 1024
    )

    return chat_completion.choices[0].message.content


def run_query(query):
    if query.strip().upper().startswith("SELECT"):
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn)
            return df


def sql_chain(question):
    sql_query = generate_sql_query(question)

    pattern = "<SQL>(.*)</SQL>"
    matches = re.findall(pattern, sql_query, re.DOTALL)
    if len(matches) == 0:
        return "Sorry, LLM is not able to generate a query for your question"

    print("SQL QUERY:", matches[0].strip())
    response = run_query(matches[0].strip())
    if response is None:
        return "Sorry, there was a problem executing SQL query"

    context = response.to_dict(orient='records')
    answer = data_comprehension(question, context)
    return answer



comprehension_prompt = """You are an expert in understanding the context of the question and replying based on the data
pertaining to the question provided. You will be provided with the QUESTION: and DATA: The data will be in the form of an array, 
or a dataframe or a dictionary. Reply based on only the data provided as DATA for answering the question asked as QUESTION.
Donot write anything like 'Based on the Data' or any other technical words. Just a plain simple natural language response.
The data would always be in the context of the question asked. For example, if the question is 'What is the average rating?' and the 
data is '4.3', then answer should be 'The average rating for the product is 4.3.' So make sure the response is curated with the question and the data.
Make sure to note the column names to have some context, if needed, for your response. There can also be cases where you are given the entire dataframe
in the DATA: field. Always remember that the data field contains answers for the questions asked. All you need to do is always reply in the following format
when asked about the product: Product title, price in indian rupees, discount, and rating and then product link. Take care that all the products
follow list format, one line after another. Not as a paragraph.

For example: 
1. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
2. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
3. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
"""

def data_comprehension(question, context):

    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": comprehension_prompt,
            },
            {
                "role": "user",
                "content": f"QUESTION: {question}, DATA: {context}",
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature = 0.2,
        # max_tokens = 1024
    )

    return chat_completion.choices[0].message.content
        



if __name__ == '__main__':

    question = "Give me PUMA shoes with rating higher than 4.5 and more than 30% discount"
    answer = sql_chain(question)
    print(answer)
    #df = run_query(query)
    #pass
