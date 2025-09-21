from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
load_dotenv()

llm=HuggingFaceEndpoint(repo_id="openai/gpt-oss-120b",task="text-generation")
model=ChatHuggingFace(llm=llm)
parser=JsonOutputParser()
template=PromptTemplate(
    template="give me name ,age and city of the fictional person \n {format_instruction}",
    input_variables=[],
    partial_variables={"format_instruction":parser.get_format_instructions()}
)

prompt=template.format()

print(prompt)

result=model.invoke(prompt)
print(result.content)
final_result=parser.parse(result.content)
print(final_result)

#for json parser you cant give schema to parse it
#schema is decided by LLm