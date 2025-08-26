"""Agent orchestrator using LangGraph for complex AI workflows."""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator, TypedDict
from enum import Enum

import structlog
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel

from app.core.config import get_settings
from app.services.tool_registry import ToolRegistry
from app.services.conversation_manager import ConversationManager
from app.services.guardrails import GuardrailsService
from app.models.conversation import ConversationState, AgentState, MessageType

logger = structlog.get_logger(__name__)


class AgentType(str, Enum):
    """Available agent types."""
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    RISK_ASSESSOR = "risk_assessor"
    COMPLIANCE_OFFICER = "compliance_officer"
    GENERAL_ASSISTANT = "general_assistant"


class WorkflowState(TypedDict):
    """State structure for LangGraph workflows."""
    conversation_id: str
    user_id: str
    tenant_id: str
    cell_id: str
    messages: List[BaseMessage]
    agent_type: AgentType
    current_step: str
    tools_used: List[str]
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    guardrails_passed: bool
    error_message: Optional[str]


class AgentOrchestrator:
    """Main orchestrator for AI agents using LangGraph."""
    
    def __init__(self):
        self.settings = get_settings()
        self.tool_registry = None
        self.conversation_manager = None
        self.guardrails = None
        self.llm_openai = None
        self.llm_anthropic = None
        self.workflows: Dict[AgentType, StateGraph] = {}
        self.checkpointer = None
    
    async def initialize(self) -> None:
        """Initialize the agent orchestrator."""
        logger.info("Initializing agent orchestrator")
        
        # Initialize dependencies
        self.tool_registry = ToolRegistry()
        self.conversation_manager = ConversationManager()
        self.guardrails = GuardrailsService()
        
        # Initialize LLMs
        if self.settings.OPENAI_API_KEY:
            self.llm_openai = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.1,
                max_tokens=4096,
                api_key=self.settings.OPENAI_API_KEY
            )
        
        if self.settings.ANTHROPIC_API_KEY:
            self.llm_anthropic = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                temperature=0.1,
                max_tokens=4096,
                api_key=self.settings.ANTHROPIC_API_KEY
            )
        
        # Initialize checkpointer for conversation memory
        self.checkpointer = SqliteSaver.from_conn_string(":memory:")
        
        # Create workflows for each agent type
        await self._create_workflows()
        
        logger.info("Agent orchestrator initialized successfully")
    
    async def _create_workflows(self) -> None:
        """Create LangGraph workflows for each agent type."""
        
        # Investigator agent workflow
        investigator_workflow = StateGraph(WorkflowState)
        investigator_workflow.add_node("guardrails_check", self._guardrails_check)
        investigator_workflow.add_node("analyze_request", self._analyze_investigation_request)
        investigator_workflow.add_node("gather_evidence", self._gather_evidence)
        investigator_workflow.add_node("analyze_patterns", self._analyze_patterns)
        investigator_workflow.add_node("generate_response", self._generate_investigator_response)
        investigator_workflow.add_node("log_interaction", self._log_interaction)
        
        investigator_workflow.set_entry_point("guardrails_check")
        investigator_workflow.add_edge("guardrails_check", "analyze_request")
        investigator_workflow.add_edge("analyze_request", "gather_evidence")
        investigator_workflow.add_edge("gather_evidence", "analyze_patterns")
        investigator_workflow.add_edge("analyze_patterns", "generate_response")
        investigator_workflow.add_edge("generate_response", "log_interaction")
        investigator_workflow.add_edge("log_interaction", END)
        
        self.workflows[AgentType.INVESTIGATOR] = investigator_workflow.compile(
            checkpointer=self.checkpointer
        )
        
        # Analyst agent workflow
        analyst_workflow = StateGraph(WorkflowState)
        analyst_workflow.add_node("guardrails_check", self._guardrails_check)
        analyst_workflow.add_node("analyze_request", self._analyze_data_request)
        analyst_workflow.add_node("query_data", self._query_data_sources)
        analyst_workflow.add_node("perform_analysis", self._perform_analysis)
        analyst_workflow.add_node("create_visualizations", self._create_visualizations)
        analyst_workflow.add_node("generate_response", self._generate_analyst_response)
        analyst_workflow.add_node("log_interaction", self._log_interaction)
        
        analyst_workflow.set_entry_point("guardrails_check")
        analyst_workflow.add_edge("guardrails_check", "analyze_request")
        analyst_workflow.add_edge("analyze_request", "query_data")
        analyst_workflow.add_edge("query_data", "perform_analysis")
        analyst_workflow.add_edge("perform_analysis", "create_visualizations")
        analyst_workflow.add_edge("create_visualizations", "generate_response")
        analyst_workflow.add_edge("generate_response", "log_interaction")
        analyst_workflow.add_edge("log_interaction", END)
        
        self.workflows[AgentType.ANALYST] = analyst_workflow.compile(
            checkpointer=self.checkpointer
        )
        
        # Risk Assessor agent workflow
        risk_workflow = StateGraph(WorkflowState)
        risk_workflow.add_node("guardrails_check", self._guardrails_check)
        risk_workflow.add_node("analyze_request", self._analyze_risk_request)
        risk_workflow.add_node("assess_risk_factors", self._assess_risk_factors)
        risk_workflow.add_node("calculate_risk_score", self._calculate_risk_score)
        risk_workflow.add_node("recommend_actions", self._recommend_risk_actions)
        risk_workflow.add_node("generate_response", self._generate_risk_response)
        risk_workflow.add_node("log_interaction", self._log_interaction)
        
        risk_workflow.set_entry_point("guardrails_check")
        risk_workflow.add_edge("guardrails_check", "analyze_request")
        risk_workflow.add_edge("analyze_request", "assess_risk_factors")
        risk_workflow.add_edge("assess_risk_factors", "calculate_risk_score")
        risk_workflow.add_edge("calculate_risk_score", "recommend_actions")
        risk_workflow.add_edge("recommend_actions", "generate_response")
        risk_workflow.add_edge("generate_response", "log_interaction")
        risk_workflow.add_edge("log_interaction", END)
        
        self.workflows[AgentType.RISK_ASSESSOR] = risk_workflow.compile(
            checkpointer=self.checkpointer
        )
        
        # General assistant workflow (simpler, more flexible)
        general_workflow = StateGraph(WorkflowState)
        general_workflow.add_node("guardrails_check", self._guardrails_check)
        general_workflow.add_node("analyze_request", self._analyze_general_request)
        general_workflow.add_node("use_tools", self._use_appropriate_tools)
        general_workflow.add_node("generate_response", self._generate_general_response)
        general_workflow.add_node("log_interaction", self._log_interaction)
        
        general_workflow.set_entry_point("guardrails_check")
        general_workflow.add_edge("guardrails_check", "analyze_request")
        general_workflow.add_edge("analyze_request", "use_tools")
        general_workflow.add_edge("use_tools", "generate_response")
        general_workflow.add_edge("generate_response", "log_interaction")
        general_workflow.add_edge("log_interaction", END)
        
        self.workflows[AgentType.GENERAL_ASSISTANT] = general_workflow.compile(
            checkpointer=self.checkpointer
        )
    
    async def process_message(
        self,
        message: str,
        conversation_id: str,
        user_id: str,
        tenant_id: str,
        cell_id: str,
        agent_type: AgentType = AgentType.GENERAL_ASSISTANT,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a message using the appropriate agent workflow."""
        
        logger.info("Processing message", 
                   conversation_id=conversation_id,
                   agent_type=agent_type.value,
                   user_id=user_id)
        
        try:
            # Get conversation history
            conversation = await self.conversation_manager.get_conversation(
                conversation_id, user_id, tenant_id, cell_id
            )
            
            # Prepare initial state
            initial_state: WorkflowState = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "cell_id": cell_id,
                "messages": conversation.messages + [HumanMessage(content=message)],
                "agent_type": agent_type,
                "current_step": "start",
                "tools_used": [],
                "context": context or {},
                "metadata": {
                    "start_time": datetime.utcnow().isoformat(),
                    "message_id": str(uuid.uuid4())
                },
                "guardrails_passed": False,
                "error_message": None
            }
            
            # Get the appropriate workflow
            workflow = self.workflows.get(agent_type)
            if not workflow:
                raise ValueError(f"No workflow found for agent type: {agent_type}")
            
            # Execute the workflow with streaming
            config = {"configurable": {"thread_id": conversation_id}}
            
            async for event in workflow.astream(initial_state, config=config):
                if event and len(event) > 0:
                    # Extract the current state
                    state_key = list(event.keys())[0]
                    current_state = event[state_key]
                    
                    # Yield progress updates
                    yield {
                        "type": "progress",
                        "step": current_state.get("current_step", "unknown"),
                        "message": f"Executing step: {current_state.get('current_step', 'unknown')}",
                        "metadata": current_state.get("metadata", {})
                    }
                    
                    # If this is the final response, yield it
                    if state_key == "generate_response" or state_key == "log_interaction":
                        if "response" in current_state.get("metadata", {}):
                            yield {
                                "type": "message",
                                "content": current_state["metadata"]["response"],
                                "conversation_id": conversation_id,
                                "agent_type": agent_type.value,
                                "tools_used": current_state.get("tools_used", []),
                                "metadata": current_state.get("metadata", {})
                            }
            
        except Exception as e:
            logger.error("Error processing message", error=str(e), conversation_id=conversation_id)
            yield {
                "type": "error",
                "message": f"Error processing message: {str(e)}",
                "conversation_id": conversation_id
            }
    
    # Workflow node implementations
    async def _guardrails_check(self, state: WorkflowState) -> WorkflowState:
        """Check message against guardrails."""
        state["current_step"] = "guardrails_check"
        
        try:
            last_message = state["messages"][-1].content if state["messages"] else ""
            
            # Run guardrails check
            is_safe = await self.guardrails.check_message_safety(
                message=last_message,
                user_id=state["user_id"],
                tenant_id=state["tenant_id"]
            )
            
            state["guardrails_passed"] = is_safe
            if not is_safe:
                state["error_message"] = "Message failed safety checks"
            
        except Exception as e:
            logger.error("Guardrails check failed", error=str(e))
            state["guardrails_passed"] = False
            state["error_message"] = f"Guardrails check error: {str(e)}"
        
        return state
    
    async def _analyze_investigation_request(self, state: WorkflowState) -> WorkflowState:
        """Analyze investigation request to determine next steps."""
        state["current_step"] = "analyze_request"
        
        if not state["guardrails_passed"]:
            return state
        
        try:
            # Use LLM to analyze the investigation request
            system_prompt = """
            You are an expert fraud investigator. Analyze the user's request and determine:
            1. What type of investigation is needed
            2. What evidence should be gathered
            3. What analysis should be performed
            4. Any immediate concerns or red flags
            
            Return your analysis as structured data.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=state["messages"][-1].content)
            ]
            
            # Use appropriate LLM
            llm = self.llm_openai or self.llm_anthropic
            if llm:
                response = await llm.ainvoke(messages)
                state["context"]["investigation_analysis"] = response.content
            
        except Exception as e:
            logger.error("Investigation analysis failed", error=str(e))
            state["error_message"] = f"Analysis error: {str(e)}"
        
        return state
    
    async def _gather_evidence(self, state: WorkflowState) -> WorkflowState:
        """Gather evidence using available tools."""
        state["current_step"] = "gather_evidence"
        
        try:
            # Use tools to gather relevant evidence
            case_tool = await self.tool_registry.get_tool("case_search")
            if case_tool:
                # Search for related cases
                search_result = await case_tool.execute({
                    "query": state["messages"][-1].content,
                    "tenant_id": state["tenant_id"],
                    "cell_id": state["cell_id"]
                })
                state["context"]["related_cases"] = search_result
                state["tools_used"].append("case_search")
            
            # Search for related documents
            doc_tool = await self.tool_registry.get_tool("document_search")
            if doc_tool:
                doc_result = await doc_tool.execute({
                    "query": state["messages"][-1].content,
                    "tenant_id": state["tenant_id"],
                    "cell_id": state["cell_id"]
                })
                state["context"]["related_documents"] = doc_result
                state["tools_used"].append("document_search")
        
        except Exception as e:
            logger.error("Evidence gathering failed", error=str(e))
            state["error_message"] = f"Evidence gathering error: {str(e)}"
        
        return state
    
    async def _analyze_patterns(self, state: WorkflowState) -> WorkflowState:
        """Analyze patterns in the gathered evidence."""
        state["current_step"] = "analyze_patterns"
        
        try:
            # Use ML scoring tool for pattern analysis
            ml_tool = await self.tool_registry.get_tool("ml_scoring")
            if ml_tool and "related_cases" in state["context"]:
                scoring_result = await ml_tool.execute({
                    "data": state["context"]["related_cases"],
                    "model": "fraud_detection",
                    "explain": True
                })
                state["context"]["pattern_analysis"] = scoring_result
                state["tools_used"].append("ml_scoring")
        
        except Exception as e:
            logger.error("Pattern analysis failed", error=str(e))
            state["error_message"] = f"Pattern analysis error: {str(e)}"
        
        return state
    
    async def _generate_investigator_response(self, state: WorkflowState) -> WorkflowState:
        """Generate final investigator response."""
        state["current_step"] = "generate_response"
        
        try:
            # Compile all gathered information
            system_prompt = f"""
            You are an expert fraud investigator assistant. Based on the investigation analysis, 
            evidence gathered, and pattern analysis, provide a comprehensive response to the user.
            
            Investigation Analysis: {state["context"].get("investigation_analysis", "N/A")}
            Related Cases: {len(state["context"].get("related_cases", []))} found
            Related Documents: {len(state["context"].get("related_documents", []))} found
            Pattern Analysis: {state["context"].get("pattern_analysis", "N/A")}
            Tools Used: {", ".join(state["tools_used"])}
            
            Provide actionable insights and recommendations.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                *state["messages"]
            ]
            
            llm = self.llm_openai or self.llm_anthropic
            if llm:
                response = await llm.ainvoke(messages)
                state["metadata"]["response"] = response.content
        
        except Exception as e:
            logger.error("Response generation failed", error=str(e))
            state["metadata"]["response"] = f"I apologize, but I encountered an error while processing your investigation request: {str(e)}"
        
        return state
    
    # Placeholder implementations for other workflow nodes
    async def _analyze_data_request(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "analyze_request"
        return state
    
    async def _query_data_sources(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "query_data"
        return state
    
    async def _perform_analysis(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "perform_analysis"
        return state
    
    async def _create_visualizations(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "create_visualizations"
        return state
    
    async def _generate_analyst_response(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "generate_response"
        state["metadata"]["response"] = "Analyst response would be generated here based on data analysis."
        return state
    
    async def _analyze_risk_request(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "analyze_request"
        return state
    
    async def _assess_risk_factors(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "assess_risk_factors"
        return state
    
    async def _calculate_risk_score(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "calculate_risk_score"
        return state
    
    async def _recommend_risk_actions(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "recommend_actions"
        return state
    
    async def _generate_risk_response(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "generate_response"
        state["metadata"]["response"] = "Risk assessment response would be generated here."
        return state
    
    async def _analyze_general_request(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "analyze_request"
        return state
    
    async def _use_appropriate_tools(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "use_tools"
        return state
    
    async def _generate_general_response(self, state: WorkflowState) -> WorkflowState:
        state["current_step"] = "generate_response"
        
        try:
            system_prompt = """
            You are a helpful financial crime investigation assistant. 
            Provide accurate, helpful responses while maintaining professional standards.
            If you don't know something, say so clearly.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                *state["messages"]
            ]
            
            llm = self.llm_openai or self.llm_anthropic
            if llm:
                response = await llm.ainvoke(messages)
                state["metadata"]["response"] = response.content
            else:
                state["metadata"]["response"] = "I'm sorry, but no language model is currently available."
        
        except Exception as e:
            logger.error("General response generation failed", error=str(e))
            state["metadata"]["response"] = f"I apologize, but I encountered an error: {str(e)}"
        
        return state
    
    async def _log_interaction(self, state: WorkflowState) -> WorkflowState:
        """Log the interaction for audit purposes."""
        state["current_step"] = "log_interaction"
        
        try:
            # Save conversation state
            await self.conversation_manager.add_message(
                conversation_id=state["conversation_id"],
                message=state["metadata"].get("response", ""),
                message_type=MessageType.AI,
                user_id=state["user_id"],
                tenant_id=state["tenant_id"],
                cell_id=state["cell_id"],
                metadata={
                    "agent_type": state["agent_type"].value,
                    "tools_used": state["tools_used"],
                    "processing_time": datetime.utcnow().isoformat()
                }
            )
            
            state["metadata"]["interaction_logged"] = True
        
        except Exception as e:
            logger.error("Interaction logging failed", error=str(e))
            state["metadata"]["interaction_logged"] = False
        
        return state
