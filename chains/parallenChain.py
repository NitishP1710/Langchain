from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableParallel

load_dotenv()

model1=ChatOpenAI()
model2=ChatAnthropic(model="claude-3-5-sonnet-20240620")

prompt1=PromptTemplate(
    template="Generate short and simple noted from the following text:/n {text}",
    input_variables=['text']
)
prompt2=PromptTemplate(
    template="GenerATE 5 short questions from following text:/n {text}",
    input_variables=['text']
)

prompt3=PromptTemplate(
    template="merge the provided notes and questions into a single document \n notes-> {notes}\nquestions-> {questions}",
    input_variables=['notes','questions'])

parser=StrOutputParser()

parallel_chain=RunnableParallel(
    {
        "notes":prompt1 | model1 | parser,
        "questions":prompt2 | model2 | parser
    }
)

merge_chain=prompt3 | model1 | parser

chain=parallel_chain | merge_chain

text=""""""

chain.invoke({"text":text})


