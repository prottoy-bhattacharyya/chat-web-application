from openai import OpenAI
import mysql.connector
from mysql.connector import Error

def metaLlama(prompt, username):
    sqldb = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="1234",
        database="chat_web_app"
    )
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
    
    response = completion.choices[0].message.content
    cursor.execute('''INSERT INTO aiChat(username, user_msg, ai_msg)
                    VALUES(%s, %s, %s)''',
                  (username, prompt, response))
    sqldb.commit()
    return response
