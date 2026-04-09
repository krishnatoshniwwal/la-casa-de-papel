import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma

# Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

class HeistBrain:
    def __init__(self):
        # 1. Keep the embedding model (it's working fine)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", 
            google_api_key=api_key,
            task_type="retrieval_document"
        )
        
        # 2. SWITCH to 'gemini-flash-latest' from your list
        # This usually points to a very stable version with a fresh quota
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-flash-latest", # <--- Switching to bypass the 429
            temperature=0.8,
            google_api_key=api_key
        )
        
        self.db_path = "./chroma_db"
        self.vectorstore = None

    def index_documents(self):
        """Builds the brain from the .txt files in /data"""
        print("🧠 Indexing casino data...")
        loader = DirectoryLoader("./data", glob="./*.txt", loader_cls=TextLoader)
        docs = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        final_docs = splitter.split_documents(docs)
        
        print(f"📄 Found {len(docs)} files. Split into {len(final_docs)} chunks.")

        self.vectorstore = Chroma.from_documents(
            documents=final_docs, 
            embedding=self.embeddings, 
            persist_directory=self.db_path
        )
        print("✅ Success! The Brain now knows the casino secrets.")

    def play_move(self, user_move):
        """The core game logic: Finds facts and tells a story."""
        if not self.vectorstore:
            # Load the existing database if it wasn't just created
            self.vectorstore = Chroma(
                persist_directory=self.db_path, 
                embedding_function=self.embeddings
            )
            
        # 1. Search the brain for relevant security facts
        relevant_docs = self.vectorstore.similarity_search(user_move, k=2)
        context = "\n---\n".join([d.page_content for d in relevant_docs])
        
        # 2. Ask Gemini to be the Game Master
        prompt = f"""
        You are the 'Sin City' style Game Master for a high-stakes Las Vegas heist. 
        Use the following SECURITY FACTS to judge the player's move.
        
        SECURITY FACTS:
        {context}
        
        PLAYER MOVE: {user_move}
        
        If the move works with the facts, describe a tense success. 
        If they ignore a danger mentioned in the facts, describe them getting caught.
        Keep it gritty, immersive, and brief.
        """
        
        response = self.llm.invoke(prompt)
        # Check if response is a list (typical in Gemini 3.0/2026 SDK)
        if isinstance(response.content, list):
            return response.content[0]['text']
        return response.content

# --- THE TEST BLOCK ---
if __name__ == "__main__":
    brain = HeistBrain()
    
    # Only uncomment the line below if you add NEW files to the /data folder
    # brain.index_documents() 
    
    player_move = "I'm going to wait for Camera 04 to flicker, then sneak into the service elevator using PIN 0729."
    
    print(f"\n🎮 PLAYER MOVE: {player_move}")
    print("\n--- AI GAME MASTER JUDGMENT ---")
    
    try:
        story = brain.play_move(player_move)
        print(story)
    except Exception as e:
        print(f"❌ Story Error: {e}")