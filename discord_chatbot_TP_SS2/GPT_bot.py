import openai
from openai import ChatCompletion, OpenAI, AsyncOpenAI


OPENAI_API_KEY = "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"

# Initialisation du client OpenAI
openai.api_key = OPENAI_API_KEY
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Function to get response from OpenAI
async def openai_chatbot(user_message):
    openai_response = await openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message},
        ]
    )
    return openai_response['choices'][0]['message']['content']



"""openai.api_key = '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'
async def openai_chatbot(user_message):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=user_message,
        max_tokens=3000,
        temperature=0.7
    )

    output = response["choices"][0]["text"]
    return output
"""