"""
Agent Configuration Templates
Predefined templates for common agent frameworks
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class AgentConfigTemplate(Base):
    """
    Store predefined configuration templates for agent frameworks
    """
    __tablename__ = "agent_config_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # e.g., "crewai", "databricks"
    display_name = Column(String)  # e.g., "CrewAI"
    description = Column(String)
    framework = Column(String)  # e.g., "crewai", "databricks", "openai"
    icon_url = Column(String, nullable=True)
    
    # Request/Response mapping configuration
    request_mapping = Column(JSON)
    response_mapping = Column(JSON)
    
    # Authentication configuration
    auth_config = Column(JSON)
    
    # Example usage
    example_request = Column(JSON)
    example_response = Column(JSON)
    
    # Metadata
    is_builtin = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Predefined templates
BUILTIN_TEMPLATES = [
    {
        "name": "crewai",
        "display_name": "CrewAI",
        "description": "Multi-agent collaboration framework with role-based agents",
        "framework": "crewai",
        "request_mapping": {
            "method": "POST",
            "path": "/kickoff",
            "headers": {
                "Content-Type": "application/json"
            },
            "body_mapping": {
                "inputs": {
                    "topic": "$.description"
                }
            }
        },
        "response_mapping": {
            "status_path": "$.success",
            "result_path": "$.result",
            "error_path": "$.error"
        },
        "auth_config": {
            "type": "none"
        },
        "example_request": {
            "inputs": {
                "topic": "Research AI trends in 2024"
            }
        },
        "example_response": {
            "result": "Comprehensive research report...",
            "workflow": [],
            "success": True
        }
    },
    {
        "name": "databricks_foundation",
        "display_name": "Databricks Foundation Models",
        "description": "Databricks LLM serving endpoints (Llama, Mistral, etc.)",
        "framework": "databricks",
        "request_mapping": {
            "method": "POST",
            "path": "/serving-endpoints/{model_name}/invocations",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer ${DATABRICKS_TOKEN}"
            },
            "body_mapping": {
                "messages": [
                    {
                        "role": "user",
                        "content": "$.description"
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
        },
        "response_mapping": {
            "status_path": "$.choices[0].finish_reason",
            "result_path": "$.choices[0].message.content",
            "error_path": "$.error.message"
        },
        "auth_config": {
            "type": "bearer_token",
            "env_var": "DATABRICKS_TOKEN"
        },
        "example_request": {
            "messages": [
                {
                    "role": "user",
                    "content": "What is artificial intelligence?"
                }
            ],
            "max_tokens": 1000
        },
        "example_response": {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Artificial intelligence is..."
                    },
                    "finish_reason": "stop"
                }
            ]
        }
    },
    {
        "name": "openai_compatible",
        "display_name": "OpenAI Compatible",
        "description": "OpenAI API compatible endpoints (GPT-3.5, GPT-4, etc.)",
        "framework": "openai",
        "request_mapping": {
            "method": "POST",
            "path": "/v1/chat/completions",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer ${OPENAI_API_KEY}"
            },
            "body_mapping": {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": "$.description"
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
        },
        "response_mapping": {
            "status_path": "$.choices[0].finish_reason",
            "result_path": "$.choices[0].message.content",
            "error_path": "$.error.message"
        },
        "auth_config": {
            "type": "bearer_token",
            "env_var": "OPENAI_API_KEY"
        },
        "example_request": {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, how are you?"
                }
            ]
        },
        "example_response": {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "I'm doing well, thank you!"
                    },
                    "finish_reason": "stop"
                }
            ]
        }
    },
    {
        "name": "custom",
        "display_name": "Custom REST API",
        "description": "Define your own custom request/response mapping",
        "framework": "custom",
        "request_mapping": {
            "method": "POST",
            "path": "/process",
            "headers": {
                "Content-Type": "application/json"
            },
            "body_mapping": {
                "query": "$.description"
            }
        },
        "response_mapping": {
            "status_path": "$.status",
            "result_path": "$.result",
            "error_path": "$.error"
        },
        "auth_config": {
            "type": "none"
        },
        "example_request": {
            "query": "Sample query"
        },
        "example_response": {
            "status": "success",
            "result": "Response here"
        }
    }
]

