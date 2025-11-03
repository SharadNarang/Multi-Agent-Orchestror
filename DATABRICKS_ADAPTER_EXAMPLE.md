# Databricks Agent Adapter - Request/Response Mapping Example

## Overview

This document shows a step-by-step example of how the adapter transforms requests and responses when communicating with a Databricks Foundation Model agent.

---

## Scenario

**User Query**: "Explain quantum computing in simple terms"

**Registered Agent**: Databricks Llama 2 70B model
- Endpoint: `https://adb-workspace.cloud.databricks.com`
- Template: `databricks_foundation`
- Model: `llama-2-70b-chat`

---

## Step 1️⃣: User Creates Task

### Frontend Request to Orchestrator

```http
POST /api/tasks HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "description": "Explain quantum computing in simple terms",
  "user_id": "demo-user",
  "session_id": "sess_12345"
}
```

---

## Step 2️⃣: Task Planner Selects Agent

The Task Planner analyzes the request and creates an execution plan:

```json
{
  "task_id": "task_67890",
  "plan": {
    "steps": [
      {
        "agent_id": 3,
        "agent_name": "DatabricksLLM",
        "description": "Explain quantum computing in simple terms",
        "capabilities_needed": ["explanation", "education"]
      }
    ]
  }
}
```

---

## Step 3️⃣: Task Executor Prepares Request

The Task Executor retrieves the agent configuration from the database:

```json
{
  "id": 3,
  "name": "DatabricksLLM",
  "endpoint": "https://adb-workspace.cloud.databricks.com",
  "agent_type": "api",
  "config": {
    "template_id": 2,
    "template_name": "databricks_foundation",
    "request_mapping": {
      "method": "POST",
      "path": "/serving-endpoints/llama-2-70b-chat/invocations",
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
    }
  }
}
```

---

## Step 4️⃣: Adapter Transforms Request

### Input to Adapter (from Orchestrator)

```json
{
  "description": "Explain quantum computing in simple terms"
}
```

### Adapter Processing

The `AgentRegistrationService._build_request_body()` method:

1. **Processes `body_mapping`**:
   ```python
   body_mapping = {
       "messages": [
           {
               "role": "user",
               "content": "$.description"  # JSONPath expression
           }
       ],
       "max_tokens": 1000,
       "temperature": 0.7
   }
   ```

2. **Extracts value using JSONPath**:
   - `$.description` → extracts `"Explain quantum computing in simple terms"`

3. **Builds transformed body**:
   ```json
   {
       "messages": [
           {
               "role": "user",
               "content": "Explain quantum computing in simple terms"
           }
       ],
       "max_tokens": 1000,
       "temperature": 0.7
   }
   ```

4. **Adds authentication header**:
   ```python
   headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer dapi12345abcdef..."
   }
   ```

### Output from Adapter (to Databricks)

```http
POST /serving-endpoints/llama-2-70b-chat/invocations HTTP/1.1
Host: adb-workspace.cloud.databricks.com
Content-Type: application/json
Authorization: Bearer dapi12345abcdef...

{
  "messages": [
    {
      "role": "user",
      "content": "Explain quantum computing in simple terms"
    }
  ],
  "max_tokens": 1000,
  "temperature": 0.7
}
```

---

## Step 5️⃣: Databricks Responds

### Raw Response from Databricks

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1699000000,
  "model": "llama-2-70b-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum computing is a revolutionary approach to computation that leverages the principles of quantum mechanics. Unlike classical computers that use bits (0s and 1s), quantum computers use quantum bits or 'qubits' which can exist in multiple states simultaneously through a phenomenon called superposition.\n\nThink of it like this: a classical bit is like a light switch that's either on or off. A qubit is like a dimmer switch that can be at any level between fully on and fully off, and even in multiple positions at once until you measure it.\n\nThis allows quantum computers to process vast amounts of information in parallel, making them potentially much more powerful for certain types of problems like cryptography, drug discovery, and complex simulations."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 156,
    "total_tokens": 168
  }
}
```

---

## Step 6️⃣: Adapter Extracts Result

### Response Mapping Configuration

```json
{
  "status_path": "$.choices[0].finish_reason",
  "result_path": "$.choices[0].message.content",
  "error_path": "$.error.message"
}
```

### Adapter Processing

The `AgentRegistrationService._extract_response_data()` method:

1. **Parse JSONPath for result**:
   ```python
   result_path = "$.choices[0].message.content"
   jsonpath_expr = parse(result_path)
   ```

2. **Apply JSONPath to response**:
   ```python
   matches = jsonpath_expr.find(response_data)
   # Navigates: response → choices → [0] → message → content
   ```

3. **Extract matched value**:
   ```
   "Quantum computing is a revolutionary approach to computation..."
   ```

### Output from Adapter (to Orchestrator)

```json
{
  "response": "Quantum computing is a revolutionary approach to computation that leverages the principles of quantum mechanics. Unlike classical computers that use bits (0s and 1s), quantum computers use quantum bits or 'qubits' which can exist in multiple states simultaneously through a phenomenon called superposition.\n\nThink of it like this: a classical bit is like a light switch that's either on or off. A qubit is like a dimmer switch that can be at any level between fully on and fully off, and even in multiple positions at once until you measure it.\n\nThis allows quantum computers to process vast amounts of information in parallel, making them potentially much more powerful for certain types of problems like cryptography, drug discovery, and complex simulations."
}
```

---

## Step 7️⃣: Task Executor Returns Result

### Response to Frontend

```json
{
  "task_id": "task_67890",
  "status": "completed",
  "result": {
    "steps": [
      {
        "agent_id": 3,
        "agent_name": "DatabricksLLM",
        "content": {
          "response": "Quantum computing is a revolutionary approach to computation that leverages the principles of quantum mechanics. Unlike classical computers that use bits (0s and 1s), quantum computers use quantum bits or 'qubits' which can exist in multiple states simultaneously through a phenomenon called superposition.\n\nThink of it like this: a classical bit is like a light switch that's either on or off. A qubit is like a dimmer switch that can be at any level between fully on and fully off, and even in multiple positions at once until you measure it.\n\nThis allows quantum computers to process vast amounts of information in parallel, making them potentially much more powerful for certain types of problems like cryptography, drug discovery, and complex simulations."
        }
      }
    ]
  }
}
```

---

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER REQUEST                                │
│  "Explain quantum computing in simple terms"                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR INPUT                              │
│  {                                                                   │
│    "description": "Explain quantum computing in simple terms"       │
│  }                                                                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ╔════════════▼════════════╗
                    ║   ADAPTER TRANSFORM     ║
                    ║   (Request Mapping)     ║
                    ╚════════════╦════════════╝
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
         1. Extract        2. Transform       3. Add Auth
         JSONPath          Structure          Header
              │                  │                  │
              └──────────────────┴──────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  DATABRICKS API REQUEST                              │
│  POST /serving-endpoints/llama-2-70b-chat/invocations               │
│  Authorization: Bearer dapi...                                       │
│                                                                      │
│  {                                                                   │
│    "messages": [                                                     │
│      {                                                               │
│        "role": "user",                                               │
│        "content": "Explain quantum computing in simple terms"       │
│      }                                                               │
│    ],                                                                │
│    "max_tokens": 1000,                                               │
│    "temperature": 0.7                                                │
│  }                                                                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
                        ┏━━━━━━━━━━━━━━┓
                        ┃  DATABRICKS  ┃
                        ┃  PROCESSES   ┃
                        ┗━━━━━━━┬━━━━━━┛
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   DATABRICKS API RESPONSE                            │
│  {                                                                   │
│    "choices": [                                                      │
│      {                                                               │
│        "message": {                                                  │
│          "role": "assistant",                                        │
│          "content": "Quantum computing is a revolutionary..."       │
│        },                                                            │
│        "finish_reason": "stop"                                       │
│      }                                                               │
│    ]                                                                 │
│  }                                                                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ╔════════════▼════════════╗
                    ║   ADAPTER EXTRACT       ║
                    ║   (Response Mapping)    ║
                    ╚════════════╦════════════╝
                                 │
              Apply JSONPath: $.choices[0].message.content
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR OUTPUT                               │
│  {                                                                   │
│    "response": "Quantum computing is a revolutionary..."            │
│  }                                                                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        USER SEES RESULT                              │
│  "Quantum computing is a revolutionary approach to                   │
│   computation that leverages the principles of quantum               │
│   mechanics..."                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Code Implementation

### Backend: Agent Registration Service

```python
# File: backend/services/agent_registration_service.py

def _build_request_body(self, body_mapping, input_data):
    """
    Transform orchestrator input → Databricks format
    """
    result = {}
    
    for key, value in body_mapping.items():
        if isinstance(value, str) and value.startswith("$."):
            # JSONPath expression: $.description
            jsonpath_expr = jsonpath_parse(value)
            matches = jsonpath_expr.find(input_data)
            if matches:
                result[key] = matches[0].value
        elif isinstance(value, dict):
            # Recursive for nested objects
            result[key] = self._build_request_body(value, input_data)
        elif isinstance(value, list):
            # Handle arrays
            result[key] = [
                self._build_request_body(item, input_data) 
                if isinstance(item, dict) else item
                for item in value
            ]
        else:
            # Static value
            result[key] = value
    
    return result

def _extract_response_data(self, response_data, response_mapping):
    """
    Extract result from Databricks response
    """
    result_path = response_mapping.get("result_path", "$.result")
    
    # Parse JSONPath: $.choices[0].message.content
    jsonpath_expr = jsonpath_parse(result_path)
    matches = jsonpath_expr.find(response_data)
    
    if matches:
        return matches[0].value
    else:
        # Fallback: return whole response
        return json.dumps(response_data)
```

---

## Key Takeaways

### 1. **No Code Changes Needed**
When registering a Databricks agent, the user only provides:
- Endpoint URL
- Authentication token
- Selects "Databricks Foundation Models" template

All mapping is handled automatically!

### 2. **JSONPath is the Glue**
```
Orchestrator Field → JSONPath → Databricks Field
───────────────────────────────────────────────
$.description     →  messages[0].content
$.choices[0].message.content  ←  Databricks response
```

### 3. **Configuration-Driven**
All mapping rules are in `backend/config/agent_templates.yaml`:
```yaml
databricks_foundation:
  request_mapping:
    body_mapping:
      messages:
        - role: user
          content: $.description  # ← Magic happens here
```

### 4. **Supports Multiple Models**
Same template works for:
- Llama 2 7B, 13B, 70B
- Mistral 7B
- Mixtral 8x7B
- Any Databricks Foundation Model API

Just change the endpoint path: `/serving-endpoints/{model-name}/invocations`

---

## Testing the Adapter

You can test the Databricks adapter without a real Databricks account using the dummy server:

```bash
# Start dummy Databricks server
python backend/dummy_agents/databricks_agent_server.py

# Register in the orchestrator
curl -X POST http://localhost:8000/api/agents/register-with-template \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DatabricksTest",
    "description": "Test Databricks integration",
    "endpoint": "http://localhost:8004",
    "capabilities": ["explanation", "reasoning"],
    "template_id": 2
  }'
```

---

## Error Handling Example

### Databricks Returns Error

```json
{
  "error": {
    "message": "Model not found: invalid-model",
    "type": "invalid_request_error"
  }
}
```

### Adapter Extracts Error

Using `error_path: $.error.message`:

```python
# Result extracted: "Model not found: invalid-model"
```

### Orchestrator Returns to User

```json
{
  "task_id": "task_67890",
  "status": "failed",
  "result": {
    "error": "Model not found: invalid-model"
  }
}
```

---

## Summary

The adapter acts as a **universal translator**:

1. **Receives** orchestrator's simple format
2. **Transforms** to Databricks API format using JSONPath mappings
3. **Calls** Databricks endpoint
4. **Receives** Databricks response (complex structure)
5. **Extracts** the actual result using JSONPath
6. **Returns** clean result to orchestrator

**Zero code changes** needed for each new Databricks model - just configure the template! 🎉

