from langchain_core.messages import SystemMessage,AIMessage,HumanMessage
from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from dotenv import load_dotenv
#system message is promp which sent innitiall before conversation begin
load_dotenv()

llm= HuggingFaceEndpoint(repo_id="openai/gpt-oss-120b",task="text-generation")
model=ChatHuggingFace(llm=llm)

messages=[
    SystemMessage(content="you are a guradian of this world"),
    HumanMessage(content="Can you save this world?")
]
result=model.invoke(messages)
messages.append(AIMessage(content=result.content) )
print(messages)