# Contributing to AI-Powered Presales Assistant

Thank you for your interest in contributing to the AI-Powered Presales Assistant! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information**:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, Node.js version)
   - Screenshots if applicable

### Suggesting Features

1. **Open an issue** with the "feature request" label
2. **Describe the use case** and business value
3. **Provide mockups or examples** if applicable
4. **Consider backwards compatibility** and breaking changes

## 🛠 Development Setup

### Prerequisites

- Python 3.11+
- Node.js 16+
- Git
- OpenAI API Key

### Local Development

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/presales_assistant.git
cd presales_assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up frontend
cd presales-assistant-ui
npm install

# Create environment file
copy .env.example .env
# Add your OpenAI API key to .env
```

## 🔄 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

### 2. Make Changes

- **Follow code style** guidelines (see below)
- **Write tests** for new functionality
- **Update documentation** as needed
- **Keep commits atomic** and well-described

### 3. Test Your Changes

```bash
# Run backend tests
python -m pytest

# Run frontend tests
cd presales-assistant-ui
npm test

# Test the full application
python ff.py  # Terminal 1
npm start     # Terminal 2 (in presales-assistant-ui/)
```

### 4. Commit Guidelines

Use conventional commit messages:

```bash
feat: add new search engine integration
fix: resolve Unicode encoding issue on Windows
docs: update installation instructions
refactor: improve portfolio matching algorithm
test: add tests for intelligence extraction
```

### 5. Submit Pull Request

1. **Push your branch** to your fork
2. **Create a pull request** against the main branch
3. **Fill out the PR template** completely
4. **Link related issues** using keywords (fixes #123)

## 📋 Code Style Guidelines

### Python (Backend)

- **Follow PEP 8** style guidelines
- **Use type hints** where possible
- **Document functions** with docstrings
- **Keep functions focused** and single-purpose
- **Use meaningful variable names**

```python
def extract_business_intelligence(
    search_results: List[Dict[str, Any]], 
    confidence_threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Extract structured business intelligence from search results.
    
    Args:
        search_results: List of search result dictionaries
        confidence_threshold: Minimum confidence score for extraction
        
    Returns:
        Dictionary containing extracted intelligence data
    """
    # Implementation here
```

### JavaScript/React (Frontend)

- **Use functional components** with hooks
- **Follow Material-UI patterns** for consistency
- **Use meaningful component names**
- **Keep components focused** and reusable
- **Use proper prop types** or TypeScript

```jsx
const PortfolioCard = ({ portfolio, onSelect, isSelected }) => {
  const handleSelection = useCallback(() => {
    onSelect(portfolio.id);
  }, [portfolio.id, onSelect]);

  return (
    <Card elevation={isSelected ? 3 : 1}>
      {/* Component implementation */}
    </Card>
  );
};
```

## 🧪 Testing Guidelines

### Backend Tests

- **Write unit tests** for utility functions
- **Test API endpoints** with different scenarios
- **Mock external services** (OpenAI, search engines)
- **Test error handling** and edge cases

### Frontend Tests

- **Test component rendering** and user interactions
- **Mock API calls** in tests
- **Test responsive behavior**
- **Use React Testing Library** best practices

## 📚 Documentation

### Code Documentation

- **Comment complex algorithms** and business logic
- **Use docstrings** for all public functions
- **Document API endpoints** with examples
- **Keep README up to date**

### User Documentation

- **Update installation instructions** for new dependencies
- **Document configuration options**
- **Provide troubleshooting guides**
- **Include screenshots** for UI changes

## 🔒 Security Guidelines

### API Keys and Secrets

- **Never commit API keys** or secrets
- **Use environment variables** for configuration
- **Update .gitignore** for new sensitive files
- **Document required environment variables**

### Input Validation

- **Validate all user inputs** on both frontend and backend
- **Sanitize search queries** to prevent injection
- **Handle file uploads securely**
- **Implement rate limiting** for API endpoints

## 📦 Release Process

### Version Numbering

We follow Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Checklist

1. **Update version numbers** in package.json and setup.py
2. **Update CHANGELOG.md** with new features and fixes
3. **Run full test suite**
4. **Update documentation** if needed
5. **Create release notes** with migration guide if applicable

## 🏆 Recognition

Contributors will be recognized in:

- **README.md** acknowledgments section
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions

## ❓ Questions?

- **Check existing issues** and documentation first
- **Join our discussions** for general questions
- **Create an issue** for specific problems
- **Email maintainers** for private concerns

## 📄 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

Thank you for contributing to making presales automation more intelligent and effective! 🚀