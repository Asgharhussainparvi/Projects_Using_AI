from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date
import csv
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class MoodEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mood_emoji: str
    mood_name: str
    notes: Optional[str] = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MoodEntryCreate(BaseModel):
    mood_emoji: str
    mood_name: str
    notes: Optional[str] = ""

# Mood mappings
MOOD_OPTIONS = {
    "😄": "Very Happy",
    "😊": "Happy", 
    "🙂": "Content",
    "😐": "Neutral",
    "😞": "Sad",
    "😢": "Very Sad",
    "😡": "Angry",
    "😰": "Anxious",
    "🤗": "Excited",
    "😴": "Tired"
}

# Routes
@api_router.get("/")
async def root():
    return {"message": "Mood Tracker API"}

@api_router.post("/moods", response_model=MoodEntry)
async def create_mood_entry(input: MoodEntryCreate):
    if input.mood_emoji not in MOOD_OPTIONS:
        raise HTTPException(status_code=400, detail="Invalid mood emoji")
    
    mood_dict = input.dict()
    mood_obj = MoodEntry(**mood_dict)
    await db.mood_entries.insert_one(mood_obj.dict())
    return mood_obj

@api_router.get("/moods", response_model=List[MoodEntry])
async def get_mood_entries():
    mood_entries = await db.mood_entries.find().sort("timestamp", -1).to_list(1000)
    return [MoodEntry(**entry) for entry in mood_entries]

@api_router.get("/moods/options")
async def get_mood_options():
    return MOOD_OPTIONS

@api_router.get("/moods/export")
async def export_moods_csv():
    mood_entries = await db.mood_entries.find().sort("timestamp", -1).to_list(10000)
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Time', 'Mood', 'Emoji', 'Notes'])
    
    # Write data
    for entry in mood_entries:
        timestamp = entry['timestamp']
        writer.writerow([
            timestamp.strftime('%Y-%m-%d'),
            timestamp.strftime('%H:%M:%S'),
            entry['mood_name'],
            entry['mood_emoji'],
            entry.get('notes', '')
        ])
    
    output.seek(0)
    
    # Create streaming response
    def generate():
        yield output.getvalue()
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mood_history.csv"}
    )

@api_router.delete("/moods/{mood_id}")
async def delete_mood_entry(mood_id: str):
    result = await db.mood_entries.delete_one({"id": mood_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Mood entry not found")
    return {"message": "Mood entry deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()