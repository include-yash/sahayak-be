# routes/todos.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database.db import users_collection
from routes.auth import get_current_user
from bson import ObjectId
import uuid

router = APIRouter()

class TodoCreate(BaseModel):
    text: str

class TodoUpdate(BaseModel):
    id: str
    text: Optional[str] = None
    completed: Optional[bool] = None

@router.get("/todos", response_model=List[dict])
async def get_todos(current_user: dict = Depends(get_current_user)):
    user = users_collection.find_one({"email": current_user["email"]})
    return user.get("todos", [])

@router.post("/todos")
async def create_todo(todo: TodoCreate, current_user: dict = Depends(get_current_user)):
    todo_item = {
        "id": str(uuid.uuid4()),
        "text": todo.text,
        "completed": False
    }
    users_collection.update_one(
        {"email": current_user["email"]},
        {"$push": {"todos": todo_item}}
    )
    return todo_item

@router.put("/todos/{todo_id}")
async def update_todo(todo_id: str, todo: TodoUpdate, current_user: dict = Depends(get_current_user)):
    result = users_collection.update_one(
        {"email": current_user["email"], "todos.id": todo_id},
        {"$set": {
            "todos.$.text": todo.text if todo.text is not None else None,
            "todos.$.completed": todo.completed if todo.completed is not None else None
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo updated"}

@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str, current_user: dict = Depends(get_current_user)):
    result = users_collection.update_one(
        {"email": current_user["email"]},
        {"$pull": {"todos": {"id": todo_id}}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted"}