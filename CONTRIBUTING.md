# Contributing to YouTube Agent System

Thank you for your interest in contributing! We welcome contributions from everyone.

## How to Contribute

### Reporting Bugs
1. Check if the bug already exists in [Issues](../../issues)
2. If not, create a new issue with:
   - Clear title describing the bug
   - Detailed description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Code snippets or screenshots if applicable

### Suggesting Enhancements
1. Check existing [Issues](../../issues) and [Discussions](../../discussions)
2. Create a new issue with:
   - Clear title describing the enhancement
   - Detailed description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Submitting Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/youtube_agent_system.git
   cd youtube_agent_system
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/your-bugfix-name
   ```

3. **Set up your development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Make your changes**
   - Write clear, descriptive commit messages
   - Follow PEP 8 style guide for Python code
   - Add comments for complex logic
   - Test your changes thoroughly

5. **Test your changes**
   ```bash
   python main.py
   # Test with various topics and durations
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template with:
     - Description of changes
     - Related issues (use #issue-number)
     - Type of change (feature/bugfix/documentation)
     - Testing performed

## Code Style Guidelines

### Python Code
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Add docstrings to functions and classes

Example:
```python
def generate_script(topic: str, duration: int) -> Dict[str, Any]:
    """
    Generate a video script for the given topic.
    
    Args:
        topic: The video topic
        duration: Duration in seconds
        
    Returns:
        Dictionary containing script data
    """
    pass
```

### Commit Messages
- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Limit the first line to 72 characters
- Reference issues when applicable (#issue-number)

Example:
```
feat: add multi-language support for scripts
- Implement language detection
- Add translation pipeline
- Update content generator
Closes #123
```

### PR Title Format
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `style:` for code style changes
- `refactor:` for code refactoring
- `perf:` for performance improvements
- `test:` for test additions/changes

## Development Workflow

### Areas for Contribution

**High Priority:**
- [ ] Stock footage integration (Pexels API)
- [ ] AI image generation (DALL-E, Stable Diffusion)
- [ ] Real voice synthesis integration
- [ ] Advanced animation effects

**Medium Priority:**
- [ ] Performance optimizations
- [ ] Better error handling
- [ ] Extended topic templates
- [ ] Configuration UI

**Documentation:**
- [ ] API documentation
- [ ] Architecture diagrams
- [ ] Tutorial videos
- [ ] Example scripts

### Adding New Agents

1. Create new agent class in `agents/` extending `BaseAgent`
2. Implement `execute()` method
3. Add logging and error handling
4. Register with `VideoProductionTeam`
5. Add tests and documentation

Example:
```python
from .base_agent import BaseAgent

class MyNewAgent(BaseAgent):
    def __init__(self):
        super().__init__("my_agent", "Agent description")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Executing task: {task}")
        # Implementation here
        return {"result": "data"}
```

### Adding New Tools

1. Create tool class in `tools/` with `async` methods
2. Implement tool interface
3. Add error handling and logging
4. Document parameters and return values
5. Add usage examples

### Adding New Animations

1. Implement animation method in `AnimatedSlideGenerator`
2. Add transition effect to `_create_slide_frame()`
3. Test with various slide durations
4. Document animation behavior

## Testing

Before submitting a PR:

1. **Run the application**
   ```bash
   python main.py
   ```

2. **Test with different topics**
   - Short topics (few words)
   - Long topics (full sentences)
   - Technical topics
   - Non-technical topics

3. **Test with different durations**
   - Short (30 seconds)
   - Medium (3 minutes)
   - Long (10+ minutes)

4. **Check the output video**
   - Verify animations work smoothly
   - Check text doesn't overflow
   - Verify timing is correct
   - Check quality score

## Review Process

1. **Code Review**
   - At least one maintainer review required
   - All checks must pass
   - No merge conflicts

2. **Feedback**
   - Constructive suggestions provided
   - Clear explanations for changes needed
   - Discussion encouraged

3. **Merging**
   - Squash commits if needed
   - Update changelog
   - Close related issues

## Community Guidelines

- Be respectful and inclusive
- Assume good intentions
- Constructive feedback only
- Report inappropriate behavior to maintainers

## Questions?

- Check [README.md](README.md) for project overview
- Check [Discussions](../../discussions) for Q&A
- Open an issue for bugs or features
- Email maintainers for other inquiries

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for making this project better! 🚀
