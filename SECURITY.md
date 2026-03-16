# Security Analysis

## Supported Languages
- Python
- JavaScript
- TypeScript
- Java
- Go
- Ruby

## Vulnerability Categories

### Critical
- SQL Injection
- Command Injection
- Hardcoded Credentials
- Path Traversal

### High
- Cross-Site Scripting (XSS)
- XML External Entity (XXE)
- Insecure Deserialization

### Medium
- Information Disclosure
- Weak Cryptography
- Missing Access Control

### Low
- Missing Headers
- Verbose Error Messages

## Usage

```python
from reviewer import CodeReviewer

reviewer = CodeReviewer()
issues = reviewer.review(code, language)
for issue in issues:
    print(f"{issue.severity}: {issue.message}")
```
