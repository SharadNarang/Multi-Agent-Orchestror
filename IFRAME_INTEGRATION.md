# iFrame Integration Guide

## Multi-Agent Orchestrator → Adobe Agentic Builder

This guide explains how to embed the Multi-Agent Orchestrator frontend into the Adobe Agentic Builder platform using iFrame technology.

---

## 🎯 Overview

The Multi-Agent Orchestrator is now configured to be embedded as an iFrame in the Adobe Agentic Builder platform. This integration provides seamless access to AI agent orchestration capabilities directly within the Agentic Builder interface.

### Key Features
- ✅ **Secure Cross-Origin Communication** - CORS configured for Adobe domains
- ✅ **PostMessage API** - Bi-directional communication between parent and child
- ✅ **Auto-Detection** - Automatically detects when running in an iFrame
- ✅ **Responsive Design** - Adapts UI for embedded mode
- ✅ **Security Headers** - CSP and X-Frame-Options configured

---

## 🔧 Backend Configuration

### 1. **CORS Settings** (`backend/config.py`)

```python
# iFrame Embedding Support
adobe_agentic_builder_url: str = "https://agentic-builder-dev.corp.adobe.com"
allow_iframe_embedding: bool = True
```

**Environment Variables:**
- `ADOBE_AGENTIC_BUILDER_URL` - Adobe Agentic Builder base URL
- `ALLOW_IFRAME_EMBEDDING` - Enable/disable iFrame embedding (default: true)

### 2. **Security Headers** (`backend/main.py`)

The backend automatically adds these security headers:

**When embedding is enabled:**
```
X-Frame-Options: ALLOW-FROM https://agentic-builder-dev.corp.adobe.com
Content-Security-Policy: frame-ancestors 'self' https://agentic-builder-dev.corp.adobe.com http://localhost:3000;
```

**When embedding is disabled:**
```
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none';
```

### 3. **CORS Configuration**

Allowed origins:
- `http://localhost:3000` (Frontend development)
- `https://agentic-builder-dev.corp.adobe.com` (Adobe Agentic Builder)

---

## 🎨 Frontend Integration

### 1. **iFrame Detection**

The frontend automatically detects if it's running in an iFrame:

```javascript
const inIframe = window.self !== window.top
```

When embedded:
- Shows visual indicator: **"🖼️ Embedded in Adobe Agentic Builder"**
- Collapses sidebar by default
- Enables PostMessage communication

### 2. **PostMessage API**

#### **Messages FROM Orchestrator → Parent**

| Message Type | Description | Data |
|--------------|-------------|------|
| `ORCHESTRATOR_READY` | Sent when orchestrator is loaded | `{ status: 'ready' }` |
| `TASK_STATUS_UPDATE` | Sent when tasks/agents change | `{ taskCount: number, activeAgents: number }` |
| `TASK_COMPLETED` | Sent when a task finishes | `{ taskId: string, result: object }` |

**Example (Parent Listening):**
```javascript
window.addEventListener('message', (event) => {
  if (event.origin !== 'http://localhost:3000') return;
  
  const { type, data } = event.data;
  
  switch (type) {
    case 'ORCHESTRATOR_READY':
      console.log('✅ Orchestrator is ready');
      break;
    case 'TASK_STATUS_UPDATE':
      console.log(`📊 Active tasks: ${data.taskCount}, Agents: ${data.activeAgents}`);
      break;
  }
});
```

#### **Messages TO Orchestrator ← Parent**

| Message Type | Description | Data |
|--------------|-------------|------|
| `EXECUTE_TASK` | Execute a task | `{ query: string, autoSubmit?: boolean }` |
| `SET_VIEW` | Change active view | `{ view: 'chat' \| 'dashboard' \| 'agents' \| 'buildAgents' }` |
| `TOGGLE_SIDEBAR` | Toggle sidebar visibility | `{}` |

**Example (Parent Sending):**
```javascript
const iframe = document.getElementById('orchestrator-iframe');

// Execute a task
iframe.contentWindow.postMessage({
  type: 'EXECUTE_TASK',
  data: {
    query: 'Research the benefits of AI in healthcare',
    autoSubmit: true
  }
}, '*');

// Switch to dashboard view
iframe.contentWindow.postMessage({
  type: 'SET_VIEW',
  data: { view: 'dashboard' }
}, '*');
```

---

## 🚀 Integration Steps

### **Step 1: Deploy Backend**

Ensure the backend is accessible from the Adobe network:

```bash
# Start backend services
cd backend
python main.py  # Port 8000
python a2a_server.py  # Port 8001
python api_agent_server.py  # Port 8002
```

### **Step 2: Deploy Frontend**

Build and deploy the frontend:

```bash
cd frontend
npm run build

# Serve the built files
# Deploy to: https://your-domain.corp.adobe.com
```

### **Step 3: Embed in Adobe Agentic Builder**

Add the iFrame to your Agentic Builder page:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Multi-Agent Orchestrator</title>
  <style>
    #orchestrator-iframe {
      width: 100%;
      height: 100vh;
      border: none;
      border-radius: 8px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <iframe 
    id="orchestrator-iframe"
    src="https://your-domain.corp.adobe.com"
    allow="clipboard-write; clipboard-read"
    sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
  ></iframe>

  <script>
    // Listen for orchestrator messages
    window.addEventListener('message', (event) => {
      console.log('Received from orchestrator:', event.data);
    });

    // Wait for ready signal
    window.addEventListener('message', (event) => {
      if (event.data.type === 'ORCHESTRATOR_READY') {
        console.log('✅ Orchestrator loaded successfully');
        
        // Send initial task
        document.getElementById('orchestrator-iframe')
          .contentWindow.postMessage({
            type: 'EXECUTE_TASK',
            data: {
              query: 'What are the latest AI trends?',
              autoSubmit: false
            }
          }, '*');
      }
    });
  </script>
</body>
</html>
```

---

## 🔒 Security Considerations

### 1. **Origin Validation**

**Production:** Uncomment origin validation in `frontend/src/App.jsx`:

```javascript
// Validate origin for production
if (event.origin !== 'https://agentic-builder-dev.corp.adobe.com') return;
```

### 2. **Authentication**

For production, add authentication:

```javascript
// Add JWT token to requests
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

### 3. **Content Security Policy**

Update CSP headers to restrict:
- Script sources
- Style sources
- Frame ancestors
- Connection sources

### 4. **Sandbox Attributes**

Use restrictive sandbox attributes:

```html
<iframe 
  sandbox="allow-scripts allow-same-origin allow-forms"
  src="https://orchestrator.corp.adobe.com"
></iframe>
```

**Recommended sandbox flags:**
- `allow-scripts` - Required for React app
- `allow-same-origin` - Required for API calls
- `allow-forms` - Required for user input
- `allow-popups` (optional) - If opening new windows

---

## 🎛️ Configuration Options

### Environment Variables

Create `.env` file:

```bash
# Backend
DATABASE_URL=sqlite:///./agent_orchestrator.db
GROQ_API_KEY=your-groq-api-key
A2A_SERVER_URL=http://localhost:8001
BACKEND_API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ADOBE_AGENTIC_BUILDER_URL=https://agentic-builder-dev.corp.adobe.com
ALLOW_IFRAME_EMBEDDING=true
```

### Disable iFrame Embedding

Set in `.env`:
```bash
ALLOW_IFRAME_EMBEDDING=false
```

This will:
- Set `X-Frame-Options: DENY`
- Set `Content-Security-Policy: frame-ancestors 'none'`
- Prevent embedding in any domain

---

## 📊 Testing

### **Local Testing**

1. **Create test HTML file** (`test-iframe.html`):

```html
<!DOCTYPE html>
<html>
<head>
  <title>Orchestrator iFrame Test</title>
  <style>
    body { margin: 0; padding: 20px; font-family: sans-serif; }
    iframe { width: 100%; height: 800px; border: 1px solid #ccc; }
    .controls { margin-bottom: 20px; }
    button { padding: 10px 20px; margin: 5px; }
  </style>
</head>
<body>
  <h1>Multi-Agent Orchestrator - iFrame Test</h1>
  
  <div class="controls">
    <button onclick="sendTask()">Send Task</button>
    <button onclick="toggleSidebar()">Toggle Sidebar</button>
    <button onclick="switchToDashboard()">Dashboard</button>
  </div>
  
  <iframe id="orchestrator" src="http://localhost:3000"></iframe>
  
  <script>
    const iframe = document.getElementById('orchestrator');
    
    function sendTask() {
      iframe.contentWindow.postMessage({
        type: 'EXECUTE_TASK',
        data: {
          query: 'What is artificial intelligence?',
          autoSubmit: true
        }
      }, '*');
    }
    
    function toggleSidebar() {
      iframe.contentWindow.postMessage({
        type: 'TOGGLE_SIDEBAR',
        data: {}
      }, '*');
    }
    
    function switchToDashboard() {
      iframe.contentWindow.postMessage({
        type: 'SET_VIEW',
        data: { view: 'dashboard' }
      }, '*');
    }
    
    window.addEventListener('message', (event) => {
      console.log('📨 Received:', event.data);
    });
  </script>
</body>
</html>
```

2. **Open in browser:**
```bash
# Serve the test file
python -m http.server 8080
# Open http://localhost:8080/test-iframe.html
```

### **Verify CORS Headers**

```bash
curl -I http://localhost:8000/health
# Should show:
# access-control-allow-origin: https://agentic-builder-dev.corp.adobe.com
# content-security-policy: frame-ancestors ...
```

---

## 🐛 Troubleshooting

### Issue: "Refused to display in a frame"

**Cause:** CSP or X-Frame-Options blocking

**Solution:**
1. Check `ALLOW_IFRAME_EMBEDDING=true` in `.env`
2. Verify parent domain matches `ADOBE_AGENTIC_BUILDER_URL`
3. Check browser console for CSP errors

### Issue: "Cross-origin blocked"

**Cause:** CORS not configured properly

**Solution:**
1. Verify backend CORS settings
2. Check `allowed_origins` in `main.py`
3. Ensure parent domain is in allowed origins

### Issue: "PostMessage not received"

**Cause:** Origin validation or incorrect target

**Solution:**
1. Check `event.origin` validation
2. Use `'*'` for testing (not production!)
3. Verify iframe is fully loaded before sending messages

### Issue: "Styling looks broken"

**Cause:** CSS not loading or embedded mode not detected

**Solution:**
1. Check `isEmbedded` state in browser console
2. Verify `.embedded` class is applied
3. Check browser dev tools for CSS errors

---

## 🔄 Deployment Checklist

- [ ] Backend deployed and accessible from Adobe network
- [ ] Frontend built and deployed
- [ ] `.env` file configured with correct URLs
- [ ] CORS headers verified
- [ ] CSP headers verified
- [ ] Origin validation uncommented (production)
- [ ] Authentication added (if required)
- [ ] SSL certificates configured
- [ ] Test iFrame embedding from Agentic Builder
- [ ] Verify PostMessage communication
- [ ] Test all user flows in embedded mode
- [ ] Monitor logs for errors

---

## 📚 Additional Resources

- [PostMessage API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [Content Security Policy Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [iFrame Sandbox Attributes](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#attr-sandbox)

---

## 🆘 Support

For issues or questions:
1. Check this documentation
2. Review browser console for errors
3. Check backend logs
4. Contact the development team

---

## 📝 Changelog

### Version 1.0.0 (Current)
- Initial iFrame embedding support
- PostMessage API implementation
- Auto-detection and responsive design
- Security headers configured
- Adobe Agentic Builder integration

---

**Last Updated:** November 2025  
**Maintainer:** Adobe DPaaS.AI Team

