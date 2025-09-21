from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from dotenv import load_dotenv
import os

load_dotenv()

# hf_token = os.getenv("TOKEN1")
# if not hf_token:
#     raise ValueError("HUGGINGFACEHUB_API_TOKEN missing in .env")

# No need for task=, it auto-detects for flan-t5
llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-120b",
    # huggingfacehub_api_token=hf_token,
    max_new_tokens=100
)

model=ChatHuggingFace(llm=llm)
result = model.invoke("What is the capital of India?")
print(result.content)
