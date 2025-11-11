"""Deep Research API - FastAPI Application"""
import asyncio
import uuid
import sys
import os
from pathlib import Path
from typing import AsyncGenerator

# Add parent directory to path to import research-core
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from api.config import settings
from api.models import (
    ResearchRequest,
    ResearchResponse,
    ResearchProgress,
    ResearchError,
    HealthResponse,
    ResearchPlan,
    ResearchStep,
    StepStatus,
)

# Import research workflow
from research_core.workflow import run_agent_workflow_async
from research_core.graph.builder import build_graph

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Deep Research API",
    description="Multi-agent deep research framework API",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        models_available=[
            settings.coordinator_model,
            settings.planner_model,
            settings.researcher_model,
            settings.coder_model,
            settings.reporter_model,
        ],
    )


@app.post("/research", response_model=ResearchResponse)
async def research_sync(request: ResearchRequest):
    """
    Synchronous research endpoint - returns final result

    Args:
        request: Research request with query and configuration

    Returns:
        Complete research response with plan, observations, and final report
    """
    research_id = str(uuid.uuid4())
    logger.info(f"Starting research {research_id}: {request.query}")

    try:
        # Set configuration from request or use defaults
        max_step_num = request.max_step_num or settings.default_max_step_num
        max_plan_iterations = request.max_plan_iterations or settings.default_max_plan_iterations
        enable_clarification = (
            request.enable_clarification
            if request.enable_clarification is not None
            else settings.enable_clarification
        )
        enable_background_investigation = (
            request.enable_background_investigation
            if request.enable_background_investigation is not None
            else settings.enable_background_investigation
        )

        # Build initial state with all configuration
        initial_state = {
            "messages": [{"role": "user", "content": request.query}],
            "locale": request.locale or "en-US",
            "research_topic": request.query,
            "clarified_research_topic": request.query,
            "auto_accepted_plan": request.auto_accept_plan,
            "enable_background_investigation": enable_background_investigation,
        }

        if enable_clarification is not None:
            initial_state["enable_clarification"] = enable_clarification

        # Run research workflow
        result = await run_agent_workflow_async(
            user_input=request.query,
            debug=False,
            max_plan_iterations=max_plan_iterations,
            max_step_num=max_step_num,
            enable_background_investigation=enable_background_investigation,
            enable_clarification=enable_clarification,
            initial_state=initial_state,
        )

        # Extract plan information
        plan_data = result.get("current_plan", {})
        if isinstance(plan_data, str):
            # Plan might be a string, create default structure
            plan = ResearchPlan(
                title=request.query,
                thought="Research completed",
                steps=[],
                has_enough_context=True,
                locale=request.locale or "en-US",
            )
        else:
            steps = []
            for step_data in plan_data.get("steps", []):
                steps.append(
                    ResearchStep(
                        title=step_data.get("title", ""),
                        description=step_data.get("description", ""),
                        step_type=step_data.get("step_type", "research"),
                        need_search=step_data.get("need_search", False),
                        status=StepStatus.COMPLETED,
                        execution_result=step_data.get("execution_res"),
                    )
                )

            plan = ResearchPlan(
                title=plan_data.get("title", request.query),
                thought=plan_data.get("thought", ""),
                steps=steps,
                has_enough_context=plan_data.get("has_enough_context", True),
                locale=plan_data.get("locale", request.locale or "en-US"),
            )

        # Build response
        response = ResearchResponse(
            research_id=research_id,
            query=request.query,
            plan=plan,
            final_report=result.get("final_report", ""),
            observations=result.get("observations", []),
            resources=result.get("resources", []),
            locale=result.get("locale", request.locale or "en-US"),
            metadata={
                "max_step_num": max_step_num,
                "max_plan_iterations": max_plan_iterations,
                "enable_clarification": enable_clarification,
                "enable_background_investigation": enable_background_investigation,
            },
        )

        logger.info(f"Research {research_id} completed successfully")
        return response

    except Exception as e:
        logger.error(f"Research {research_id} failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ResearchError(
                error="Research workflow failed",
                detail=str(e),
                research_id=research_id,
            ).dict(),
        )


@app.post("/research/stream")
async def research_stream(request: ResearchRequest):
    """
    Streaming research endpoint - streams progress updates

    Args:
        request: Research request with query and configuration

    Returns:
        Server-sent events stream with progress updates
    """
    research_id = str(uuid.uuid4())
    logger.info(f"Starting streaming research {research_id}: {request.query}")

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events from research workflow"""
        try:
            # Set configuration from request or use defaults
            max_step_num = request.max_step_num or settings.default_max_step_num
            max_plan_iterations = request.max_plan_iterations or settings.default_max_plan_iterations
            enable_clarification = (
                request.enable_clarification
                if request.enable_clarification is not None
                else settings.enable_clarification
            )
            enable_background_investigation = (
                request.enable_background_investigation
                if request.enable_background_investigation is not None
                else settings.enable_background_investigation
            )

            # Create graph for streaming
            graph = build_graph()

            # Build input state with all configuration
            input_state = {
                "messages": [{"role": "user", "content": request.query}],
                "locale": request.locale or "en-US",
                "research_topic": request.query,
                "clarified_research_topic": request.query,
                "auto_accepted_plan": request.auto_accept_plan,
                "enable_background_investigation": enable_background_investigation,
            }

            if enable_clarification is not None:
                input_state["enable_clarification"] = enable_clarification

            # Stream graph execution
            config = {
                "configurable": {
                    "thread_id": research_id,
                    "max_plan_iterations": max_plan_iterations,
                    "max_step_num": max_step_num,
                }
            }

            async for chunk in graph.astream(input_state, config=config):
                # Extract node and state information
                for node_name, state_data in chunk.items():
                    progress = ResearchProgress(
                        stage=node_name,
                        message=f"Processing: {node_name}",
                        observations=state_data.get("observations"),
                        current_step=len(state_data.get("observations", [])),
                    )

                    # Send as JSON event
                    yield f"data: {progress.model_dump_json()}\n\n"

                await asyncio.sleep(0.1)  # Prevent overwhelming client

            logger.info(f"Streaming research {research_id} completed")

        except Exception as e:
            logger.error(f"Streaming research {research_id} failed: {str(e)}", exc_info=True)
            error = ResearchError(
                error="Research workflow failed",
                detail=str(e),
                research_id=research_id,
            )
            yield f"data: {error.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def run():
    """Run the API server"""
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=False,
    )


if __name__ == "__main__":
    run()
