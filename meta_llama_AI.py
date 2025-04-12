from openai import OpenAI
import mysql.connector

def metaLlama(ques):
  sqldb = mysql.connector.connect(
    host="localhost",
    user="root",
    # password="1234",
    database="chat_web_app"
  )
  cursor = sqldb.cursor()

  client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
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
