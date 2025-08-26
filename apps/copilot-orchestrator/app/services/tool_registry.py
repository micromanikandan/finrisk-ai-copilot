"""Tool registry implementing MCP (Model Context Protocol) for AI agent tools."""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from enum import Enum
import httpx
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)


class ToolType(str, Enum):
    """Available tool types."""
    CASE_MANAGEMENT = "case_management"
    DOCUMENT_SEARCH = "document_search"
    DATA_QUERY = "data_query"
    ML_SCORING = "ml_scoring"
    ENTITY_RESOLUTION = "entity_resolution"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE_CHECK = "compliance_check"
    AUDIT_LOG = "audit_log"


class MCPTool(ABC):
    """Base class for MCP (Model Context Protocol) tools."""
    
    def __init__(self, name: str, description: str, tool_type: ToolType):
        self.name = name
        self.description = description
        self.tool_type = tool_type
        self.settings = get_settings()
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters against the tool's schema."""
        # Basic validation - could be enhanced with jsonschema
        schema = self.get_schema()
        required_params = schema.get("required", [])
        
        for param in required_params:
            if param not in parameters:
                return False
        
        return True


class CaseSearchTool(MCPTool):
    """Tool for searching and retrieving case information."""
    
    def __init__(self):
        super().__init__(
            name="case_search",
            description="Search for fraud and compliance investigation cases",
            tool_type=ToolType.CASE_MANAGEMENT
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search for cases using the case service API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.settings.CASE_SERVICE_URL}/api/v1/cases",
                    params={
                        "search": parameters.get("query", ""),
                        "status": parameters.get("status"),
                        "caseType": parameters.get("case_type"),
                        "priority": parameters.get("priority"),
                        "size": parameters.get("limit", 10)
                    },
                    headers={"Authorization": f"Bearer {parameters.get('auth_token', '')}"}
                )
                
                if response.status_code == 200:
                    cases = response.json()
                    return {
                        "success": True,
                        "cases": cases,
                        "count": len(cases)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
        
        except Exception as e:
            logger.error("Case search failed", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "status": {"type": "string", "enum": ["OPEN", "IN_PROGRESS", "CLOSED"]},
                "case_type": {"type": "string"},
                "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "tenant_id": {"type": "string"},
                "cell_id": {"type": "string"},
                "auth_token": {"type": "string"}
            },
            "required": ["query", "tenant_id", "cell_id"]
        }


class DocumentSearchTool(MCPTool):
    """Tool for searching documents and evidence."""
    
    def __init__(self):
        super().__init__(
            name="document_search",
            description="Search for documents, evidence, and related content",
            tool_type=ToolType.DOCUMENT_SEARCH
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search for documents using the search service API."""
        try:
            async with httpx.AsyncClient() as client:
                search_request = {
                    "query": parameters.get("query", ""),
                    "indices": parameters.get("indices", ["documents"]),
                    "search_type": parameters.get("search_type", "hybrid"),
                    "size": parameters.get("limit", 10),
                    "filters": parameters.get("filters", {})
                }
                
                response = await client.post(
                    f"{self.settings.SEARCH_SERVICE_URL}/api/v1/search/",
                    json=search_request,
                    headers={"Authorization": f"Bearer {parameters.get('auth_token', '')}"}
                )
                
                if response.status_code == 200:
                    search_result = response.json()
                    return {
                        "success": True,
                        "documents": search_result.get("hits", []),
                        "total_hits": search_result.get("total_hits", 0),
                        "took_ms": search_result.get("took_ms", 0)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Search API error: {response.status_code}"
                    }
        
        except Exception as e:
            logger.error("Document search failed", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "indices": {"type": "array", "items": {"type": "string"}},
                "search_type": {"type": "string", "enum": ["hybrid", "keyword", "semantic"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "filters": {"type": "object"},
                "tenant_id": {"type": "string"},
                "cell_id": {"type": "string"},
                "auth_token": {"type": "string"}
            },
            "required": ["query", "tenant_id", "cell_id"]
        }


class MLScoringTool(MCPTool):
    """Tool for ML model scoring and risk assessment."""
    
    def __init__(self):
        super().__init__(
            name="ml_scoring",
            description="Score data using ML models for fraud and risk detection",
            tool_type=ToolType.ML_SCORING
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Score data using ML models."""
        try:
            async with httpx.AsyncClient() as client:
                scoring_request = {
                    "model_name": parameters.get("model", "fraud_detection_v1"),
                    "features": parameters.get("data", {}),
                    "explain": parameters.get("explain", True)
                }
                
                response = await client.post(
                    f"{self.settings.ML_SCORING_SERVICE_URL}/api/v1/scoring/predict",
                    json=scoring_request,
                    headers={"Authorization": f"Bearer {parameters.get('auth_token', '')}"}
                )
                
                if response.status_code == 200:
                    scoring_result = response.json()
                    return {
                        "success": True,
                        "prediction": scoring_result.get("prediction"),
                        "probability": scoring_result.get("probability"),
                        "risk_score": scoring_result.get("risk_score"),
                        "explanation": scoring_result.get("explanation"),
                        "shap_values": scoring_result.get("shap_values")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"ML scoring API error: {response.status_code}"
                    }
        
        except Exception as e:
            logger.error("ML scoring failed", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Model name to use for scoring"},
                "data": {"type": "object", "description": "Feature data for scoring"},
                "explain": {"type": "boolean", "description": "Include explainability results"},
                "tenant_id": {"type": "string"},
                "cell_id": {"type": "string"},
                "auth_token": {"type": "string"}
            },
            "required": ["model", "data", "tenant_id", "cell_id"]
        }


class EntityResolutionTool(MCPTool):
    """Tool for entity resolution and relationship mapping."""
    
    def __init__(self):
        super().__init__(
            name="entity_resolution",
            description="Resolve entities and find relationships using graph database",
            tool_type=ToolType.ENTITY_RESOLUTION
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve entities and find relationships."""
        try:
            async with httpx.AsyncClient() as client:
                entity_request = {
                    "entity_name": parameters.get("entity_name"),
                    "entity_type": parameters.get("entity_type"),
                    "relationship_depth": parameters.get("depth", 2),
                    "include_risk_scores": parameters.get("include_risk", True)
                }
                
                response = await client.post(
                    f"{self.settings.ENTITY_SERVICE_URL}/api/v1/entities/resolve",
                    json=entity_request,
                    headers={"Authorization": f"Bearer {parameters.get('auth_token', '')}"}
                )
                
                if response.status_code == 200:
                    entity_result = response.json()
                    return {
                        "success": True,
                        "entity": entity_result.get("entity"),
                        "relationships": entity_result.get("relationships", []),
                        "risk_indicators": entity_result.get("risk_indicators", [])
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Entity resolution API error: {response.status_code}"
                    }
        
        except Exception as e:
            logger.error("Entity resolution failed", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entity_name": {"type": "string", "description": "Name of entity to resolve"},
                "entity_type": {"type": "string", "enum": ["PERSON", "ORGANIZATION", "ACCOUNT"]},
                "depth": {"type": "integer", "minimum": 1, "maximum": 5},
                "include_risk": {"type": "boolean"},
                "tenant_id": {"type": "string"},
                "cell_id": {"type": "string"},
                "auth_token": {"type": "string"}
            },
            "required": ["entity_name", "entity_type", "tenant_id", "cell_id"]
        }


class AuditLogTool(MCPTool):
    """Tool for logging audit events."""
    
    def __init__(self):
        super().__init__(
            name="audit_log",
            description="Log audit events for compliance and investigation tracking",
            tool_type=ToolType.AUDIT_LOG
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Log an audit event."""
        try:
            # This would typically write to an audit service
            audit_event = {
                "timestamp": parameters.get("timestamp"),
                "user_id": parameters.get("user_id"),
                "action": parameters.get("action"),
                "resource": parameters.get("resource"),
                "details": parameters.get("details", {}),
                "tenant_id": parameters.get("tenant_id"),
                "cell_id": parameters.get("cell_id")
            }
            
            logger.info("Audit event logged", **audit_event)
            
            return {
                "success": True,
                "audit_id": f"audit_{asyncio.current_task().get_name()}",
                "logged_at": audit_event["timestamp"]
            }
        
        except Exception as e:
            logger.error("Audit logging failed", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "timestamp": {"type": "string", "format": "date-time"},
                "user_id": {"type": "string"},
                "action": {"type": "string"},
                "resource": {"type": "string"},
                "details": {"type": "object"},
                "tenant_id": {"type": "string"},
                "cell_id": {"type": "string"}
            },
            "required": ["user_id", "action", "tenant_id", "cell_id"]
        }


class ToolRegistry:
    """Registry for managing MCP tools available to AI agents."""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.tool_types: Dict[ToolType, List[str]] = {}
    
    async def initialize(self) -> None:
        """Initialize the tool registry with available tools."""
        logger.info("Initializing tool registry")
        
        # Register all available tools
        tools = [
            CaseSearchTool(),
            DocumentSearchTool(),
            MLScoringTool(),
            EntityResolutionTool(),
            AuditLogTool(),
        ]
        
        for tool in tools:
            await self.register_tool(tool)
        
        logger.info("Tool registry initialized", tool_count=len(self.tools))
    
    async def register_tool(self, tool: MCPTool) -> None:
        """Register a new tool."""
        self.tools[tool.name] = tool
        
        if tool.tool_type not in self.tool_types:
            self.tool_types[tool.tool_type] = []
        
        self.tool_types[tool.tool_type].append(tool.name)
        
        logger.info("Tool registered", name=tool.name, type=tool.tool_type.value)
    
    async def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    async def get_tools_by_type(self, tool_type: ToolType) -> List[MCPTool]:
        """Get all tools of a specific type."""
        tool_names = self.tool_types.get(tool_type, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools with their schemas."""
        tools_info = []
        
        for tool in self.tools.values():
            tools_info.append({
                "name": tool.name,
                "description": tool.description,
                "type": tool.tool_type.value,
                "schema": tool.get_schema()
            })
        
        return tools_info
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        validate: bool = True
    ) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        tool = await self.get_tool(tool_name)
        
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }
        
        if validate and not tool.validate_parameters(parameters):
            return {
                "success": False,
                "error": f"Invalid parameters for tool '{tool_name}'"
            }
        
        try:
            result = await tool.execute(parameters)
            
            # Log tool execution for audit
            audit_tool = await self.get_tool("audit_log")
            if audit_tool:
                await audit_tool.execute({
                    "user_id": parameters.get("user_id", "system"),
                    "action": f"tool_execution:{tool_name}",
                    "resource": "ai_agent_tool",
                    "details": {
                        "tool_name": tool_name,
                        "success": result.get("success", False)
                    },
                    "tenant_id": parameters.get("tenant_id", "unknown"),
                    "cell_id": parameters.get("cell_id", "unknown"),
                    "timestamp": parameters.get("timestamp")
                })
            
            return result
        
        except Exception as e:
            logger.error("Tool execution failed", tool=tool_name, error=str(e))
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def get_tool_schema_for_llm(self) -> List[Dict[str, Any]]:
        """Get tool schemas formatted for LLM function calling."""
        llm_tools = []
        
        for tool in self.tools.values():
            llm_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.get_schema()
                }
            })
        
        return llm_tools
