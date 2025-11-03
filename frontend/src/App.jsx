import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {
  const [agents, setAgents] = useState([])
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [activeView, setActiveView] = useState('chat') // chat, dashboard, agents, buildAgents, registerAgent
  const [agentStats, setAgentStats] = useState(null)
  const [tasks, setTasks] = useState([])
  const [isPowerUser, setIsPowerUser] = useState(false) // Admin mode toggle
  const [isEmbedded, setIsEmbedded] = useState(false)
  
  // Registration wizard state
  const [templates, setTemplates] = useState([])
  const [registrationStep, setRegistrationStep] = useState(1)
  const [regForm, setRegForm] = useState({
    name: '',
    description: '',
    endpoint: '',
    capabilities: [],
    template_id: null,
    auth_type: 'none',
    auth_token: '',
    test_query: 'Hello, this is a test',
    custom_request_mapping: '',
    custom_response_mapping: ''
  })
  const [testResult, setTestResult] = useState(null)
  const [registering, setRegistering] = useState(false)

  // Detect if running in iFrame
  useEffect(() => {
    const inIframe = window.self !== window.top
    setIsEmbedded(inIframe)
    
    if (inIframe) {
      console.log('🖼️ Running in iFrame (Adobe Agentic Builder)')
      
      // Notify parent that we're ready
      window.parent.postMessage({
        type: 'ORCHESTRATOR_READY',
        data: { status: 'ready' }
      }, '*')
      
      // Listen for messages from parent
      const handleParentMessage = (event) => {
        // Validate origin for production
        // if (event.origin !== 'https://agentic-builder-dev.corp.adobe.com') return
        
        const { type, data } = event.data
        
        switch (type) {
          case 'EXECUTE_TASK':
            // Handle task from parent
            if (data.query) {
              setInputMessage(data.query)
              // Auto-submit if requested
              if (data.autoSubmit) {
                setTimeout(() => handleSendMessage(), 100)
              }
            }
            break
          case 'SET_VIEW':
            if (data.view) {
              setActiveView(data.view)
            }
            break
          case 'TOGGLE_SIDEBAR':
            setSidebarOpen(prev => !prev)
            break
          default:
            console.log('Unknown message type:', type)
        }
      }
      
      window.addEventListener('message', handleParentMessage)
      return () => window.removeEventListener('message', handleParentMessage)
    }
  }, [])
  
  // Send status updates to parent if embedded
  useEffect(() => {
    if (isEmbedded && window.parent) {
      window.parent.postMessage({
        type: 'TASK_STATUS_UPDATE',
        data: {
          taskCount: tasks.length,
          activeAgents: agents.filter(a => a.status === 'active').length
        }
      }, '*')
    }
  }, [tasks, agents, isEmbedded])

  useEffect(() => {
    fetchAgents()
    createSession()
    fetchAgentStats()
  }, [])

  // Fetch templates when navigating to register agent view
  useEffect(() => {
    if (activeView === 'registerAgent') {
      fetchTemplates()
    }
  }, [activeView])

  const fetchAgents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/agents`)
      setAgents(response.data)
    } catch (error) {
      console.error('Error fetching agents:', error)
    }
  }

  const fetchAgentStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/agents/stats`)
      setAgentStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const createSession = async () => {
    try {
      const response = await axios.post(`${API_BASE}/api/sessions`, {
        user_id: 'user-' + Date.now()
      })
      setSessionId(response.data.session_id)
    } catch (error) {
      console.error('Error creating session:', error)
    }
  }

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

  // Check if selected template is custom
  const isCustomTemplate = () => {
    const selectedTemplate = templates.find(t => t.id === regForm.template_id)
    return selectedTemplate?.name === 'custom'
  }

  // Register agent
  const registerAgent = async () => {
    setRegistering(true)

    try {
      // Prepare custom config if using custom template and mappings provided
      let customConfig = null
      if (isCustomTemplate() && (regForm.custom_request_mapping || regForm.custom_response_mapping)) {
        customConfig = {}
        if (regForm.custom_request_mapping) {
          try {
            customConfig.request_mapping = JSON.parse(regForm.custom_request_mapping)
          } catch (e) {
            alert('Invalid JSON in Request Mapping')
            setRegistering(false)
            return
          }
        }
        if (regForm.custom_response_mapping) {
          try {
            customConfig.response_mapping = JSON.parse(regForm.custom_response_mapping)
          } catch (e) {
            alert('Invalid JSON in Response Mapping')
            setRegistering(false)
            return
          }
        }
      }

      const response = await axios.post(`${API_BASE}/api/agents/register-with-template`, {
        name: regForm.name,
        description: regForm.description,
        endpoint: regForm.endpoint,
        capabilities: regForm.capabilities,
        template_id: regForm.template_id,
        custom_config: customConfig,
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
        test_query: 'Hello, this is a test',
        custom_request_mapping: '',
        custom_response_mapping: ''
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

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    }

    setMessages([...messages, userMessage])
    const taskDescription = inputMessage
    setInputMessage('')
    setLoading(true)

    try {
      // Create the task
      const taskResponse = await axios.post(`${API_BASE}/api/tasks`, {
        description: taskDescription,
        user_id: 'demo-user',
        session_id: sessionId
      })

      setTasks(prev => [taskResponse.data, ...prev])
      const taskId = taskResponse.data.task_id

      // Show initial processing message
      const processingMessage = {
        role: 'assistant',
        content: `🔄 Processing your request...\n\n🎯 Task ID: ${taskId}\n📊 Status: ${taskResponse.data.status}\n\nCoordinating with AI agents:\n${taskResponse.data.plan?.steps?.map((s, i) => `${i + 1}. ${s.agent_name || 'Agent'}: ${s.description}`).join('\n') || 'Planning in progress...'}\n\n⏳ Please wait while agents process your request...`,
        timestamp: new Date().toISOString(),
        taskId: taskId
      }

      setMessages(prev => [...prev, processingMessage])

      // Poll for task completion
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await axios.get(`${API_BASE}/api/tasks/${taskId}`)
          const taskStatus = statusResponse.data

          if (taskStatus.status === 'completed') {
            clearInterval(pollInterval)
            setLoading(false)

            // Extract the agent's response from the result
            let agentResponse = 'Task completed successfully!'
            
            if (taskStatus.result && taskStatus.result.steps && taskStatus.result.steps.length > 0) {
              const firstStep = taskStatus.result.steps[0]
              if (firstStep.content && firstStep.content.response) {
                agentResponse = firstStep.content.response
              } else if (firstStep.content && firstStep.content.status) {
                agentResponse = JSON.stringify(firstStep.content, null, 2)
              }
            } else if (taskStatus.result && taskStatus.result.summary) {
              agentResponse = taskStatus.result.summary
            }

            const resultMessage = {
              role: 'assistant',
              content: agentResponse,
              timestamp: new Date().toISOString(),
              taskId: taskId
            }

            setMessages(prev => {
              // Remove the processing message and add the result
              const withoutProcessing = prev.filter(m => m.taskId !== taskId)
              return [...withoutProcessing, resultMessage]
            })

          } else if (taskStatus.status === 'failed') {
            clearInterval(pollInterval)
            setLoading(false)

            const errorMessage = {
              role: 'assistant',
              content: `❌ Task failed.\n\nError: ${taskStatus.result?.error || 'Unknown error occurred'}`,
              timestamp: new Date().toISOString(),
              taskId: taskId
            }

            setMessages(prev => {
              const withoutProcessing = prev.filter(m => m.taskId !== taskId)
              return [...withoutProcessing, errorMessage]
            })
          }
        } catch (error) {
          console.error('Error polling task status:', error)
        }
      }, 2000) // Poll every 2 seconds

      // Timeout after 60 seconds
      setTimeout(() => {
        clearInterval(pollInterval)
        setLoading(false)
      }, 60000)

    } catch (error) {
      console.error('Error creating task:', error)
      const errorMessage = {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error creating the task. Please ensure:\n• Backend services are running (http://localhost:8000)\n• Groq API key is configured\n• All agents are registered and active',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
      setLoading(false)
    }
  }

  const handleNewChat = () => {
    setMessages([])
    createSession()
    setActiveView('chat')
  }

  const checkAgentHealth = async (agentId) => {
    try {
      await axios.post(`${API_BASE}/api/agents/${agentId}/health`)
      fetchAgents()
      alert('Health check initiated!')
    } catch (error) {
      alert('Health check failed')
    }
  }

  const suggestedPrompts = [
    "Research the latest AI trends and create a summary",
    "Analyze the benefits of automation in business",
    "Explain the key features of LangGraph framework",
    "What are best practices for multi-agent systems?"
  ]

  // Render Chat View
  const renderChatView = () => (
    <div className="chat-container">
      {messages.length === 0 ? (
        <div className="welcome-screen">
          <h1>How can I help you today?</h1>
          
          <div className="quick-actions">
            <button className="action-btn primary">
              <span>▶</span> Get Started
            </button>
            <button className="action-btn" onClick={() => setActiveView('agents')}>
              <span>🤖</span> AGENT DISCOVERY
            </button>
            <button className="action-btn" onClick={() => setActiveView('dashboard')}>
              <span>📊</span> OBSERVABILITY
            </button>
          </div>

          <div className="suggested-prompts">
            <h3>Suggested prompts to try:</h3>
            <div className="prompts-grid">
              {suggestedPrompts.map((prompt, index) => (
                <div 
                  key={index} 
                  className="prompt-card"
                  onClick={() => setInputMessage(prompt)}
                >
                  {prompt}
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-avatar">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-time">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )

  // Render Dashboard View
  const renderDashboardView = () => (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>📊 Agent Observability and Monitoring</h1>
        <p>Monitor your multi-agent orchestrator system</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-icon">🤖</div>
          <div className="stat-content">
            <h3>{agentStats?.total || 0}</h3>
            <p>Total Agents</p>
          </div>
        </div>

        <div className="stat-card success">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>{agentStats?.active || 0}</h3>
            <p>Active Agents</p>
          </div>
        </div>

        <div className="stat-card warning">
          <div className="stat-icon">⏸️</div>
          <div className="stat-content">
            <h3>{agentStats?.inactive || 0}</h3>
            <p>Inactive Agents</p>
          </div>
        </div>

        <div className="stat-card info">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <h3>{tasks.length}</h3>
            <p>Tasks Created</p>
          </div>
        </div>
      </div>

      <div className="dashboard-section">
        <h2>System Status</h2>
        <div className="status-grid">
          <div className="status-item">
            <span className="status-indicator active"></span>
            <div className="status-info">
              <strong>Main Orchestrator</strong>
              <span>http://localhost:8000</span>
            </div>
          </div>
          <div className="status-item">
            <span className="status-indicator active"></span>
            <div className="status-info">
              <strong>A2A Server</strong>
              <span>http://localhost:8001</span>
            </div>
          </div>
          <div className="status-item">
            <span className="status-indicator active"></span>
            <div className="status-info">
              <strong>API Agent Server</strong>
              <span>http://localhost:8002</span>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-section">
        <h2>Agent Types Distribution</h2>
        <div className="agent-types">
          {agentStats?.by_type && Object.entries(agentStats.by_type).map(([type, count]) => (
            <div key={type} className="type-bar">
              <div className="type-info">
                <span>{type}</span>
                <strong>{count}</strong>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${(count / agentStats.total) * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {tasks.length > 0 && (
        <div className="dashboard-section">
          <h2>Recent Tasks</h2>
          <div className="tasks-list">
            {tasks.slice(0, 5).map((task, index) => (
              <div key={index} className="task-item">
                <div className="task-icon">📝</div>
                <div className="task-info">
                  <strong>Task #{task.task_id}</strong>
                  <span className={`status-badge ${task.status}`}>{task.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )

  // Render Agent Discovery View
  const renderAgentsView = () => (
    <div className="agents-container">
      <div className="agents-header">
        <h1>🤖 Agent Discovery</h1>
        <p>Explore and manage your AI agents</p>
      </div>

      <div className="agents-grid">
        {agents.map((agent) => (
          <div key={agent.id} className="agent-card">
            <div className="agent-card-header">
              <div className="agent-icon">
                {agent.agent_type === 'a2a_server' ? '🔄' : '⚡'}
              </div>
              <span className={`status-badge ${agent.status}`}>
                {agent.status}
              </span>
            </div>

            <h3>{agent.name}</h3>
            <p className="agent-description">{agent.description}</p>

            <div className="agent-type">
              <strong>Type:</strong> {agent.agent_type}
            </div>

            <div className="agent-endpoint">
              <strong>Endpoint:</strong>
              <code>{agent.endpoint}</code>
            </div>

            <div className="agent-capabilities">
              <strong>Capabilities:</strong>
              <div className="capability-tags">
                {agent.capabilities?.map((cap, idx) => (
                  <span key={idx} className="capability-tag">{cap}</span>
                ))}
              </div>
            </div>

            <div className="agent-actions">
              <button 
                className="btn-health"
                onClick={() => checkAgentHealth(agent.id)}
              >
                💚 Health Check
              </button>
              <button className="btn-details">
                ℹ️ Details
              </button>
            </div>

            <div className="agent-meta">
              <small>ID: {agent.id} • Created: {new Date(agent.created_at).toLocaleDateString()}</small>
            </div>
          </div>
        ))}
      </div>

      {agents.length === 0 && (
        <div className="empty-agents">
          <div className="empty-icon">🤖</div>
          <h3>No agents registered yet</h3>
          <p>Register agents via the API or backend to see them here.</p>
        </div>
      )}
    </div>
  )

  // Render Build Agents View
  const renderBuildAgentsView = () => (
    <div className="build-agents-container">
      <div className="build-agents-header-bar">
        <div className="header-info">
          <div className="adobe-logo-small">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="32" height="32" rx="6" fill="#EB1000"/>
              <path d="M16 8L9 24H12.5L14 20.5H18L19.5 24H23L16 8Z" fill="white"/>
              <path d="M16 12L18.5 18.5H13.5L16 12Z" fill="white"/>
            </svg>
          </div>
          <div className="header-text">
            <h2>Adobe Agentic Builder</h2>
            <p>Design, configure, and deploy custom AI agents</p>
          </div>
        </div>
        <a 
          href="https://agentic-builder-dev.corp.adobe.com/agent-space"
          target="_blank"
          rel="noopener noreferrer"
          className="open-new-tab-btn"
          title="Open in new tab"
        >
          <span>↗</span>
        </a>
      </div>

      <div className="agentic-builder-iframe-container">
        <iframe 
          src="https://agentic-builder-dev.corp.adobe.com/agent-space"
          className="agentic-builder-iframe"
          title="Adobe Agentic Builder"
          allow="clipboard-write; clipboard-read"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
        />
      </div>
    </div>
  )

  // Render Register Agent Wizard
  const renderRegisterAgentView = () => (
    <div className="register-agent-container">
      <div className="register-header">
        <h1>➕ Register External Agent</h1>
        <p>Connect any REST API agent using configuration templates</p>
      </div>

      <div className="wizard-progress">
        <div className={`wizard-step-indicator ${registrationStep >= 1 ? 'active' : ''}`}>1. Template</div>
        <div className={`wizard-step-indicator ${registrationStep >= 2 ? 'active' : ''}`}>2. Info</div>
        <div className={`wizard-step-indicator ${registrationStep >= 3 ? 'active' : ''}`}>3. Connection</div>
        {isCustomTemplate() && (
          <div className={`wizard-step-indicator ${registrationStep >= 3.5 ? 'active' : ''}`}>3.5. Mapping</div>
        )}
        <div className={`wizard-step-indicator ${registrationStep >= 4 ? 'active' : ''}`}>4. Test</div>
        <div className={`wizard-step-indicator ${registrationStep >= 5 ? 'active' : ''}`}>5. Register</div>
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
                placeholder="http://localhost:8003"
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
                onClick={() => setRegistrationStep(isCustomTemplate() ? 3.5 : 4)}
                disabled={!regForm.endpoint}
              >
                Next →
              </button>
            </div>
          </div>
        )}

        {/* Step 3.5: Advanced Mapping Configuration (Custom Template Only) */}
        {registrationStep === 3.5 && isCustomTemplate() && (
          <div className="wizard-step">
            <h2>⚙️ Advanced Mapping Configuration</h2>
            <p className="step-description">
              Define custom request/response mappings for your REST API. 
              Use JSONPath expressions (e.g., <code>$.description</code>) to map fields.
            </p>
            
            <div className="form-group">
              <label>Request Mapping (JSON)</label>
              <textarea
                className="json-editor"
                value={regForm.custom_request_mapping}
                onChange={(e) => setRegForm({...regForm, custom_request_mapping: e.target.value})}
                placeholder={`{
  "method": "POST",
  "path": "/process",
  "headers": {
    "Content-Type": "application/json"
  },
  "body_mapping": {
    "query": "$.description"
  }
}`}
                rows={12}
              />
              <small>Define how orchestrator requests map to your agent's API format</small>
            </div>

            <div className="form-group">
              <label>Response Mapping (JSON)</label>
              <textarea
                className="json-editor"
                value={regForm.custom_response_mapping}
                onChange={(e) => setRegForm({...regForm, custom_response_mapping: e.target.value})}
                placeholder={`{
  "status_path": "$.status",
  "result_path": "$.result",
  "error_path": "$.error"
}`}
                rows={8}
              />
              <small>Define how to extract results from your agent's responses</small>
            </div>

            <div className="mapping-help">
              <h4>💡 JSONPath Examples:</h4>
              <ul>
                <li><code>$.result</code> - Extract top-level "result" field</li>
                <li><code>$.data.message</code> - Extract nested field</li>
                <li><code>$.choices[0].text</code> - Extract from array</li>
              </ul>
            </div>

            <div className="wizard-actions">
              <button className="btn-back" onClick={() => setRegistrationStep(3)}>
                ← Back
              </button>
              <button 
                className="btn-next"
                onClick={() => setRegistrationStep(4)}
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
                  <p>⏳ Testing connection...</p>
                ) : testResult.success ? (
                  <>
                    <h3>✅ Connection Successful!</h3>
                    <p>Status: {testResult.status_code || 200}</p>
                    {testResult.extracted_result && (
                      <div className="result-preview">
                        <strong>Response:</strong>
                        <pre>{typeof testResult.extracted_result === 'string' ? testResult.extracted_result.substring(0, 200) : JSON.stringify(testResult.extracted_result, null, 2).substring(0, 200)}...</pre>
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
              <button className="btn-back" onClick={() => setRegistrationStep(isCustomTemplate() ? 3.5 : 3)}>
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
                <strong>Capabilities:</strong> {regForm.capabilities.join(', ') || 'None'}
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

  return (
    <div className={`app-container ${isEmbedded ? 'embedded' : ''}`}>
      {/* Embedded Mode Indicator */}
      {isEmbedded && (
        <div className="embedded-indicator">
          Embedded in Adobe Agentic Builder
        </div>
      )}
      
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="brand">
            <svg className="brand-logo" width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="32" height="32" rx="6" fill="#EB1000"/>
              <path d="M16 8L9 24H12.5L14 20.5H18L19.5 24H23L16 8Z" fill="white"/>
              <path d="M16 12L18.5 18.5H13.5L16 12Z" fill="white"/>
            </svg>
            <div className="brand-text">
              <h2>Adobe</h2>
              <span className="brand-subtitle">DPaaS.AI</span>
            </div>
          </div>
          <button className="toggle-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? '←' : '→'}
          </button>
        </div>

        <button className="new-chat-btn" onClick={handleNewChat}>
          <span className="plus-icon">+</span>
          New Chat
        </button>

        {/* Admin Toggle */}
        <div className="power-user-toggle">
          <label className="toggle-label">
            <input 
              type="checkbox" 
              checked={isPowerUser}
              onChange={(e) => setIsPowerUser(e.target.checked)}
            />
            <span className="toggle-slider"></span>
            <span className="toggle-text">
              {isPowerUser ? '🔐 Admin' : '👤 User'}
            </span>
          </label>
        </div>

        <div className="nav-menu">
          <button 
            className={`nav-item ${activeView === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveView('chat')}
          >
            <span className="nav-icon">💬</span>
            Chat
          </button>
          
          <button 
            className={`nav-item ${activeView === 'agents' ? 'active' : ''}`}
            onClick={() => setActiveView('agents')}
          >
            <span className="nav-icon">🤖</span>
            Agent Discovery
          </button>

          <button 
            className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveView('dashboard')}
          >
            <span className="nav-icon">📊</span>
            Agent Observability
          </button>

          {isPowerUser && (
            <>
              <button 
                className={`nav-item ${activeView === 'buildAgents' ? 'active' : ''}`}
                onClick={() => setActiveView('buildAgents')}
              >
                <span className="nav-icon">🔧</span>
                Build Agents
              </button>
              
              <button 
                className={`nav-item ${activeView === 'registerAgent' ? 'active' : ''}`}
                onClick={() => setActiveView('registerAgent')}
              >
                <span className="nav-icon">➕</span>
                Register Agent
              </button>
            </>
          )}
        </div>

        <div className="sidebar-divider"></div>

        <div className="recent-chats">
          <div className="section-header">
            <span>▼</span> Recent Chats
          </div>
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">💬</div>
              <p>No conversations yet</p>
              <small>Start a new conversation to see your chat history here.</small>
            </div>
          ) : (
            <div className="chat-item" onClick={() => setActiveView('chat')}>
              <div className="chat-preview">
                {messages[0]?.content.substring(0, 50)}...
              </div>
            </div>
          )}
        </div>

      </div>

      {/* Main Content */}
      <div className="main-content">
        {activeView === 'chat' && renderChatView()}
        {activeView === 'buildAgents' && renderBuildAgentsView()}
        {activeView === 'registerAgent' && renderRegisterAgentView()}
        {activeView === 'dashboard' && renderDashboardView()}
        {activeView === 'agents' && renderAgentsView()}

        {/* Input Area - Only show for chat view */}
        {activeView === 'chat' && (
          <div className="input-container">
            <div className="input-wrapper">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask me anything about your data..."
                disabled={loading}
              />
              <button 
                className="send-btn"
                onClick={handleSendMessage}
                disabled={loading || !inputMessage.trim()}
              >
                <span className="send-icon">➤</span>
              </button>
            </div>
            <div className="input-footer">
              Powered by Adobe DPaaS.AI - Multi-Agent Orchestrator with LangGraph & A2A Protocol
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
