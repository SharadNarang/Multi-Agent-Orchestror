# YAML Configuration Guide

## Overview

Agent configuration templates have been moved from hardcoded Python to a YAML configuration file for better maintainability and flexibility.

## Configuration File Location

```
backend/config/agent_templates.yaml
```

## Template Structure

Each template in the YAML file has the following structure:

```yaml
templates:
  - name: template_identifier          # Unique identifier
    display_name: Display Name         # Human-readable name
    description: Template description  # What this template is for
    framework: framework_name          # e.g., crewai, databricks, openai, custom
    
    request_mapping:                   # How to transform requests
      method: POST                     # HTTP method
      path: /endpoint/path            # API endpoint path
      headers:                         # HTTP headers
        Content-Type: application/json
        Authorization: Bearer ${TOKEN}
      body_mapping:                    # Request body transformation
        field_name: $.jsonpath         # JSONPath expressions
    
    response_mapping:                  # How to extract responses
      status_path: $.status           # Path to status indicator
      result_path: $.result           # Path to result data
      error_path: $.error             # Path to error messages
    
    auth_config:                       # Authentication configuration
      type: bearer_token               # Auth type: none, bearer_token, etc.
      env_var: API_TOKEN_NAME          # Environment variable name
    
    example_request:                   # Example request for testing
      query: Sample query
    
    example_response:                  # Example response format
      result: Sample result
```

## Available Templates

### 1. CrewAI
Multi-agent collaboration framework with role-based agents.
- **Framework**: `crewai`
- **Endpoint**: `/kickoff`
- **Authentication**: None

### 2. Databricks Foundation Models
Databricks LLM serving endpoints (Llama, Mistral, etc.)
- **Framework**: `databricks`
- **Endpoint**: `/serving-endpoints/{model_name}/invocations`
- **Authentication**: Bearer Token (`DATABRICKS_TOKEN`)

### 3. OpenAI Compatible
OpenAI API compatible endpoints (GPT-3.5, GPT-4, etc.)
- **Framework**: `openai`
- **Endpoint**: `/v1/chat/completions`
- **Authentication**: Bearer Token (`OPENAI_API_KEY`)

### 4. Custom REST API
Define your own custom request/response mapping
- **Framework**: `custom`
- **Endpoint**: `/process` (customizable)
- **Authentication**: None (customizable)

## Adding New Templates

To add a new template, edit `backend/config/agent_templates.yaml` and add a new entry:

```yaml
templates:
  # ... existing templates ...
  
  - name: my_custom_agent
    display_name: My Custom Agent
    description: Description of what this agent does
    framework: custom
    request_mapping:
      method: POST
      path: /my/endpoint
      headers:
        Content-Type: application/json
      body_mapping:
        input: $.description
    response_mapping:
      result_path: $.output
      error_path: $.error
    auth_config:
      type: none
    example_request:
      input: Test query
    example_response:
      output: Test response
```

Changes take effect immediately - just restart the backend service.

## JSONPath Expressions

Templates use JSONPath to map fields between the orchestrator and external agents:

### Common Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| `$.field` | Top-level field | `$.description` → extracts `description` |
| `$.nested.field` | Nested field | `$.data.message` → extracts `data.message` |
| `$.array[0]` | First array element | `$.choices[0].text` |
| `$.array[*]` | All array elements | `$.results[*].value` |

### Examples

```json
{
  "description": "User query goes here",
  "data": {
    "message": "nested message",
    "items": [
      {"id": 1, "value": "first"},
      {"id": 2, "value": "second"}
    ]
  }
}
```

- `$.description` → `"User query goes here"`
- `$.data.message` → `"nested message"`
- `$.data.items[0].value` → `"first"`
- `$.data.items[*].value` → `["first", "second"]`

## Frontend Wizard - Step 3.5

For the **Custom** template, users can now define custom mappings through an optional Step 3.5 in the registration wizard:

### What Users Can Configure

1. **Request Mapping** (JSON):
   ```json
   {
     "method": "POST",
     "path": "/custom/endpoint",
     "headers": {
       "Content-Type": "application/json"
     },
     "body_mapping": {
       "query": "$.description"
     }
   }
   ```

2. **Response Mapping** (JSON):
   ```json
   {
     "status_path": "$.status",
     "result_path": "$.data.result",
     "error_path": "$.error.message"
   }
   ```

### When Step 3.5 Appears

- Only visible when the **Custom REST API** template is selected
- Appears between Step 3 (Connection) and Step 4 (Test)
- Optional - users can use default mappings or customize them

### UI Features

- **JSON Editor**: Dark-themed monospace editor for JSON input
- **Syntax Help**: Inline examples of JSONPath expressions
- **Placeholder Text**: Pre-filled with example JSON structure
- **Validation**: JSON syntax validation before registration

## Backend Implementation

### Loading Templates

```python
from models.agent_config_template import BUILTIN_TEMPLATES

# Templates are automatically loaded from YAML on import
print(len(BUILTIN_TEMPLATES))  # 4 templates
```

### Custom Template Support

When registering an agent with custom mappings:

```python
# Frontend sends custom_config with the registration
{
  "template_id": 4,  # Custom template ID
  "custom_config": {
    "request_mapping": { ... },
    "response_mapping": { ... }
  }
}

# Backend merges with template defaults
agent_config = {
    "template_id": template_id,
    "request_mapping": custom_config.get("request_mapping") or template.request_mapping,
    "response_mapping": custom_config.get("response_mapping") or template.response_mapping
}
```

## Benefits of YAML Configuration

✅ **Easy to Edit**: No Python code changes needed
✅ **Version Control**: Track template changes in git
✅ **Non-Developer Friendly**: Product managers can add templates
✅ **Hot Reload**: Changes take effect on service restart
✅ **Validation**: YAML syntax is easier to validate
✅ **Documentation**: Comments and structure are clearer

## Troubleshooting

### Templates Not Loading

**Problem**: Templates not appearing in the frontend

**Check**:
1. YAML file exists at `backend/config/agent_templates.yaml`
2. YAML syntax is valid (use a YAML validator)
3. Backend service has been restarted
4. Check backend logs for YAML parsing errors

### Template Syntax Errors

**Problem**: `Error loading templates from YAML`

**Solution**:
- Validate YAML syntax at https://www.yamllint.com/
- Check for proper indentation (use spaces, not tabs)
- Ensure all required fields are present
- Check for typos in field names

### JSONPath Not Extracting Data

**Problem**: Test connection succeeds but no result extracted

**Solution**:
- Verify JSONPath expressions at https://jsonpath.com/
- Check the actual API response structure
- Use `$.` prefix for all paths
- Test with simpler paths first (e.g., `$.result`)

## Next Steps

1. Add more built-in templates for popular frameworks
2. Implement template marketplace/sharing
3. Add visual JSONPath builder
4. Support more authentication methods (OAuth, API Key headers, etc.)
5. Add template validation and testing tools

