#!/usr/bin/env python3
"""
AI Code Reviewer
================
An intelligent code review tool that uses AI to analyze your code.

Features:
- Multi-language support (Python, JavaScript, TypeScript, Go, Rust, Java)
- Security vulnerability detection
- Code quality analysis
- Best practices suggestions
- Performance recommendations
- GitHub integration
- CLI interface
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import litellm
import re


LANGUAGE_EXTENSIONS = {
    'python': ['.py'],
    'javascript': ['.js', '.jsx'],
    'typescript': ['.ts', '.tsx'],
    'go': ['.go'],
    'rust': ['.rs'],
    'java': ['.java'],
    'cpp': ['.cpp', '.cc', '.cxx'],
    'c': ['.c', '.h'],
}


@dataclass
class ReviewResult:
    """Code review result"""
    file: str
    issues: List[Dict]
    score: int
    suggestions: List[str]


class CodeAnalyzer:
    """Static code analysis without AI"""
    
    RULES = {
        'python': [
            {'pattern': r'eval\s*\(', 'severity': 'high', 'message': 'Avoid eval() - security risk'},
            {'pattern': r'os\.system\s*\(', 'severity': 'high', 'message': 'Avoid os.system() - shell injection risk'},
            {'pattern': r'pickle\.loads?', 'severity': 'medium', 'message': 'Pickle can be unsafe with untrusted data'},
            {'pattern': r'password\s*=\s*["\'][^"\']+["\']', 'severity': 'medium', 'message': 'Hardcoded password detected'},
            {'pattern': r'TODO|FIXME|XXX|HACK', 'severity': 'low', 'message': 'Incomplete code marker found'},
            {'pattern': r'except:\s*$', 'severity': 'medium', 'message': 'Bare except clause - catches all exceptions'},
            {'pattern': r'print\s*\(', 'severity': 'low', 'message': 'Debug print statement found'},
        ],
        'javascript': [
            {'pattern': r'eval\s*\(', 'severity': 'high', 'message': 'Avoid eval() - security risk'},
            {'pattern': r'console\.log', 'severity': 'low', 'message': 'Debug console.log found'},
            {'pattern': r'document\.write', 'severity': 'high', 'message': 'document.write is dangerous'},
            {'pattern': r'innerHTML\s*=', 'severity': 'medium', 'message': 'Potential XSS via innerHTML'},
            {'pattern': r'password|pwd|secret', 'severity': 'high', 'message': 'Potential credential in code'},
            {'pattern': r'var\s+\w+', 'severity': 'low', 'message': 'Use let/const instead of var'},
        ],
        'typescript': [
            {'pattern': r'@ts-ignore', 'severity': 'low', 'message': 'Type checking disabled'},
            {'pattern': r'any\s*\)', 'severity': 'low', 'message': 'Avoid using any type'},
            {'pattern': r'console\.log', 'severity': 'low', 'message': 'Debug console.log found'},
        ],
        'go': [
            {'pattern': r'fmt\.Println', 'severity': 'low', 'message': 'Debug print found'},
            {'pattern': r'panic\s*\(', 'severity': 'medium', 'message': 'Panic usage detected'},
            {'pattern': r'//TODO', 'severity': 'low', 'message': 'TODO comment found'},
        ],
        'rust': [
            {'pattern': r'unsafe\s*{', 'severity': 'medium', 'message': 'Unsafe code block'},
            {'pattern': r'\.unwrap\(\)', 'severity': 'low', 'message': 'Using unwrap() - may panic'},
            {'pattern': r'eprintln!', 'severity': 'low', 'message': 'Error print to stderr'},
        ],
    }
    
    def __init__(self):
        self.issues = []
        self._compiled_rules = {}
        for lang, rules in self.RULES.items():
            self._compiled_rules[lang] = []
            for rule in rules:
                self._compiled_rules[lang].append({
                    'pattern': re.compile(rule['pattern']),
                    'severity': rule['severity'],
                    'message': rule['message']
                })
    
    def analyze_file(self, filepath: str) -> ReviewResult:
        """Analyze a single file"""
        issues = []
        suggestions = []
        
        try:
            lang = self._detect_language(filepath)
            
            lines_count = 0
            has_docstring = False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    lines_count += 1
                    
                    if lang == 'python':
                        if '"""' in line or "'''" in line:
                            has_docstring = True
                            
                    if lang in self._compiled_rules:
                        for rule in self._compiled_rules[lang]:
                            if rule['pattern'].search(line):
                                issues.append({
                                    'line': i,
                                    'severity': rule['severity'],
                                    'message': rule['message'],
                                    'code': line.strip()[:80]
                                })
            
            # Check file size
            if lines_count > 1000:
                suggestions.append(f"File has {lines_count} lines - consider splitting")
            
            # Check for missing docstrings
            if lang == 'python' and lines_count > 50 and not has_docstring:
                suggestions.append("Consider adding a docstring")
                
        except Exception as e:
            issues.append({
                'line': 0,
                'severity': 'error',
                'message': f"Could not read file: {str(e)}",
                'code': ''
            })
        
        # Calculate score
        score = 100
        for issue in issues:
            if issue['severity'] == 'high':
                score -= 20
            elif issue['severity'] == 'medium':
                score -= 10
            elif issue['severity'] == 'low':
                score -= 3
        
        score = max(0, score)
        
        return ReviewResult(
            file=filepath,
            issues=issues,
            score=score,
            suggestions=suggestions
        )
    
    def _detect_language(self, filepath: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext = Path(filepath).suffix.lower()
        
        for lang, extensions in LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang
        return None


class CodeReviewer:
    """AI-powered code analysis using litellm"""
    
    def __init__(self, model: str = 'gpt-4o-mini'):
        self.model = model
        
    def review(self, code: str, language: str) -> List[Dict]:
        """Review code snippet (for tests)"""
        prompt = f"""
You are an expert code reviewer. Review the following {language} code for security vulnerabilities, bugs, and quality issues.
Return the result as a JSON object with a single key "issues", which is a list of objects.
Each issue object must have:
- "line": integer line number (or 0 if general)
- "severity": "high", "medium", or "low"
- "message": string describing the issue
- "code": string containing the relevant code snippet

Code to review:
```
{code}
```
"""
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            return parsed.get("issues", [])
        except Exception as e:
            return [{"line": 0, "severity": "error", "message": f"LLM Error: {str(e)}", "code": ""}]
            
    def analyze_file(self, filepath: str) -> ReviewResult:
        """Analyze a single file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_content = f.read()
            lang = self._detect_language(filepath) or "unknown"
            
            prompt = f"""
You are an expert code reviewer. Review the following {lang} file for security vulnerabilities, bugs, and quality issues.
Return the result as a JSON object with the following structure:
{{
    "issues": [
        {{"line": 10, "severity": "high", "message": "SQL injection risk", "code": "query = ..."}}
    ],
    "score": 85,
    "suggestions": [
        "Use parameterized queries instead of string formatting"
    ]
}}
Score should be 0-100 (100 is perfect).

File content:
```
{file_content}
```
"""
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result_json = response.choices[0].message.content
            parsed = json.loads(result_json)
            
            return ReviewResult(
                file=filepath,
                issues=parsed.get("issues", []),
                score=parsed.get("score", 100),
                suggestions=parsed.get("suggestions", [])
            )
            
        except Exception as e:
            return ReviewResult(
                file=filepath,
                issues=[{"line": 0, "severity": "error", "message": f"Error: {str(e)}", "code": ""}],
                score=0,
                suggestions=[]
            )
            
    def _detect_language(self, filepath: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext = Path(filepath).suffix.lower()
        for lang, extensions in LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                return lang
        return None

class GitHubIntegration:
    """GitHub integration for code reviews"""
    
    def __init__(self, token: str = None):
        self.token = token or os.environ.get('GITHUB_TOKEN')
    
    def create_review(self, owner: str, repo: str, pr_number: int, body: str) -> bool:
        """Create a code review comment"""
        if not self.token:
            print("⚠️ No GitHub token configured")
            return False
        
        import requests
        
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'body': body,
            'event': 'COMMENT'
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            return response.status_code == 200
        except:
            return False


def print_review(result: ReviewResult):
    """Print review result nicely"""
    print(f"\n📄 {result.file}")
    print(f"   Score: {result.score}/100")
    
    if result.issues:
        print("   Issues:")
        for issue in result.issues:
            emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢', 'error': '❌'}.get(issue['severity'], '⚪')
            print(f"     {emoji} Line {issue['line']}: {issue['message']}")
    
    if result.suggestions:
        print("   Suggestions:")
        for suggestion in result.suggestions:
            print(f"     💡 {suggestion}")


def main():
    parser = argparse.ArgumentParser(description='AI Code Reviewer')
    parser.add_argument('path', nargs='?', default='.', help='File or directory to review')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recursive scan')
    parser.add_argument('--output', '-o', help='Output JSON report')
    parser.add_argument('--github', '-g', nargs=3, metavar=('OWNER', 'REPO', 'PR'),
                       help='Create GitHub review')
    parser.add_argument('--extensions', '-e', help='File extensions to check (comma separated)')
    parser.add_argument('--model', '-m', default='gpt-4o-mini', help='LLM model to use (e.g. gpt-4o, ollama/llama3)')
    
    args = parser.parse_args()
    
    print("🔍 AI Code Reviewer")
    print("=" * 50)
    
    analyzer = CodeReviewer(model=args.model)
    results = []
    
    path = Path(args.path)
    
    # Determine extensions to check
    extensions = None
    if args.extensions:
        extensions = ['.' + ext.strip('.') for ext in args.extensions.split(',')]
    
    # Collect files
    files = []
    if path.is_file():
        files = [str(path)]
    elif path.is_dir():
        if args.recursive:
            for ext in (extensions or ['.py', '.js', '.ts', '.go', '.rs', '.java', '.cpp', '.c']):
                files.extend(path.rglob(f'*{ext}'))
        else:
            for ext in (extensions or ['.py', '.js', '.ts', '.go', '.rs', '.java', '.cpp', '.c']):
                files.extend(path.glob(f'*{ext}'))
    
    print(f"📁 Analyzing {len(files)} files...\n")
    
    # Analyze files
    for filepath in files:
        if '__pycache__' in filepath or 'node_modules' in filepath or '.git' in filepath:
            continue
        
        result = analyzer.analyze_file(filepath)
        results.append(result)
        print_review(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    total_score = sum(r.score for r in results) / len(results) if results else 0
    print(f"   Overall Score: {total_score:.1f}/100")
    print(f"   Files Reviewed: {len(results)}")
    
    high_issues = sum(1 for r in results for i in r.issues if i['severity'] == 'high')
    medium_issues = sum(1 for r in results for i in r.issues if i['severity'] == 'medium')
    
    print(f"   🔴 High: {high_issues}")
    print(f"   🟡 Medium: {medium_issues}")
    
    # Save to JSON
    if args.output:
        output_data = {
            'summary': {
                'total_score': total_score,
                'files_reviewed': len(results),
                'high_issues': high_issues,
                'medium_issues': medium_issues
            },
            'results': [
                {
                    'file': r.file,
                    'score': r.score,
                    'issues': r.issues,
                    'suggestions': r.suggestions
                }
                for r in results
            ]
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n📄 Report saved to: {args.output}")
    
    # GitHub integration
    if args.github:
        owner, repo, pr = args.github
        body = f"## 🔍 Code Review\n\n"
        body += f"**Overall Score:** {total_score:.1f}/100\n\n"
        body += f"**Files Reviewed:** {len(results)}\n\n"
        body += f"**Issues Found:**\n"
        body += f"- 🔴 High: {high_issues}\n"
        body += f"- 🟡 Medium: {medium_issues}\n\n"
        
        github = GitHubIntegration()
        if github.create_review(owner, repo, int(pr), body):
            print("\n✅ GitHub review created!")
        else:
            print("\n⚠️ Failed to create GitHub review")


if __name__ == '__main__':
    main()
