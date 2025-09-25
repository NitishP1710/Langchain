from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

#initialize the llm
llm= OpenAI(model_name="gpt-3.5-turbo",temperature=0)

#create a prompt Template
prompt=PromptTemplate(
    template="suggest cathy title blog about {topic}",
    input_variables=["topic"]
)

#define input
topic=input("Enter a topic: ")
#format prompt with input
formatted_prompt=prompt.format(topic=topic)

#call llm 
blog_title=llm.invoke(formatted_prompt)

print(blog_title)