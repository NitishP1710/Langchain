from langchain_community.document_loaders import PyPDFLoader

loader=PyPDFLoader("Resume.pdf")
docs=loader.load()
print(docs)