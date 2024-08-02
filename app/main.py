from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId

app = FastAPI()

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["messages_db"]
collection = db["messages"]

# Создание модели для сообщений
class Message(BaseModel):
    text: str
    author: str

#Получение всех сообщений
@app.get("/api/v1/messages/")
async def get_messages():
    messages = list(collection.find({}, {"_id": 0}))
    return messages


#Создание нового сообщения
@app.post("/api/v1/message/")
async def create_message(message: Message):
    collection.insert_one(message.dict())
    return {"message": "Message created successfully"}