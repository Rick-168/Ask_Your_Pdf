from dotenv import load_dotenv
import os

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")


from io import BytesIO
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import tempfile

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain

def info_from_back(pdf_bytes: bytes):
    # 1. Write bytes to a temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        # 2. Load it via PyPDFLoader
        loader = PyPDFLoader(tmp_path)
        data = loader.load()
    finally:
        # 3. Clean up the temp file
        os.remove(tmp_path)

    return data

def pre_process(data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
    text_doc = text_splitter.split_documents(data)
    return text_doc
    


def initialize(text_doc):

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    pinecone_api_key = os.environ.get("PINECONE_API_KEY")

    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "langchain2"  

    # If index not created
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

 
    docsearch = PineconeVectorStore.from_texts([t.page_content for t in text_doc], embeddings, index_name = 'langchain2' )
    return docsearch

   


def get_ans(pdf_bytes: bytes, quest: str) -> str:

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7
    )

    data = info_from_back(pdf_bytes)
    text_doc = pre_process(data)
    docsearch = initialize(text_doc)

    chain = load_qa_chain(llm, chain_type='stuff')
    docs = docsearch.similarity_search(quest)
    answer = chain.run(input_documents = docs, question = quest)

    return answer