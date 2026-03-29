"""
Pydantic models for API request/response validation.
"""
from pydantic import BaseModel
from typing import Optional, List, Any
import json


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    user_id: Optional[str] = None
    profile_complete: bool = False


class UserProfile(BaseModel):
    persona: str
    risk_level: str          # conservative | moderate | aggressive
    goals: List[str]
    interests: List[str]
    recommended_products: List[str]


class ProfileInitRequest(BaseModel):
    user_id: str
    name: str
    profile: UserProfile


class EventRequest(BaseModel):
    user_id: str
    event_type: str          # click | search | view | like
    metadata: dict = {}


class RecommendationItem(BaseModel):
    product: str
    reason: str
    score: float


class UserResponse(BaseModel):
    id: str
    name: str
    persona: str
    risk_level: str
    goals: List[str]
    interests: List[str]
    recommended_products: List[str]
    created_at: str
