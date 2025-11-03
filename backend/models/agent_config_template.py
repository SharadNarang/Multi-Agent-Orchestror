"""
Agent Configuration Templates
Predefined templates for common agent frameworks
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base
import yaml
import os
from pathlib import Path

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


def load_templates_from_yaml():
    """
    Load agent templates from YAML configuration file
    """
    # Get the path to the config file
    config_dir = Path(__file__).parent.parent / "config"
    yaml_file = config_dir / "agent_templates.yaml"
    
    if not yaml_file.exists():
        print(f"Warning: Template config file not found at {yaml_file}")
        return []
    
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('templates', [])
    except Exception as e:
        print(f"Error loading templates from YAML: {e}")
        return []

# Load templates from YAML configuration
BUILTIN_TEMPLATES = load_templates_from_yaml()

