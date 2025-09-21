from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from dotenv import load_dotenv
from typing import TypedDict,Annotated,Optional

load_dotenv()
llm=HuggingFaceEndpoint(repo_id="openai/gpt-oss-120b")

model =ChatHuggingFace(llm=llm)

class Review(TypedDict):
    summary:str
    sentiment: str

class Review(TypedDict):
     key_themes: Annotated[list[str], "Write down all the key themes discussed in the review in a list"]
     summary: Annotated[str, "A brief summary of the review"]
     sentiment: Annotated[str, "Return sentiment of the review either negative, positive or neutral"]
     pros: Annotated[Optional[list[str]], "Write down all the pros inside a list"]
     cons: Annotated[Optional[list[str]], "Write down all the pros inside a list"]
     structured_model=model.with_structured_output(Review)

structured_model=model.with_structured_output(Review)
result=structured_model.invoke("""The hardware is great, but the software feels bloated. There are
too many pre-installed apps that I can't remove. Also, the UI looks outdated compared to
other brands. Hoping for a software update to fix this.""")

print(result)