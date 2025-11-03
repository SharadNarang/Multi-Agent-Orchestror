"""
Agent Registration Service
Handles agent registration with configuration templates and testing
"""
from sqlalchemy.orm import Session
from models.agent import Agent, AgentType, AgentStatus
from models.agent_config_template import AgentConfigTemplate, BUILTIN_TEMPLATES
from typing import Dict, Any, List, Optional
import httpx
import json
from jsonpath_ng import parse as jsonpath_parse

class AgentRegistrationService:
    """
    Service for registering external agents with configuration templates
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def initialize_templates(self):
        """Initialize built-in templates if they don't exist"""
        for template_data in BUILTIN_TEMPLATES:
            existing = self.db.query(AgentConfigTemplate).filter(
                AgentConfigTemplate.name == template_data["name"]
            ).first()
            
            if not existing:
                template = AgentConfigTemplate(**template_data, is_builtin=True)
                self.db.add(template)
        
        self.db.commit()
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available configuration templates"""
        templates = self.db.query(AgentConfigTemplate).filter(
            AgentConfigTemplate.is_active == True
        ).all()
        
        return [
            {
                "id": t.id,
                "name": t.name,
                "display_name": t.display_name,
                "description": t.description,
                "framework": t.framework,
                "is_builtin": t.is_builtin,
                "example_request": t.example_request,
                "example_response": t.example_response
            }
            for t in templates
        ]
    
    def get_template(self, template_id: int) -> Optional[AgentConfigTemplate]:
        """Get a specific template"""
        return self.db.query(AgentConfigTemplate).filter(
            AgentConfigTemplate.id == template_id
        ).first()
    
    def get_template_by_name(self, name: str) -> Optional[AgentConfigTemplate]:
        """Get a template by name"""
        return self.db.query(AgentConfigTemplate).filter(
            AgentConfigTemplate.name == name
        ).first()
    
    async def test_agent_connection(
        self,
        endpoint: str,
        template_config: Dict[str, Any],
        test_query: str = "Hello, this is a test",
        auth_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Test connection to an external agent
        """
        try:
            # Extract request mapping
            request_mapping = template_config.get("request_mapping", {})
            response_mapping = template_config.get("response_mapping", {})
            
            # Build request
            method = request_mapping.get("method", "POST")
            path = request_mapping.get("path", "/process")
            headers = request_mapping.get("headers", {})
            
            # Add auth headers if provided
            if auth_headers:
                headers.update(auth_headers)
            
            # Build body with test query
            body = self._build_request_body(
                request_mapping.get("body_mapping", {}),
                {"description": test_query}
            )
            
            # Construct full URL
            full_url = endpoint.rstrip('/') + '/' + path.lstrip('/')
            
            # Make request
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "POST":
                    response = await client.post(full_url, json=body, headers=headers)
                elif method == "GET":
                    response = await client.get(full_url, headers=headers)
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported HTTP method: {method}"
                    }
                
                # Check response
                if response.status_code >= 200 and response.status_code < 300:
                    response_data = response.json()
                    
                    # Try to extract result using response mapping
                    try:
                        result = self._extract_response_data(
                            response_data,
                            response_mapping
                        )
                        
                        return {
                            "success": True,
                            "status_code": response.status_code,
                            "response": response_data,
                            "extracted_result": result,
                            "message": "Connection successful"
                        }
                    except Exception as e:
                        return {
                            "success": True,
                            "status_code": response.status_code,
                            "response": response_data,
                            "warning": f"Could not extract result: {str(e)}",
                            "message": "Connected but response format may need adjustment"
                        }
                else:
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
        
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Connection timeout after 30 seconds"
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": "Could not connect to endpoint. Check URL and network."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Test failed: {str(e)}"
            }
    
    def register_agent_with_template(
        self,
        name: str,
        description: str,
        endpoint: str,
        capabilities: List[str],
        template_id: int,
        custom_config: Optional[Dict[str, Any]] = None,
        auth_config: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Register a new agent using a configuration template
        """
        # Check if agent already exists
        existing = self.db.query(Agent).filter(Agent.name == name).first()
        if existing:
            raise ValueError(f"Agent with name '{name}' already exists")
        
        # Get template
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Build config combining template and custom config
        agent_config = {
            "template_id": template_id,
            "template_name": template.name,
            "request_mapping": custom_config.get("request_mapping") if custom_config else template.request_mapping,
            "response_mapping": custom_config.get("response_mapping") if custom_config else template.response_mapping,
            "auth_config": auth_config or template.auth_config
        }
        
        # Create agent
        agent = Agent(
            name=name,
            description=description,
            agent_type=AgentType.API,
            endpoint=endpoint,
            capabilities=capabilities,
            config=agent_config,
            status=AgentStatus.ACTIVE,
            meta_data={
                "template": template.name,
                "framework": template.framework
            }
        )
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        
        return agent
    
    def _build_request_body(
        self,
        body_mapping: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build request body using JSONPath mapping
        """
        result = {}
        
        for key, value in body_mapping.items():
            if isinstance(value, str) and value.startswith("$."):
                # Extract from input data using JSONPath
                jsonpath_expr = jsonpath_parse(value)
                matches = jsonpath_expr.find(input_data)
                if matches:
                    result[key] = matches[0].value
                else:
                    result[key] = None
            elif isinstance(value, dict):
                # Recursive mapping
                result[key] = self._build_request_body(value, input_data)
            elif isinstance(value, list):
                # Handle list mappings
                result[key] = [
                    self._build_request_body(item, input_data) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                # Static value
                result[key] = value
        
        return result
    
    def _extract_response_data(
        self,
        response_data: Dict[str, Any],
        response_mapping: Dict[str, Any]
    ) -> str:
        """
        Extract result from response using JSONPath
        """
        result_path = response_mapping.get("result_path", "$.result")
        
        # Parse JSONPath
        jsonpath_expr = jsonpath_parse(result_path)
        matches = jsonpath_expr.find(response_data)
        
        if matches:
            return matches[0].value
        else:
            # Fallback: return whole response as JSON string
            return json.dumps(response_data)

