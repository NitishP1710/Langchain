from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm=HuggingFaceEndpoint(repo_id="openai/gpt-oss-120b",task="text-generation")
model=ChatHuggingFace(llm=llm)
chat_history=[
    SystemMessage(content="You are a math expert")
]
while True:
    user_input=input("Me :")
    chat_history.append(HumanMessage(content=user_input))
    if(user_input=="exit"):
        break
    result=model.invoke(chat_history)
    chat_history.append(AIMessage(content=result.content))
    print("AI :",result.content)
print(chat_history)  