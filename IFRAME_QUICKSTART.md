# 🚀 iFrame Integration - Quick Start

## ✅ What's Been Implemented

Your Multi-Agent Orchestrator can now be embedded in the Adobe Agentic Builder using iFrame technology!

### Changes Made:

#### **Backend** (`backend/`)
- ✅ CORS configured for `https://agentic-builder-dev.corp.adobe.com`
- ✅ Security headers (CSP, X-Frame-Options) added
- ✅ Configurable embedding settings
- ✅ Cross-origin communication enabled

#### **Frontend** (`frontend/src/`)
- ✅ Auto-detection of iFrame mode
- ✅ PostMessage API for parent-child communication
- ✅ Visual indicator when embedded
- ✅ Responsive design for embedded mode
- ✅ Remote task execution support

#### **Documentation**
- ✅ Comprehensive integration guide ([IFRAME_INTEGRATION.md](IFRAME_INTEGRATION.md))
- ✅ Test HTML file ([test-iframe.html](test-iframe.html))
- ✅ README updated with reference

---

## 🧪 Quick Test (2 minutes)

### **Step 1: Start Your Services**

```powershell
# Terminal 1 - Backend
cd C:\Users\shnarang\multi-agent-orchestrator\backend
.\venv\Scripts\activate
python main.py

# Terminal 2 - A2A Server
cd C:\Users\shnarang\multi-agent-orchestrator\backend
.\venv\Scripts\activate
python a2a_server.py

# Terminal 3 - API Agent
cd C:\Users\shnarang\multi-agent-orchestrator\backend
.\venv\Scripts\activate
python api_agent_server.py

# Terminal 4 - Frontend
cd C:\Users\shnarang\multi-agent-orchestrator\frontend
npm run dev
```

### **Step 2: Open Test Page**

1. Open `test-iframe.html` in your browser:
   ```
   File > Open > C:\Users\shnarang\multi-agent-orchestrator\test-iframe.html
   ```

2. You should see:
   - ✅ "🖼️ Embedded in Adobe Agentic Builder" indicator at top-right
   - ✅ Interactive controls above the iframe
   - ✅ Message logs at the bottom
   - ✅ The orchestrator running inside the iframe

### **Step 3: Test Communication**

Click these buttons to test:
- **🔢 Simple Query (1+1)** - Tests simple task execution
- **🔬 Research Task** - Tests complex research workflow
- **📐 Toggle Sidebar** - Tests UI control
- **📊 Dashboard View** - Tests view switching

Watch the **Message Logs** at the bottom to see:
- 📤 **Outgoing**: Messages sent to orchestrator
- 📨 **Incoming**: Responses from orchestrator

---

## 🔧 Configuration

### Environment Variables

Create/update `.env` in `backend/`:

```bash
# Required
GROQ_API_KEY=your-groq-api-key-here

# iFrame Settings (already configured)
ADOBE_AGENTIC_BUILDER_URL=https://agentic-builder-dev.corp.adobe.com
ALLOW_IFRAME_EMBEDDING=true
FRONTEND_URL=http://localhost:3000
```

### Disable iFrame Embedding

To disable embedding (for security):

```bash
# In .env
ALLOW_IFRAME_EMBEDDING=false
```

---

## 📡 PostMessage API

### **Parent → Orchestrator (Send Commands)**

```javascript
const iframe = document.getElementById('orchestrator-iframe');

// Execute a task
iframe.contentWindow.postMessage({
  type: 'EXECUTE_TASK',
  data: {
    query: 'What is artificial intelligence?',
    autoSubmit: true  // Auto-submit the query
  }
}, '*');

// Switch view
iframe.contentWindow.postMessage({
  type: 'SET_VIEW',
  data: { view: 'dashboard' }  // 'chat', 'dashboard', 'agents', 'buildAgents'
}, '*');

// Toggle sidebar
iframe.contentWindow.postMessage({
  type: 'TOGGLE_SIDEBAR',
  data: {}
}, '*');
```

### **Orchestrator → Parent (Listen for Updates)**

```javascript
window.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'ORCHESTRATOR_READY':
      console.log('✅ Orchestrator loaded');
      break;
      
    case 'TASK_STATUS_UPDATE':
      console.log(`Tasks: ${data.taskCount}, Agents: ${data.activeAgents}`);
      break;
      
    case 'TASK_COMPLETED':
      console.log(`Task ${data.taskId} completed!`);
      break;
  }
});
```

---

## 🎯 Integration in Adobe Agentic Builder

### Basic Embedding

```html
<!-- Add to your Agentic Builder page -->
<iframe 
  id="orchestrator"
  src="https://your-domain.corp.adobe.com"
  style="width: 100%; height: 800px; border: none;"
  allow="clipboard-write; clipboard-read"
  sandbox="allow-scripts allow-same-origin allow-forms"
></iframe>

<script>
  // Listen for ready signal
  window.addEventListener('message', (event) => {
    if (event.data.type === 'ORCHESTRATOR_READY') {
      console.log('✅ Orchestrator ready!');
      
      // Send initial task
      document.getElementById('orchestrator')
        .contentWindow.postMessage({
          type: 'EXECUTE_TASK',
          data: { query: 'Hello from Agentic Builder!', autoSubmit: true }
        }, '*');
    }
  });
</script>
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] **Uncomment origin validation** in `frontend/src/App.jsx`:
  ```javascript
  // Line 36-37
  if (event.origin !== 'https://agentic-builder-dev.corp.adobe.com') return;
  ```

- [ ] **Use HTTPS** for all deployments
- [ ] **Configure proper CSP** headers
- [ ] **Add authentication** if required
- [ ] **Test from actual Adobe Agentic Builder** domain
- [ ] **Monitor logs** for security issues

---

## 📊 Expected Behavior

### **When Standalone** (http://localhost:3000)
- Full sidebar visible
- No embedded indicator
- Normal operation

### **When Embedded** (in iFrame)
- "🖼️ Embedded in Adobe Agentic Builder" indicator
- Sidebar collapsed by default
- PostMessage communication active
- Responsive to parent commands

---

## 🐛 Troubleshooting

### Issue: "Refused to display in a frame"

**Solution:**
```bash
# Check backend logs for CSP errors
# Verify ALLOW_IFRAME_EMBEDDING=true in .env
# Restart backend after changes
```

### Issue: "Cross-origin blocked"

**Solution:**
```bash
# Check CORS headers in browser console
# Verify backend/main.py has correct allowed_origins
# Ensure parent domain matches ADOBE_AGENTIC_BUILDER_URL
```

### Issue: No communication between parent and iframe

**Solution:**
```javascript
// Check browser console for errors
// Verify iframe is fully loaded before sending messages
// Use '*' origin for testing (not production!)
```

---

## 📚 Full Documentation

For complete details, see:
- **[IFRAME_INTEGRATION.md](IFRAME_INTEGRATION.md)** - Complete integration guide
- **[SERVICE_FLOW.md](SERVICE_FLOW.md)** - Architecture diagrams
- **[API_GUIDE.md](API_GUIDE.md)** - API reference

---

## ✨ Next Steps

1. **Test locally** with `test-iframe.html`
2. **Deploy to Adobe network** (if not already)
3. **Integrate with Agentic Builder**
4. **Monitor and optimize**

---

## 🆘 Support

Questions or issues?
1. Check the [full integration guide](IFRAME_INTEGRATION.md)
2. Review browser console logs
3. Check backend service logs
4. Open an issue on GitHub

---

**Happy Embedding! 🎉**

*Last Updated: November 2025*

