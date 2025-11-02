# Multi-Agent Orchestrator - Frontend

React-based frontend application for the Multi-Agent Orchestrator system, built with Vite and modern React practices.

## 🚀 Features

- **Modern React**: Built with React 18+ and hooks
- **Vite**: Fast development server and build tool
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live task status updates
- **Agent Management**: View and manage registered agents
- **Task Execution**: Create and monitor tasks
- **Session Management**: Conversation history and context

## 📦 Tech Stack

- **React 18.2.0** - UI library
- **Vite 5.0.7** - Build tool and dev server
- **Axios 1.6.2** - HTTP client for API calls
- **CSS3** - Styling

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── App.jsx          # Main application component
│   ├── App.css          # Application styles
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration
└── README.md           # This file
```

## 🚀 Getting Started

### Prerequisites

- Node.js 16 or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The application will be available at http://localhost:3000

### Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## ⚙️ Configuration

### Vite Configuration (`vite.config.js`)

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_A2A_SERVER_URL=http://localhost:8001
VITE_API_AGENT_URL=http://localhost:8002
```

Access in code:
```javascript
const apiUrl = import.meta.env.VITE_API_BASE_URL
```

## 🎨 UI Components

### Main App Component

The main application component handles:
- Task creation and management
- Agent listing and status
- Session management
- Real-time updates

### Key Features

1. **Task Creation**
   - Input task description
   - Select user ID
   - Submit and track execution

2. **Task Monitoring**
   - View task status
   - See execution steps
   - Display results

3. **Agent Management**
   - List registered agents
   - View agent capabilities
   - Check agent health status

4. **Session History**
   - View conversation context
   - Browse message history
   - Track session metadata

## 🔌 API Integration

### API Client Setup

```javascript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Create task
const createTask = async (description, userId) => {
  const response = await apiClient.post('/api/tasks', {
    description,
    user_id: userId,
  })
  return response.data
}

// Get task status
const getTaskStatus = async (taskId) => {
  const response = await apiClient.get(`/api/tasks/${taskId}`)
  return response.data
}

// List agents
const listAgents = async () => {
  const response = await apiClient.get('/api/agents')
  return response.data
}
```

### Example Usage

```javascript
// In a React component
import { useState, useEffect } from 'react'
import axios from 'axios'

function TaskManager() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(false)

  const createTask = async (description) => {
    setLoading(true)
    try {
      const response = await axios.post('http://localhost:8000/api/tasks', {
        description,
        user_id: 'user123'
      })
      
      setTasks([...tasks, response.data])
    } catch (error) {
      console.error('Error creating task:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <button onClick={() => createTask('Analyze data')}>
        Create Task
      </button>
      {tasks.map(task => (
        <div key={task.task_id}>
          Task {task.task_id}: {task.status}
        </div>
      ))}
    </div>
  )
}
```

## 🎨 Styling

The application uses CSS modules and modern CSS features:

- **Flexbox** for layout
- **Grid** for complex layouts
- **CSS Variables** for theming
- **Responsive Design** with media queries

### Example Styles

```css
/* App.css */
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.task-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.task-status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.task-status.completed {
  background: var(--success-color);
  color: white;
}

.task-status.pending {
  background: var(--secondary-color);
  color: white;
}
```

## 🧪 Testing

### Running Tests

```bash
# Run tests (when implemented)
npm test

# Run tests with coverage
npm run test:coverage
```

### Example Test

```javascript
import { render, screen, fireEvent } from '@testing-library/react'
import App from './App'

test('renders task creation form', () => {
  render(<App />)
  const buttonElement = screen.getByText(/Create Task/i)
  expect(buttonElement).toBeInTheDocument()
})

test('creates a task when button is clicked', async () => {
  render(<App />)
  const input = screen.getByPlaceholderText(/Task description/i)
  const button = screen.getByText(/Create Task/i)
  
  fireEvent.change(input, { target: { value: 'Test task' } })
  fireEvent.click(button)
  
  // Assert task is created
  const taskElement = await screen.findByText(/Test task/i)
  expect(taskElement).toBeInTheDocument()
})
```

## 📱 Responsive Design

The application is responsive and works on various screen sizes:

- **Desktop**: Full-width layout with sidebars
- **Tablet**: Stacked layout with collapsible sidebars
- **Mobile**: Single column layout with hamburger menu

### Media Queries

```css
/* Mobile */
@media (max-width: 768px) {
  .container {
    padding: 10px;
  }
  
  .task-card {
    padding: 15px;
  }
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
  .container {
    max-width: 900px;
  }
}

/* Desktop */
@media (min-width: 1025px) {
  .container {
    max-width: 1200px;
  }
}
```

## 🔧 Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR. Changes to React components will reflect immediately without losing state.

### Import Aliases

Configure path aliases in `vite.config.js`:

```javascript
export default defineConfig({
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@utils': '/src/utils',
    },
  },
})
```

Usage:
```javascript
import MyComponent from '@components/MyComponent'
```

### Code Splitting

Use dynamic imports for code splitting:

```javascript
import { lazy, Suspense } from 'react'

const TaskManager = lazy(() => import('./components/TaskManager'))

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <TaskManager />
    </Suspense>
  )
}
```

## 🐛 Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Kill process on port 3000 (Windows)
netstat -ano | findstr :3000
taskkill /PID <process_id> /F

# Change port in vite.config.js
server: {
  port: 3001
}
```

**2. API connection errors**
- Verify backend is running on http://localhost:8000
- Check CORS configuration in backend
- Verify proxy settings in vite.config.js

**3. Module not found errors**
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

**4. Build errors**
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

## 📦 Build and Deployment

### Production Build

```bash
# Create optimized build
npm run build

# Output will be in dist/ directory
```

### Deployment Options

**1. Static Hosting (Netlify, Vercel)**
```bash
# Build command
npm run build

# Publish directory
dist
```

**2. Docker**
```dockerfile
FROM node:16 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**3. GitHub Pages**
```bash
# Install gh-pages
npm install --save-dev gh-pages

# Add to package.json scripts
"deploy": "npm run build && gh-pages -d dist"

# Deploy
npm run deploy
```

## 🚀 Performance Optimization

### Code Splitting
```javascript
// Use React.lazy for route-based code splitting
const Home = lazy(() => import('./pages/Home'))
const Tasks = lazy(() => import('./pages/Tasks'))
```

### Image Optimization
```javascript
// Use responsive images
<img 
  src="image.jpg"
  srcSet="image-320w.jpg 320w, image-640w.jpg 640w"
  sizes="(max-width: 600px) 320px, 640px"
  alt="Description"
/>
```

### Caching
```javascript
// Use React Query for data caching
import { useQuery } from 'react-query'

const { data, isLoading } = useQuery('tasks', fetchTasks, {
  staleTime: 5 * 60 * 1000, // 5 minutes
})
```

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - See LICENSE file for details.

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Axios Documentation](https://axios-http.com/)
- [MDN Web Docs](https://developer.mozilla.org/)

