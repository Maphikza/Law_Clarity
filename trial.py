# import os
# import openai
# from pprint import pprint
#
# openai.api_key = os.getenv("OPENAI_API_KEY")
# response = openai.Completion.create(
#     model="code-davinci-002",
#     prompt="\"\"\"\n1. Create a flask-sqlalchemy database that will save input and output values of completion.\n\"\"\"",
#     temperature=0,
#     max_tokens=256,
#     top_p=1,
#     frequency_penalty=0,
#     presence_penalty=0
# )
#
# print(response["choices"][0]["text"])

def love():
    print("I love you baby")


love()
