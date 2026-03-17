# Architecture Document: AI Code Reviewer

## 1. System Overview

AI Code Reviewer is a Python CLI tool that scans source code files to identify issues, security vulnerabilities, and code quality problems. It uses pattern matching and rule-based analysis.

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface                          │
│                    (reviewer.py)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Analysis Engine                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  - File scanner (recursive)                         │  │
│  │  - Language detection                                │  │
│  │  - Pattern matching                                  │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Security │    │ Quality  │    │ Scoring  │
    │ Rules    │    │ Rules    │    │ Engine   │
    └──────────┘    └──────────┘    └──────────┘
```

## 3. Core Components

### CLI Handler
- Command-line argument parsing
- File/directory selection
- Output formatting

### Analysis Engine
- Recursive file scanning
- Language detection by extension
- Pattern-based rule matching

### Rules Engine
- Security rules (vulnerabilities)
- Quality rules (best practices)
- Scoring calculation

### Output Formatter
- Console output
- JSON report generation
- GitHub PR integration

## 4. File Structure

```
ai-code-reviewer/
├── reviewer.py         # Main application
├── specs/             # Documentation
└── README.md
```

---

*Document Version: 1.0*  
*Created: 2026-03-17*
