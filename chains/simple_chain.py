from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
load_dotenv()

llm=HuggingFaceEndpoint(repo_id="openai/gpt-oss-120b",task="text-generation")
model=ChatHuggingFace(llm=llm)

parser=StrOutputParser()

# 1st- prompt-> detailed report
template1=PromptTemplate(
    template="write a de tailed report on {topic}",
    input_variables=['topic']
)

chain=template1 | model | parser
result=chain.invoke({'topic':'cricket'})
print(result)

chain.get_graph().print_ascii()  #visulize chain 