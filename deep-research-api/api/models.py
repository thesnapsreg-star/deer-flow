"""API Request and Response Models"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ResearchRequest(BaseModel):
    """Request model for research tasks"""
    query: str = Field(..., description="The research query or question")
    max_step_num: Optional[int] = Field(default=None, description="Maximum number of research steps")
    max_plan_iterations: Optional[int] = Field(default=None, description="Maximum plan iterations")
    enable_clarification: Optional[bool] = Field(default=None, description="Enable multi-turn clarification")
    enable_background_investigation: Optional[bool] = Field(default=None, description="Enable background investigation")
    auto_accept_plan: Optional[bool] = Field(default=True, description="Auto-accept the research plan")
    report_style: Optional[str] = Field(default="academic", description="Report style (academic, news, social, investment)")
    locale: Optional[str] = Field(default="en-US", description="Research locale")


class StepStatus(str, Enum):
    """Research step status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchStep(BaseModel):
    """Research plan step"""
    title: str
    description: str
    step_type: str
    need_search: bool
    status: StepStatus = StepStatus.PENDING
    execution_result: Optional[str] = None


class ResearchPlan(BaseModel):
    """Research plan"""
    title: str
    thought: str
    steps: List[ResearchStep]
    has_enough_context: bool
    locale: str


class ResearchProgress(BaseModel):
    """Research progress update"""
    stage: str = Field(..., description="Current stage (coordinator, planner, researcher, coder, reporter)")
    message: str = Field(..., description="Progress message")
    plan: Optional[ResearchPlan] = None
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    observations: Optional[List[str]] = None


class ResearchResponse(BaseModel):
    """Final research response"""
    research_id: str
    query: str
    plan: ResearchPlan
    final_report: str
    observations: List[str]
    resources: List[Dict[str, Any]]
    locale: str
    metadata: Dict[str, Any] = {}


class ResearchError(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    research_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    models_available: List[str]
