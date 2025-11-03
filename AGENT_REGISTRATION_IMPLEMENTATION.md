# Agent Registration System - Implementation Guide

## 🎉 What's Been Created

### ✅ Backend Components (Complete)

#### 1. **Dummy Agent Servers** (`backend/dummy_agents/`)
Created 3 dummy agent servers that simulate different frameworks:

- **`crewai_agent_server.py`** (Port 8003)
  - Simulates CrewAI multi-agent collaboration
  - Endpoints: `/health`, `/capabilities`, `/kickoff`, `/process`
  - Returns CrewAI-style workflow responses

- **`databricks_agent_server.py`** (Port 8004)
  - Simulates Databricks Foundation Model API
  - Endpoints: `/health`, `/serving-endpoints/{model}/invocations`, `/process`
  - Returns OpenAI-compatible format

- **`openai_compatible_agent_server.py`** (Port 8005)
  - Simulates OpenAI API responses
  - Endpoints: `/health`, `/v1/models`, `/v1/chat/completions`, `/process`
  - Returns OpenAI format

#### 2. **Database Models**
- **`models/agent_config_template.py`**
  - `AgentConfigTemplate` model for storing templates
  - 4 built-in templates: CrewAI, Databricks, OpenAI-Compatible, Custom
  - Includes request/response mappings and auth configurations

#### 3. **Agent Registration Service**
- **`services/agent_registration_service.py`**
  - `AgentRegistrationService` class
  - Methods:
    - `initialize_templates()` - Load built-in templates
    - `list_templates()` - Get all templates
    - `test_agent_connection()` - Test agent before registration
    - `register_agent_with_template()` - Register with config
    - `_build_request_body()` - JSONPath request transformation
    - `_extract_response_data()` - JSONPath response extraction

#### 4. **API Endpoints** (Added to `main.py`)
```
GET  /api/agent-templates              - List all templates
GET  /api/agent-templates/{id}         - Get specific template
POST /api/agents/test-connection       - Test agent connection
POST /api/agents/register-with-template - Register agent
```

#### 5. **Dependencies** (Updated `requirements.txt`)
- Added `jsonpath-ng` for JSONPath parsing
- Added `psycopg2-binary` for PostgreSQL support

### ⏳ Frontend Components (Partial - Needs Completion)

#### What's Added:
- State variables for registration wizard in `App.jsx`
- Template management state
- Registration form state
- Test result state

#### What Still Needs To Be Done:
1. **Fetch templates function**
2. **Test connection function**
3. **Register agent function**
4. **Registration wizard UI** (5-step wizard)
5. **"Register Agent" navigation button** (for power users)
6. **CSS styles** for registration wizard

---

## 🚀 How to Complete the Frontend

### Step 1: Add Helper Functions to `App.jsx`

After the `createSession` function, add:

```javascript
// Fetch agent templates
const fetchTemplates = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/agent-templates`)
    setTemplates(response.data)
  } catch (error) {
    console.error('Error fetching templates:', error)
  }
}

// Test agent connection
const testAgentConnection = async () => {
  if (!regForm.endpoint || !regForm.template_id) {
    alert('Please enter endpoint and select template')
    return
  }

  setTestResult({ testing: true })

  try {
    const template = templates.find(t => t.id === regForm.template_id)
    
    const response = await axios.post(`${API_BASE}/api/agents/test-connection`, {
      endpoint: regForm.endpoint,
      template_config: {
        request_mapping: template.request_mapping,
        response_mapping: template.response_mapping
      },
      test_query: regForm.test_query,
      auth_headers: regForm.auth_type === 'bearer' ? {
        'Authorization': `Bearer ${regForm.auth_token}`
      } : null
    })

    setTestResult(response.data)
  } catch (error) {
    setTestResult({
      success: false,
      error: error.response?.data?.detail || error.message
    })
  }
}

// Register agent
const registerAgent = async () => {
  setRegistering(true)

  try {
    const response = await axios.post(`${API_BASE}/api/agents/register-with-template`, {
      name: regForm.name,
      description: regForm.description,
      endpoint: regForm.endpoint,
      capabilities: regForm.capabilities,
      template_id: regForm.template_id,
      auth_config: regForm.auth_type === 'bearer' ? {
        type: 'bearer_token',
        token: regForm.auth_token
      } : { type: 'none' }
    })

    alert(`✅ Agent "${response.data.name}" registered successfully!`)
    
    // Reset form and go back to agents view
    setRegistrationStep(1)
    setRegForm({
      name: '',
      description: '',
      endpoint: '',
      capabilities: [],
      template_id: null,
      auth_type: 'none',
      auth_token: '',
      test_query: 'Hello, this is a test'
    })
    setTestResult(null)
    setActiveView('agents')
    
    // Refresh agents list
    fetchAgents()
  } catch (error) {
    alert(`❌ Error: ${error.response?.data?.detail || error.message}`)
  } finally {
    setRegistering(false)
  }
}
```

### Step 2: Add UseEffect for Templates

Add after the existing useEffect:

```javascript
// Fetch templates when navigating to register agent view
useEffect(() => {
  if (activeView === 'registerAgent') {
    fetchTemplates()
  }
}, [activeView])
```

### Step 3: Add "Register Agent" Button

In the navigation section (around line 640), add the button for power users:

```javascript
{isPowerUser && (
  <>
    <button 
      className={`nav-item ${activeView === 'registerAgent' ? 'active' : ''}`}
      onClick={() => setActiveView('registerAgent')}
    >
      <span className="nav-icon">➕</span>
      Register Agent
    </button>
    
    <button 
      className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`}
      onClick={() => setActiveView('dashboard')}
    >
      <span className="nav-icon">📊</span>
      Dashboard
    </button>
    
    <button 
      className={`nav-item ${activeView === 'agents' ? 'active' : ''}`}
      onClick={() => setActiveView('agents')}
    >
      <span className="nav-icon">🤖</span>
      Agents
    </button>
  </>
)}
```

### Step 4: Add Wizard View Rendering

In the main content area (around line 655), add:

```javascript
{activeView === 'registerAgent' && renderRegisterAgentView()}
```

### Step 5: Create the Wizard View Function

Add before the `return` statement (around line 580):

```javascript
// Render Register Agent Wizard
const renderRegisterAgentView = () => (
  <div className="register-agent-container">
    <div className="register-header">
      <h1>➕ Register External Agent</h1>
      <p>Connect any REST API agent using configuration templates</p>
    </div>

    <div className="wizard-progress">
      <div className={`step ${registrationStep >= 1 ? 'active' : ''}`}>1. Template</div>
      <div className={`step ${registrationStep >= 2 ? 'active' : ''}`}>2. Basic Info</div>
      <div className={`step ${registrationStep >= 3 ? 'active' : ''}`}>3. Connection</div>
      <div className={`step ${registrationStep >= 4 ? 'active' : ''}`}>4. Test</div>
      <div className={`step ${registrationStep >= 5 ? 'active' : ''}`}>5. Register</div>
    </div>

    <div className="wizard-content">
      {/* Step 1: Select Template */}
      {registrationStep === 1 && (
        <div className="wizard-step">
          <h2>Select Agent Template</h2>
          <p>Choose a template that matches your agent's framework</p>
          
          <div className="template-grid">
            {templates.map(template => (
              <div 
                key={template.id}
                className={`template-card ${regForm.template_id === template.id ? 'selected' : ''}`}
                onClick={() => setRegForm({...regForm, template_id: template.id})}
              >
                <h3>{template.display_name}</h3>
                <p>{template.description}</p>
                <div className="template-badge">{template.framework}</div>
              </div>
            ))}
          </div>

          <div className="wizard-actions">
            <button 
              className="btn-next"
              onClick={() => setRegistrationStep(2)}
              disabled={!regForm.template_id}
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Basic Info */}
      {registrationStep === 2 && (
        <div className="wizard-step">
          <h2>Basic Information</h2>
          
          <div className="form-group">
            <label>Agent Name *</label>
            <input 
              type="text"
              value={regForm.name}
              onChange={(e) => setRegForm({...regForm, name: e.target.value})}
              placeholder="e.g., My Research Agent"
            />
          </div>

          <div className="form-group">
            <label>Description *</label>
            <textarea
              value={regForm.description}
              onChange={(e) => setRegForm({...regForm, description: e.target.value})}
              placeholder="What does this agent do?"
              rows={3}
            />
          </div>

          <div className="form-group">
            <label>Capabilities</label>
            <input 
              type="text"
              value={regForm.capabilities.join(', ')}
              onChange={(e) => setRegForm({
                ...regForm, 
                capabilities: e.target.value.split(',').map(c => c.trim()).filter(c => c)
              })}
              placeholder="e.g., research, analysis, writing"
            />
            <small>Comma-separated list of capabilities</small>
          </div>

          <div className="wizard-actions">
            <button className="btn-back" onClick={() => setRegistrationStep(1)}>
              ← Back
            </button>
            <button 
              className="btn-next"
              onClick={() => setRegistrationStep(3)}
              disabled={!regForm.name || !regForm.description}
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Connection */}
      {registrationStep === 3 && (
        <div className="wizard-step">
          <h2>Connection Settings</h2>
          
          <div className="form-group">
            <label>Endpoint URL *</label>
            <input 
              type="text"
              value={regForm.endpoint}
              onChange={(e) => setRegForm({...regForm, endpoint: e.target.value})}
              placeholder="https://your-agent.com/api"
            />
          </div>

          <div className="form-group">
            <label>Authentication</label>
            <select 
              value={regForm.auth_type}
              onChange={(e) => setRegForm({...regForm, auth_type: e.target.value})}
            >
              <option value="none">None</option>
              <option value="bearer">Bearer Token</option>
            </select>
          </div>

          {regForm.auth_type === 'bearer' && (
            <div className="form-group">
              <label>Authorization Token</label>
              <input 
                type="password"
                value={regForm.auth_token}
                onChange={(e) => setRegForm({...regForm, auth_token: e.target.value})}
                placeholder="Enter your API token"
              />
            </div>
          )}

          <div className="wizard-actions">
            <button className="btn-back" onClick={() => setRegistrationStep(2)}>
              ← Back
            </button>
            <button 
              className="btn-next"
              onClick={() => setRegistrationStep(4)}
              disabled={!regForm.endpoint}
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Test Connection */}
      {registrationStep === 4 && (
        <div className="wizard-step">
          <h2>Test Connection</h2>
          <p>Send a test request to verify the agent is accessible</p>
          
          <div className="form-group">
            <label>Test Query</label>
            <input 
              type="text"
              value={regForm.test_query}
              onChange={(e) => setRegForm({...regForm, test_query: e.target.value})}
              placeholder="Hello, this is a test"
            />
          </div>

          <button className="btn-test" onClick={testAgentConnection}>
            🧪 Test Connection
          </button>

          {testResult && (
            <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
              {testResult.testing ? (
                <p>Testing connection...</p>
              ) : testResult.success ? (
                <>
                  <h3>✅ Connection Successful!</h3>
                  <p>Status: {testResult.status_code}</p>
                  {testResult.extracted_result && (
                    <div className="result-preview">
                      <strong>Response:</strong>
                      <pre>{JSON.stringify(testResult.extracted_result, null, 2)}</pre>
                    </div>
                  )}
                </>
              ) : (
                <>
                  <h3>❌ Connection Failed</h3>
                  <p>{testResult.error}</p>
                </>
              )}
            </div>
          )}

          <div className="wizard-actions">
            <button className="btn-back" onClick={() => setRegistrationStep(3)}>
              ← Back
            </button>
            <button 
              className="btn-next"
              onClick={() => setRegistrationStep(5)}
              disabled={!testResult || !testResult.success}
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Step 5: Register */}
      {registrationStep === 5 && (
        <div className="wizard-step">
          <h2>Review & Register</h2>
          
          <div className="review-section">
            <h3>Agent Details</h3>
            <div className="review-item">
              <strong>Name:</strong> {regForm.name}
            </div>
            <div className="review-item">
              <strong>Description:</strong> {regForm.description}
            </div>
            <div className="review-item">
              <strong>Endpoint:</strong> {regForm.endpoint}
            </div>
            <div className="review-item">
              <strong>Template:</strong> {templates.find(t => t.id === regForm.template_id)?.display_name}
            </div>
            <div className="review-item">
              <strong>Capabilities:</strong> {regForm.capabilities.join(', ')}
            </div>
          </div>

          <div className="wizard-actions">
            <button className="btn-back" onClick={() => setRegistrationStep(4)}>
              ← Back
            </button>
            <button 
              className="btn-register"
              onClick={registerAgent}
              disabled={registering}
            >
              {registering ? 'Registering...' : '✅ Register Agent'}
            </button>
          </div>
        </div>
      )}
    </div>
  </div>
)
```

### Step 6: Add CSS Styles

Add to `frontend/src/App.css`:

```css
/* Register Agent Wizard */
.register-agent-container {
  padding: 30px;
  max-width: 900px;
  margin: 0 auto;
}

.register-header {
  text-align: center;
  margin-bottom: 40px;
}

.register-header h1 {
  font-size: 2rem;
  margin-bottom: 10px;
}

.wizard-progress {
  display: flex;
  justify-content: space-between;
  margin-bottom: 40px;
  padding: 0 20px;
}

.wizard-progress .step {
  flex: 1;
  padding: 12px;
  text-align: center;
  background: #f0f0f0;
  border-radius: 6px;
  margin: 0 5px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  transition: all 0.3s;
}

.wizard-progress .step.active {
  background: var(--accent-color);
  color: white;
}

.wizard-content {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.wizard-step h2 {
  margin-bottom: 10px;
  color: var(--text-primary);
}

.wizard-step > p {
  margin-bottom: 30px;
  color: var(--text-secondary);
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.template-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-card:hover {
  border-color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.template-card.selected {
  border-color: var(--accent-color);
  background: #f0fdf4;
}

.template-card h3 {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
}

.template-card p {
  margin: 0 0 12px 0;
  font-size: 0.9rem;
  color: #666;
}

.template-badge {
  display: inline-block;
  padding: 4px 12px;
  background: var(--accent-color);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
}

.form-group small {
  display: block;
  margin-top: 4px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.wizard-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn-back,
.btn-next,
.btn-test,
.btn-register {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-back {
  background: #f0f0f0;
  color: #666;
}

.btn-next,
.btn-register {
  background: var(--accent-color);
  color: white;
}

.btn-test {
  background: #3b82f6;
  color: white;
  width: 100%;
  margin-bottom: 20px;
}

.btn-back:hover,
.btn-next:hover,
.btn-test:hover,
.btn-register:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.btn-next:disabled,
.btn-register:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.test-result {
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.test-result.success {
  background: #f0fdf4;
  border: 1px solid #86efac;
}

.test-result.error {
  background: #fef2f2;
  border: 1px solid #fca5a5;
}

.result-preview {
  margin-top: 12px;
  padding: 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.result-preview pre {
  margin: 8px 0 0 0;
  font-size: 0.85rem;
  overflow-x: auto;
}

.review-section {
  background: #f9fafb;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.review-item {
  padding: 12px 0;
  border-bottom: 1px solid #e0e0e0;
}

.review-item:last-child {
  border-bottom: none;
}

.review-item strong {
  display: inline-block;
  min-width: 120px;
  color: var(--text-secondary);
}
```

---

## 🧪 Testing the System

### Step 1: Start All Dummy Agent Servers

```bash
# Terminal 1 - CrewAI Agent
cd backend/dummy_agents
python crewai_agent_server.py

# Terminal 2 - Databricks Agent
python databricks_agent_server.py

# Terminal 3 - OpenAI Compatible Agent
python openai_compatible_agent_server.py
```

### Step 2: Start Main Backend

```bash
# Terminal 4 - Main Orchestrator
cd backend
python main.py
```

### Step 3: Start Frontend

```bash
# Terminal 5 - Frontend
cd frontend
npm run dev
```

### Step 4: Test Registration

1. Open browser: `http://localhost:3000`
2. Toggle "Power User" mode
3. Click "➕ Register Agent"
4. Follow wizard:
   - Select "CrewAI" template
   - Enter name: "Test CrewAI Agent"
   - Enter endpoint: `http://localhost:8003`
   - Test connection
   - Register

---

## 📊 Database Schema

The system will create this table automatically:

```sql
CREATE TABLE agent_config_templates (
  id SERIAL PRIMARY KEY,
  name VARCHAR UNIQUE NOT NULL,
  display_name VARCHAR,
  description VARCHAR,
  framework VARCHAR,
  icon_url VARCHAR,
  request_mapping JSONB,
  response_mapping JSONB,
  auth_config JSONB,
  example_request JSONB,
  example_response JSONB,
  is_builtin BOOLEAN DEFAULT TRUE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

---

## 🔄 Using PostgreSQL Instead of SQLite

To use PostgreSQL, update `backend/config.py`:

```python
class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/orchestrator"
    # ... rest of settings
```

---

## ✅ Summary

### What Works Now:
- ✅ 3 dummy agent servers running on ports 8003-8005
- ✅ Backend API endpoints for templates and registration
- ✅ Database models and service layer
- ✅ JSONPath-based request/response transformation
- ✅ Connection testing before registration

### What You Need To Do:
1. Add the frontend functions (copy from Step 1 above)
2. Add the wizard UI (copy from Step 5 above)
3. Add the CSS styles (copy from Step 6 above)
4. Add the navigation button (copy from Step 3 above)
5. Test the complete flow

---

**Total Implementation Time:** ~30 minutes to add frontend code
**Files Modified:** 2 (App.jsx, App.css)
**Lines of Code to Add:** ~500 lines

---

Would you like me to create the complete `App.jsx` file with all the changes, or would you prefer to add them incrementally?

