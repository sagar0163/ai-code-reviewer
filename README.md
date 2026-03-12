# AI Code Reviewer 🤖

An intelligent code review tool that analyzes your code for issues, security vulnerabilities, and best practices.

## Features

- 🔍 **Multi-language Support** - Python, JavaScript, TypeScript, Go, Rust, Java, C/C++
- 🛡️ **Security Analysis** - Detect hardcoded passwords, eval(), XSS vulnerabilities
- 📊 **Code Quality** - Check for TODOs, bare excepts, code complexity
- 💡 **Suggestions** - Best practices and performance recommendations
- 📈 **Scoring** - 100-point scoring system
- 🔗 **GitHub Integration** - Post reviews directly to PRs
- 📄 **JSON Reports** - Export results for CI/CD

## Installation

```bash
# Clone
git clone https://github.com/sagar0163/ai-code-reviewer.git
cd ai-code-reviewer

# Run
python3 reviewer.py --help
```

## Usage

### Basic Usage

```bash
# Review a single file
python3 reviewer.py main.py

# Review a directory
python3 reviewer.py ./src

# Recursive scan
python3 reviewer.py ./src --recursive
```

### Advanced Options

```bash
# Specific file extensions
python3 reviewer.py ./src --extensions py,js,ts

# Save JSON report
python3 reviewer.py ./src --output report.json

# GitHub PR review
python3 reviewer.py ./src --github owner repo 1
```

### Output Example

```
🔍 AI Code Reviewer
==================================================

📄 src/main.py
   Score: 85/100
   Issues:
     🟡 Line 42: Avoid os.system() - shell injection risk
     🟢 Line 15: Debug print statement found

📄 src/utils.py
   Score: 95/100
   Suggestions:
     💡 Consider adding a docstring

==================================================
📊 SUMMARY
==================================================
   Overall Score: 90.0/100
   Files Reviewed: 5
   🔴 High: 0
   🟡 Medium: 1
```

## Supported Languages

| Language | Extensions | Security Checks |
|----------|------------|----------------|
| Python | .py | eval, os.system, pickle, passwords |
| JavaScript | .js, .jsx | eval, innerHTML, XSS |
| TypeScript | .ts, .tsx | @ts-ignore, any type |
| Go | .go | fmt.Print, panic |
| Rust | .rs | unsafe, unwrap() |
| Java | .java | Runtime.exec |
| C/C++ | .c, .cpp | gets(), strcpy |

## Scoring System

| Score | Rating |
|-------|---------|
| 90-100 | ⭐ Excellent |
| 70-89 | ✅ Good |
| 50-69 | ⚠️ Needs Work |
| <50 | ❌ Critical |

## GitHub Integration

Set your GitHub token:

```bash
export GITHUB_TOKEN=your_token_here
```

Then run with PR number:

```bash
python3 reviewer.py ./src --github sagar0163 my-project 42
```

## CI/CD Integration

Add to your GitHub Actions:

```yaml
- name: Code Review
  run: |
    python3 reviewer.py ./src --output review.json
    
- name: Upload Review
  uses: actions/upload-artifact@v2
  with:
    name: code-review
    path: review.json
```

## Rules Detected

### High Severity
- `eval()` usage
- `os.system()` / `shell_exec()`
- Hardcoded passwords/secrets
- `document.write()` (XSS)

### Medium Severity
- Pickle with untrusted data
- `innerHTML` assignment
- Bare except clauses

### Low Severity
- Debug print statements
- TODO/FIXME comments
- Unwrap() on Results

## License

MIT License - Feel free to use!

## Author

Created by Sagar Jadhav

# Added enhancement timestamp
