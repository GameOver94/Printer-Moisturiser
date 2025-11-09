# Contributing to Printer Moisturiser

Thank you for your interest in contributing to Printer Moisturiser!

## Code Style Guidelines

This project follows specific coding conventions to maintain consistency:

### Naming Conventions

- **Functions**: Use `snake_case`
  ```python
  def collect_printer_info():
      pass
  ```

- **Variables**: Use `camelCase`
  ```python
  printerInfo = {}
  ```

- **Private Members**: Use `m_` prefix
  ```python
  class MyClass:
      def __init__(self):
          self.m_privateValue = 0
  ```

### Type Hinting

All functions must include complete type hints:

```python
def my_function(param1: str, param2: int) -> bool:
    """Function with type hints."""
    return True
```

### Documentation

All modules, classes, and functions must have docstrings:

```python
def my_function(param: str) -> str:
    """Brief description of the function.

    Args:
        param: Description of the parameter.

    Returns:
        str: Description of the return value.
    """
    return param
```

## Testing

Before submitting a PR:

1. Test your changes locally:
   ```bash
   ./test.sh
   ```

2. Ensure all imports work:
   ```bash
   cd src && python -m py_compile *.py
   ```

3. Test with Docker:
   ```bash
   docker-compose build
   ```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes following the code style guidelines
4. Test your changes thoroughly
5. Commit your changes with clear commit messages
6. Push to your fork
7. Open a Pull Request with a clear description of your changes

## Reporting Issues

When reporting issues, please include:

- Description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, Docker version)
- Relevant log output

## Questions?

Feel free to open an issue for any questions or concerns.
