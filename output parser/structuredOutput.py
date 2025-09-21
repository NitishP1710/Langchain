from tempfile import template
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser,ResponseSchema
load_dotenv()

llm=HuggingFaceEndpoint(repo_id="openai/gpt-oss-120b",task="text-generation")
model=ChatHuggingFace(llm=llm)

schema=[
    ResponseSchema(name="fact_1" ,description="fact 1 about the person"),
    ResponseSchema(name="fact_2" ,description="fact 2 about the person"),
    ResponseSchema(name="fact_3" ,description="fact 3 about the person"),
    ResponseSchema(name="fact_4" ,description="fact 4 about the person")    
]
parser=StructuredOutputParser.from_response_schemas(schema)
template=PromptTemplate(
    template="give me 4 facts about {topic} \n {format_instruction}",
    input_variables=["topic"],
    partial_variables={"format_instruction":parser.get_format_instructions()}
)

prompt=template.format(topic="black hole")

result=model.invoke(prompt)
final_result=parser.parse(result.content)
print(final_result)