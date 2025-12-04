from langchain_core import embeddings
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
#Documnet ingestion
video_id = "1bUy-1hGZpI"
try:
    transcript_list = YouTubeTranscriptApi().fetch(video_id)
    transcript = " ".join(chunk.text for chunk in transcript_list)
    print(transcript)  # preview first 500 chars
except TranscriptsDisabled:
    print("Transcript is disabled for this video")

#splitting text into chunk

print("\n##########################################################\n")
splitter=RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks=splitter.create_documents([transcript])

#embedding
embeddings=GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
vector_store=FAISS.from_documents(chunks,embeddings)

retriever=vector_store.as_retriever(search_type="similarity",search_kwargs={"k":4})

retriever.invoke("What is Langchain")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0,max_tokens=None,timeout=None,
  max_retries=2,
    # other params...
)

prompt=PromptTemplate(
    template="""
    you are a helpful assistance Answer only from the provided transcript context
    if context is insufficient just say dont know
    {context}
    Question :{question}
    """,
    input_variables=["context","question"]
)

question ="what is the topic of the video?"
retrieved_docs=retriever.invoke(question)

context_txt="\n\n".join(doc.page_content for doc in retrieved_docs)
final_prompt=prompt.invoke({"context":context_txt,"question":question})


answer=llm.invoke(final_prompt)
print(answer.content)
