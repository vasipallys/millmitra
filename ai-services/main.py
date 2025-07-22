from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.ai_orchestrator import RiceMillAIOrchestrator
from voice.voice_processor import VoiceProcessor
from analytics.predictive_analytics import PredictiveAnalytics

app = FastAPI(title="Rice Mill AI Services", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI components
ai_orchestrator = RiceMillAIOrchestrator()
voice_processor = VoiceProcessor()
analytics = PredictiveAnalytics()

@app.post("/process-query")
async def process_query(query: str, context: dict = None):
    response = await ai_orchestrator.process_query(query, context or {})
    return {"response": response}

@app.post("/process-voice")
async def process_voice(audio_data: bytes):
    result = await voice_processor.process_audio(audio_data)
    return result

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Rice Mill AI Services...")
    uvicorn.run(app, host="127.0.0.1", port=8000)