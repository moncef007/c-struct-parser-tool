# Contributing to Struct Parser Tool

Thank you for your interest in contributing to **C Struct Parser Tool**! 
This document outlines how you can help improve the project — whether you're reporting a bug, proposing a feature, or submitting code.

## Code of Conduct

By participating, you agree to uphold a respectful and inclusive environment. Harassment or discrimination of any kind will not be tolerated.

## How You Can Help

### Report Bugs
- Use the [GitHub Issues](https://github.com/moncef007/c-struct-parser-tool/issues) tracker.
- Include:
  - Your OS and Python version
  - The struct definition (C code)
  - The binary dump (or hex snippet)
  - The command you ran
  - Expected vs. actual output

### Suggest Features
- Open an issue with the label `enhancement`.
- Explain the use case clearly (e.g., “Support for big-endian dumps” or “Add `--packed` mode”).

### Improve Documentation
- Fix typos, clarify examples, or expand the README.
- Pull requests welcome!

### Submit Code
We love pull requests! Here’s how:

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/your-idea`
3. **Commit your changes**: `git commit -am 'feat: add some feature'`
4. **Push to the branch**: `git push origin feature/your-idea`
5. **Open a Pull Request**

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/moncef007/c-struct-parser-tool.git
cd c-struct-parser-tool
```

2. Install in editable mode with dev dependencies:
```bash
pip install -e .[dev,test]
```

3. Run test
```bash
make test
```

## Code Style & Quality
1. **Formatting:** Use black (no config needed).
2. **Type hints:** Required for new code.
3. **Tests:** Add tests for new functionality.
4. **Commit messages:** Clear and descriptive (e.g., “fix: handle empty structs”).

## License
By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0 or later (see LICENSE ).

---

We appreciate every contribution — big or small!