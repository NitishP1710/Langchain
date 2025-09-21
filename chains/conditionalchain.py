from httpx._transports import default
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableParallel,RunnableBranch,RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel,Field
from typing import Literal

load_dotenv()

model=ChatOpenAI()
parser=StrOutputParser()

class Feedback(BaseModel):
    sentiment: Literal["positive","negative"]=Field(description="the sentiment of the feedback")

parser2=PydanticOutputParser(pydantic_object=Feedback)
prompt1=PromptTemplate(
    template="classify the sentiment of following feedback txt into positive or negative \n {feedback} \n {format_instructions}",
    input_variables=['feedback'],
    partial_variables={"format_instructions":parser2.get_format_instructions()}
)

classfier_chain=prompt1 | model | parser2

# result=classfier_chain.invoke({"feedback":"the product is good"})
# print(result)

# branch_chai=RunnableBranch(
#     (condition1,chain1),
#     (condition2,chain2),
#     default chain
# )

prompt2=PromptTemplate(
    template="write an approprite response to this positive feedback \n {feedback}",
    input_variables=['feedback']
)

prompt3=PromptTemplate(
    template="write an approprite response to this negative feedback \n {feedback}",
    input_variables=['feedback']
)

branch_chain=RunnableBranch(
    (lambda x:x["sentiment"]=="positive",prompt2 | model | parser),
    (lambda x:x["sentiment"]=="negative",prompt3 | model | parser),
    RunnableLambda(lambda x:x["feedback"]) 
)


cahin=classfier_chain | branch_chain

result=cahin.invoke({"feedback":"the product is good"})