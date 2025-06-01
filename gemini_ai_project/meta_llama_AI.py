from openai import OpenAI
import mysql.connector
from mysql.connector import Error

def metaLlama(prompt, user_id, username):
    sqldb = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="1234",
        database="test_chat_app"
    )
    DB_CONFIG = {
      'host': 'localhost',
      'user': 'root',
      'password': '1234',
      'database': 'test_chat_app'
    }
    sqldb = mysql.connector.connect(**DB_CONFIG)
       
    cursor = sqldb.cursor()

    html_text = ''' Please format your response using only HTML tags. 
                          For example, use <p> for paragraphs, <strong> for bold text, 
                          <em> for italics,  
                          <br> for line breaks and colorful texts
                          and never mention about html tags in your answer'''

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key= "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"
    )

    completion = client.chat.completions.create(
        # model="meta-llama/llama-4-maverick:free",
        model = "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
        messages=[
            {
              "role": "user",
              "content": prompt + html_text
            }
          ]
    )
    try:
      response = completion.choices[0].message.content
    except openai.AuthenticationError as e:
      response = "" + str(e)
      return response
    
    cursor.execute('''INSERT INTO aiChat(user_id, username, prompt, response)
                    VALUES(%s, %s, %s, %s)''',
                  (int(user_id), username, prompt, response))
    sqldb.commit()
    return response
