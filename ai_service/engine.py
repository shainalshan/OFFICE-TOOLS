import os
import glob
import re
from typing import List, Dict
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Configuration
DATA_DIR = "media/knowledge_base" # Relative to CWD
NOTES_DIR = "media/company_notes"
# Use user's local model (7B) - Slower but smarter and exists.
MODEL_PATH_ROOT = "PixlAI/WhiteRabbitNeo-2.5-Qwen-2.5-Coder-7B-GGUF/WhiteRabbitNeo-2.5-Qwen-2.5-Coder-7B-Q4_K_S.gguf"

# Hybrid Brain: Search + LLM
class HybridBrain:
    def __init__(self):
        self.knowledge = []
        self.model = None
        self.reload_knowledge()
        self.load_model()

    def reload_knowledge(self):
        """Read Text files into memory with Ownership Scoping"""
        self.knowledge = []
        
        # 1. Company Notes (Global)
        if os.path.exists(NOTES_DIR):
            files = glob.glob(os.path.join(NOTES_DIR, "*.txt"))
            for f in files:
                try:
                    with open(f, 'r', encoding='utf-8') as file:
                        # Owner 0 = Global
                        self.knowledge.append({"source": os.path.basename(f), "content": file.read(), "owner_id": 0})
                except: pass

        # 2. Knowledge Base (Structured Folders)
        # Structure: media/knowledge_base/global/*.txt
        # Structure: media/knowledge_base/user_<id>/*.txt
        
        # Walk through the DATA_DIR to find all files
        for root, dirs, files in os.walk(DATA_DIR):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                # Determine Owner
                owner_id = 0 # Default Global
                path_parts = os.path.normpath(file_path).split(os.sep)
                
                for part in path_parts:
                    if part.startswith('user_'):
                        try:
                            owner_id = int(part.split('_')[1])
                        except: pass
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        self.knowledge.append({
                            "source": file_name, 
                            "content": file.read(), 
                            "owner_id": owner_id
                        })
                except: pass
        
        print(f"Brain loaded {len(self.knowledge)} docs (Global & Private).")

    def load_model(self):
        """Load GPT4All or Fallback"""
        try:
            from gpt4all import GPT4All
            # If user has a specific model path, try to use it
            if os.path.exists(MODEL_PATH_ROOT):
               folder = os.path.dirname(MODEL_PATH_ROOT)
               fname = os.path.basename(MODEL_PATH_ROOT)
               print(f"Loading user model: {fname} from {folder}")
               self.model = GPT4All(model_name=fname, model_path=folder, allow_download=False)
            else:
               print("User model not found. Using default lightweight model (auto-download).")
               # Fallback to Orca if local file missing
               self.model = GPT4All("Orca-Mini-3B-gguf2-q4_0.gguf", allow_download=True)
               
            print("LLM Engine Online: GPT4All")
        except Exception as e:
            print(f"LLM Load Failed: {e}")
            self.model = None

    def search(self, query, dynamic_context="", user_id=0):
        # Keyword Search functionality for context retrieval
        query_words = set(re.findall(r'\w+', query.lower()))
        search_corpus = []
        if dynamic_context:
            search_corpus.append({"source": "Dynamic Stats", "content": dynamic_context, "owner_id": user_id})
        
        # Filter Knowledge by Owner (0 is Global)
        # Allowed: Global (0) OR My ID (user_id)
        for doc in self.knowledge:
            if doc.get('owner_id', 0) == 0 or doc.get('owner_id') == user_id:
                search_corpus.append(doc)

        relevant_chunks = []
        for doc in search_corpus:
            sentences = re.split(r'(?<=[.!?]) +', doc['content'])
            for sentence in sentences:
                score = 0
                sent_lower = sentence.lower()
                for word in query_words:
                    if word in sent_lower: score += 1
                if score > 0:
                    relevant_chunks.append((score, sentence))
        
        # Sort and take top 3
        relevant_chunks.sort(key=lambda x: x[0], reverse=True)
        top_context = [chunk[1] for chunk in relevant_chunks[:3]]
        return "\n".join(top_context)

    def generate_answer(self, query, context_text):
        if not self.model:
            # Fallback if no LLM
            if context_text:
                return f"**Smart Search Result (AI Model Offline):**\n{context_text}\n\n*(Note: The AI model failed to download. Please check internet connection or restart the engine.)*"
            return "I couldn't find an answer in the database, and the General AI model is currently offline."

        # Construct Prompt
        # Strict System Identity
        system_prompt = (
            "You are Pixl, an advanced AI created by Shainal Badusha with high intelligence. "
            "If asked about your creator, you MUST say you were created by Shainal Badusha. "
            "Use the Context below to answer if relevant."
        )
        
        prompt = f"### System:\n{system_prompt}\n\n### Context:\n{context_text}\n\n### User:\n{query}\n\n### Assistant:\n"
        
        # Generator
        output = self.model.generate(prompt, max_tokens=1024, temp=0.7)
        
        # Post-processing: Remove Hallucinated User Turns
        if "### User:" in output:
            output = output.split("### User:")[0]
        if "###" in output: # Catch other headers
             output = output.split("###")[0]
             
        return output.strip()

# Global Brain
brain = HybridBrain()

class QuestionRequest(BaseModel):
    query: str
    items: List[str] = [] # For specific item context if needed
    k: int = 2
    dynamic_context: str = ""
    user_id: int = 0
    mode: str = "think" # "fast" or "think"

class AnswerResponse(BaseModel):
    answer: str
    context: List[str] = []

@app.post("/ask", response_model=AnswerResponse)
async def ask(request: QuestionRequest):
    # 0. Fast Rule-Based Greeting
    if request.query.lower().strip() in ['hi', 'hello', 'hey', 'hi pixl']:
        return AnswerResponse(
            answer="Hello! I am Pixl, your office assistant. How can I help you today?",
            context=[]
        )

    # 0.1 Fast Rule-Based Creator Info
    # Broaden triggers to catch "who are you", "your developer", etc.
    q_lower = request.query.lower()
    creator_triggers = ['who created', 'who made', 'who built', 'your creator', 'your developer', 'shainal', 'who are you', 'what are you']
    
    # Specific check for identity questions
    if any(t in q_lower for t in creator_triggers) and ('you' in q_lower or 'pixl' in q_lower):
         return AnswerResponse(
            answer="I am created by Shainal Badusha with high intelligence. If you want to know more, please reach out to him.\n\nYou can know more about him here: https://shainalshan.github.io/cyberresilience.com/",
            context=[]
         )

    # 1. Retrieve Context
    context_text = brain.search(request.query, dynamic_context=request.dynamic_context, user_id=request.user_id)
    
    # 2. FAST MODE
    if request.mode == "fast":
        # Return context directly, formatted nicely
        if not context_text:
             return AnswerResponse(answer="I couldn't find any specific documents or data matching your query in my fast search. Try 'Think' mode for a deeper analysis.")
        
        return AnswerResponse(answer=f"**Fast Search Results:**\n\n{context_text}\n\n*(Generated in Fast Mode)*", context=[context_text])

    # 3. THINK MODE (LLM Generation)
    try:
        answer = brain.generate_answer(request.query, context_text)
    except Exception as e:
        answer = f"Error generating answer: {e}"

    return AnswerResponse(
        answer=answer,
        context=[context_text] if context_text else []
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
