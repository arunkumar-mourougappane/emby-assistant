# Contributing to Emby Helper

Thank you for your interest in contributing to Emby Helper! This document provides guidelines for contributing to the project.

## 🤝 Ways to Contribute

- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new features
- **Code Contributions**: Submit pull requests
- **Documentation**: Improve or add documentation
- **Testing**: Test on different systems and report results

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Version information**:

   - Emby Helper version (commit hash or release)
   - Python version (`python --version`)
   - OS and version
   - Emby server version

2. **Steps to reproduce**:

   - What you did
   - What you expected to happen
   - What actually happened

3. **Logs and errors**:

   - Error messages
   - Terminal output
   - Browser console errors (for web version)

4. **Configuration** (without sensitive data):
   - Which version (Web/GTK)
   - Any custom configuration

## 💡 Feature Requests

When suggesting features:

1. **Describe the feature** clearly
2. **Explain the use case** - why is it useful?
3. **Consider both versions** - should it work in Web and GTK?
4. **Check existing issues** to avoid duplicates

## 🔧 Code Contributions

### Getting Started

1. **Fork the repository**
2. **Clone your fork**:

   ```bash
   git clone https://github.com/YOUR-USERNAME/emby-assistant.git
   cd emby-assistant
   ```

3. **Set up development environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

4. **Configure for testing**:

   ```bash
   cp .env.example .env
   # Edit .env with your test Emby server details
   ```

### Code Style

- **Python**: Follow PEP 8 style guide
- **Comments**: Add docstrings to functions and classes
- **Type hints**: Use type hints where appropriate
- **Imports**: Group and sort imports logically

### Project Structure

```text
emby-helper/
├── app.py              # Flask web application
├── app_gtk.py          # GTK desktop application
├── emby_client.py      # Shared Emby API client
├── config.py           # Shared configuration
├── templates/          # Web UI templates
└── docs/              # Documentation
```

### Making Changes

1. **Create a branch**:

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes**:

   - Keep changes focused and atomic
   - Test both Web and GTK versions if applicable
   - Update documentation if needed

3. **Test your changes**:

   - Test Web version: `python app.py`
   - Test GTK version: `python app_gtk.py`
   - Verify against a real Emby server
   - Check error handling

4. **Commit your changes**:

   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

   Use clear commit messages:

   - `Add: New feature description`
   - `Fix: Bug description`
   - `Update: What was updated`
   - `Docs: Documentation changes`

5. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**:
   - Describe what your PR does
   - Reference any related issues
   - Include screenshots if UI changes
   - List any testing performed

### Testing Guidelines

- **Test both versions** when making shared code changes
- **Test with different Emby configurations**:
  - Empty libraries
  - Large libraries
  - Active processing
  - No active tasks
- **Test error conditions**:
  - Server offline
  - Invalid API key
  - Network issues
  - Missing images

## 📝 Documentation Contributions

Documentation improvements are always welcome!

### Documentation Files

- `README.md` - Main documentation
- `docs/QUICKSTART.md` - Quick start guide
- `docs/README-GTK.md` - GTK version docs
- `docs/COMPARISON.md` - Version comparison
- `docs/THUMBNAILS.md` - Feature documentation
- `docs/PROJECT.md` - Project overview

### Documentation Guidelines

- Use clear, simple language
- Include code examples where helpful
- Add screenshots for UI features
- Keep formatting consistent
- Update the documentation index if adding new docs

## 🎨 UI/UX Improvements

For UI improvements:

1. **Consider both versions**:

   - Web: HTML/CSS/JavaScript
   - GTK: GTK3 widgets and styling

2. **Maintain consistency**:

   - Colors and themes
   - Layout and spacing
   - Icons and badges

3. **Test responsiveness** (Web version):
   - Desktop browsers
   - Mobile browsers
   - Different screen sizes

## 🔐 Security

- **Never commit** `.env` files with real credentials
- **Use environment variables** for sensitive data
- **Report security issues** privately (don't open public issues)

## 📋 Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows project style
- [ ] Changes are tested on both versions (if applicable)
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No sensitive data in code
- [ ] New dependencies are added to `requirements.txt`

## 🏗️ Development Setup Tips

### GTK Development (Linux)

Install GTK development tools:

```bash
# Ubuntu/Debian
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 glade

# Fedora
sudo dnf install python3-gobject gtk3 glade

# Arch
sudo pacman -S python-gobject gtk3 glade
```

### Web Development

For web UI development:

- Use browser developer tools (F12)
- Test in multiple browsers
- Check console for JavaScript errors

## 🤔 Questions?

- **Need help?** Open an issue with the "question" label
- **Not sure about something?** Ask before making major changes
- **Want to discuss ideas?** Open an issue for discussion

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## 🙏 Thank You!

Every contribution, no matter how small, helps make Emby Helper better!

---

**Quick Links:**
[Main README](../README.md) |
[Documentation](docs/INDEX.md) |
[Project Structure](docs/PROJECT.md)
