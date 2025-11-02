# Contributing to Multi-Agent Orchestrator

Thank you for your interest in contributing to the Multi-Agent Orchestrator! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

## 🤝 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

### Our Standards

- **Be respectful**: Treat everyone with respect and kindness
- **Be collaborative**: Work together towards common goals
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Remember that everyone has different skill levels

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** for backend development
- **Node.js 16+** for frontend development
- **Git** for version control
- **Code editor** (VS Code, PyCharm, etc.)

### Setting Up Development Environment

1. **Fork the repository**
```bash
# Go to https://github.com/SharadNarang/Multi-Agent-Orchestror
# Click "Fork" button
```

2. **Clone your fork**
```bash
git clone https://github.com/YOUR_USERNAME/Multi-Agent-Orchestror.git
cd Multi-Agent-Orchestror
```

3. **Add upstream remote**
```bash
git remote add upstream https://github.com/SharadNarang/Multi-Agent-Orchestror.git
```

4. **Set up backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

5. **Set up frontend**
```bash
cd frontend
npm install
```

6. **Run tests**
```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

## 💡 How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Reports**: Report bugs through GitHub issues
2. **Feature Requests**: Suggest new features or enhancements
3. **Code Contributions**: Submit bug fixes or new features
4. **Documentation**: Improve or add documentation
5. **Testing**: Write tests or improve test coverage
6. **Reviews**: Review pull requests from other contributors

### Finding Issues to Work On

- Check the [Issues](https://github.com/SharadNarang/Multi-Agent-Orchestror/issues) page
- Look for labels like `good first issue` or `help wanted`
- Comment on an issue to let others know you're working on it

## 🔄 Development Workflow

### 1. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/add-authentication`)
- `fix/` - Bug fixes (e.g., `fix/task-execution-error`)
- `docs/` - Documentation updates (e.g., `docs/update-api-guide`)
- `refactor/` - Code refactoring (e.g., `refactor/agent-registry`)
- `test/` - Test additions/updates (e.g., `test/task-planner`)

### 2. Make Changes

- Write clean, maintainable code
- Follow coding standards (see below)
- Add tests for new features
- Update documentation as needed

### 3. Commit Changes

```bash
git add .
git commit -m "descriptive commit message"
```

#### Commit Message Convention

Use clear, descriptive commit messages following this format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build/tooling changes

**Examples:**
```bash
feat(agent): add new agent registration endpoint

fix(task-executor): resolve task execution timeout issue

docs(readme): update installation instructions

test(orchestrator): add unit tests for task planner
```

### 4. Push Changes

```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the PR template
5. Submit the pull request

## 📝 Coding Standards

### Python (Backend)

#### Style Guide

Follow [PEP 8](https://pep8.org/) style guide:

```python
# Good
def calculate_task_priority(task: Task, agent: Agent) -> int:
    """Calculate task priority based on agent capabilities.
    
    Args:
        task: Task object to prioritize
        agent: Agent object with capabilities
        
    Returns:
        Priority score (higher is more urgent)
    """
    priority = 0
    for capability in task.required_capabilities:
        if capability in agent.capabilities:
            priority += 1
    return priority


# Bad
def calc_priority(t,a):
    p=0
    for c in t.req_cap:
        if c in a.cap:
            p+=1
    return p
```

#### Type Hints

Always use type hints:

```python
from typing import List, Dict, Optional

def process_task(
    task_id: int,
    agents: List[Agent],
    config: Optional[Dict[str, Any]] = None
) -> TaskResult:
    ...
```

#### Docstrings

Use Google-style docstrings:

```python
def register_agent(name: str, capabilities: List[str]) -> Agent:
    """Register a new agent with the orchestrator.
    
    Args:
        name: Unique name for the agent
        capabilities: List of agent capabilities
        
    Returns:
        Registered Agent object
        
    Raises:
        ValueError: If agent name already exists
        
    Example:
        >>> agent = register_agent("ResearchBot", ["research", "analysis"])
        >>> print(agent.id)
        1
    """
    ...
```

#### Imports

Organize imports in this order:

```python
# Standard library
import os
import sys
from typing import List, Dict

# Third-party
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Local imports
from models.agent import Agent
from services.registry import AgentRegistry
```

### JavaScript/React (Frontend)

#### Style Guide

Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript):

```javascript
// Good
const TaskCard = ({ task, onUpdate }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleUpdate = async () => {
    setIsLoading(true);
    try {
      await onUpdate(task.id);
    } catch (error) {
      console.error('Failed to update task:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="task-card">
      <h3>{task.description}</h3>
      <button onClick={handleUpdate} disabled={isLoading}>
        Update
      </button>
    </div>
  );
};

// Bad
function TaskCard(props) {
  var loading = false;
  
  function update() {
    loading = true;
    props.onUpdate(props.task.id).then(() => {
      loading = false;
    });
  }
  
  return <div><h3>{props.task.description}</h3></div>;
}
```

#### Component Structure

```javascript
import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './TaskCard.css';

/**
 * TaskCard component displays task information
 * @param {Object} task - Task object with details
 * @param {Function} onUpdate - Callback when task is updated
 */
const TaskCard = ({ task, onUpdate }) => {
  // Component logic here
};

TaskCard.propTypes = {
  task: PropTypes.shape({
    id: PropTypes.number.isRequired,
    description: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
  }).isRequired,
  onUpdate: PropTypes.func.isRequired,
};

export default TaskCard;
```

## 🧪 Testing Guidelines

### Backend Testing

Use pytest for backend tests:

```python
# tests/test_task_planner.py
import pytest
from orchestrator.task_planner import TaskPlanner

@pytest.fixture
def task_planner(db_session):
    """Create a TaskPlanner instance for testing."""
    return TaskPlanner(db_session)

def test_create_execution_plan(task_planner):
    """Test task execution plan creation."""
    task = task_planner.create_execution_plan(
        task_description="Test task",
        session_id="test-session"
    )
    
    assert task is not None
    assert task.status == "planning"
    assert len(task.plan["steps"]) > 0

def test_invalid_task_description(task_planner):
    """Test handling of invalid task description."""
    with pytest.raises(ValueError):
        task_planner.create_execution_plan(
            task_description="",
            session_id="test-session"
        )
```

### Frontend Testing

Use React Testing Library:

```javascript
// src/components/TaskCard.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import TaskCard from './TaskCard';

describe('TaskCard', () => {
  const mockTask = {
    id: 1,
    description: 'Test task',
    status: 'pending',
  };
  
  test('renders task information', () => {
    render(<TaskCard task={mockTask} onUpdate={() => {}} />);
    
    expect(screen.getByText('Test task')).toBeInTheDocument();
    expect(screen.getByText('pending')).toBeInTheDocument();
  });
  
  test('calls onUpdate when button is clicked', () => {
    const handleUpdate = jest.fn();
    render(<TaskCard task={mockTask} onUpdate={handleUpdate} />);
    
    fireEvent.click(screen.getByText('Update'));
    expect(handleUpdate).toHaveBeenCalledWith(1);
  });
});
```

### Test Coverage

- Aim for at least 80% code coverage
- Write tests for:
  - Core business logic
  - API endpoints
  - Component rendering
  - Error handling
  - Edge cases

## 📚 Documentation

### Code Documentation

- Document all public APIs
- Include examples in docstrings
- Explain complex algorithms
- Add inline comments for tricky code

### README Updates

Update relevant README files when:
- Adding new features
- Changing APIs
- Modifying setup/installation
- Adding new dependencies

### API Documentation

Update `API_GUIDE.md` for:
- New endpoints
- Changed request/response formats
- New query parameters
- Authentication changes

## 🔍 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated Checks**: CI/CD runs tests and linters
2. **Code Review**: Maintainers review code
3. **Feedback**: Address review comments
4. **Approval**: At least one approval required
5. **Merge**: Maintainer merges the PR

## 🐛 Issue Guidelines

### Bug Reports

Include:
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Numbered steps to reproduce
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python/Node version, etc.
- **Screenshots**: If applicable

**Template:**
```markdown
**Bug Description**
A clear description of the bug

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen

**Environment**
- OS: Windows 10
- Python: 3.9.7
- Node: 16.14.0
```

### Feature Requests

Include:
- **Problem**: What problem does this solve?
- **Solution**: Proposed solution
- **Alternatives**: Alternative solutions considered
- **Additional Context**: Any other context

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create an issue
- **Security**: Email maintainers directly

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Thank you for contributing to Multi-Agent Orchestrator! Your efforts help make this project better for everyone.

