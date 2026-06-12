# Agent Guidelines

## Code Style

- Write pythonic code: prefer list comprehensions, `with` statements, unpacking, and idiomatic patterns
- Keep flow simple and easy to follow — avoid unnecessary abstractions
- Do not use static type annotations in Python
- Use `snake_case` for all variable, function, and file names
- Avoid using reserved keywords of Python, SQL, JS, or CSS as identifiers or file names

## Comments

- Comment only when the reason behind code is non-obvious
- Use standard single-line comments (`#`) — no decorative separators like `----` or `====`
- Do not write docstrings or multi-line comment blocks

## Changes

- Make the minimal change needed to accomplish the task — no refactors or cleanups beyond scope
- Do not install libraries; recommend them and let the user install

## Files

- Always end new files with a newline
