from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import threading
import time

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Chrome extension

# Global variable to store vector stores for each video
video_vector_stores = {}
video_transcripts = {}

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0, 
    max_tokens=None,
    timeout=None,
    max_retries=2
)

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

prompt = PromptTemplate(
    template="""
    You are a helpful assistance. Answer only from the provided transcript context.
    If the context is insufficient, just say "I don't have enough information about that in the video content."
    
    Context: {context}
    Question: {question}
    """,
    input_variables=["context", "question"]
)

def process_video_transcript(video_id):
    # """Process video transcript and create vector store"""
    try:
       # print(f"Processing transcript for video: {video_id}")
        # Get transcript
        transcript_list = YouTubeTranscriptApi().fetch(video_id)
        transcript = " ".join(chunk.text for chunk in transcript_list)
        
        if not transcript.strip():
            raise ValueError("Empty transcript")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        chunks = splitter.create_documents([transcript])
        
        vector_store = FAISS.from_documents(chunks, embeddings)
        
        # Store for later use
        video_vector_stores[video_id] = vector_store
        video_transcripts[video_id] = transcript
        
        print(f"Successfully processed video: {video_id}")
        return True
        
    except Exception as e:
        print(f"Error processing video {video_id}: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "YouTube AI Chat Assistant"})

@app.route('/initialize', methods=['POST'])
def initialize_chat():
    """Initialize chat with video ID"""
    try:
        data = request.json
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({"error": "Video ID is required"}), 400
            
        # Check if video is already processed
        if video_id in video_vector_stores:
            return jsonify({
                "status": "ready", 
                "message": "Video already processed"
            })
        
        # Process video in background thread
        def process_background():
            process_video_transcript(video_id)
        
        thread = threading.Thread(target=process_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "processing", 
            "message": "Processing video transcript..."
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """Ask a question about the video"""
    try:
        data = request.json
        video_id = data.get('video_id')
        question = data.get('question')
        
        if not video_id or not question:
            return jsonify({"error": "Video ID and question are required"}), 400
            
        # Check if video is processed
        if video_id not in video_vector_stores:
            return jsonify({"error": "Video not processed yet"}), 400
            
        # Get relevant chunks
        vector_store = video_vector_stores[video_id]
        retriever = vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 4}
        )
        
        retrieved_docs = retriever.invoke(question)
        context_txt = "\n\n".join(doc.page_content for doc in retrieved_docs)
        
        # Generate answer
        final_prompt = prompt.invoke({"context": context_txt, "question": question})
        answer = llm.invoke(final_prompt)
        
        return jsonify({"answer": answer.content})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status/<video_id>', methods=['GET'])
def get_video_status(video_id):
    """Get processing status of a video"""
    if video_id in video_vector_stores:
        return jsonify({"status": "ready", "transcript_length": len(video_transcripts.get(video_id, ""))})
    else:
        return jsonify({"status": "processing"})

if __name__ == '__main__':
    print("Starting YouTube AI Chat Assistant Backend Server...")
    print("Make sure to set your GOOGLE_API_KEY in the .env file")
    app.run(host='0.0.0.0', port=5000, debug=True)
