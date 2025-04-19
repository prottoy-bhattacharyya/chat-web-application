from openai import OpenAI
import mysql.connector
from mysql.connector import Error

def metaLlama(ques):
  sqldb = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="1234",
    database="chat_web_app"
  )
  cursor = sqldb.cursor()

  client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    # api_key="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",
    # api_key="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"
    # api_key= "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"
    # api_key= "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"
    api_key= "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"
  )

  completion = client.chat.completions.create(
    # model="meta-llama/llama-4-maverick:free",
    model = "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
    messages=[
        {
          "role": "user",
          "content": ques
        }
      ]
    )

  response = completion.choices[0].message.content
  cursor.execute('''INSERT INTO aiChat(user_msg, ai_msg)
                 VALUES(%s, %s)''',
                 (ques, response))
  sqldb.commit()
  return response
