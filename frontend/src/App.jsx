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
  const [activeView, setActiveView] = useState('chat') // chat, dashboard, agents
  const [agentStats, setAgentStats] = useState(null)
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    fetchAgents()
    createSession()
    fetchAgentStats()
  }, [])

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

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    }

    setMessages([...messages, userMessage])
    setInputMessage('')
    setLoading(true)

    try {
      const taskResponse = await axios.post(`${API_BASE}/api/tasks`, {
        description: inputMessage,
        user_id: 'demo-user',
        session_id: sessionId
      })

      setTasks(prev => [taskResponse.data, ...prev])

      const aiMessage = {
        role: 'assistant',
        content: `✅ Task created successfully!\n\n🎯 Task ID: ${taskResponse.data.task_id}\n📊 Status: ${taskResponse.data.status}\n\nI'm coordinating multiple AI agents to handle: "${inputMessage}"\n\nAgents involved:\n${taskResponse.data.plan?.steps?.map((s, i) => `${i + 1}. ${s.agent_name || 'Agent'}: ${s.description}`).join('\n') || 'Planning in progress...'}`,
        timestamp: new Date().toISOString(),
        taskId: taskResponse.data.task_id
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error. Please ensure:\n• Backend services are running\n• Groq API key is configured\n• All agents are active',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
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
              <span>🤖</span> VIEW AGENTS
            </button>
            <button className="action-btn" onClick={() => setActiveView('dashboard')}>
              <span>📊</span> DASHBOARD
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
        <h1>📊 System Dashboard</h1>
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

  return (
    <div className="app-container">
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

        <div className="nav-menu">
          <button 
            className={`nav-item ${activeView === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveView('chat')}
          >
            <span className="nav-icon">💬</span>
            Chat
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

        <div className="sidebar-footer">
          <div className="agent-status">
            <h4>Active Agents: {agents.filter(a => a.status === 'active').length}</h4>
            {agents.slice(0, 2).map(agent => (
              <div key={agent.id} className="agent-item">
                <span className="status-dot"></span>
                {agent.name}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {activeView === 'chat' && renderChatView()}
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
