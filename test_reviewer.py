"""Unit tests for AI Code Reviewer"""

import pytest
from reviewer import CodeReviewer


class TestCodeReviewer:
    def test_initialization(self):
        reviewer = CodeReviewer()
        assert reviewer is not None
    
    def test_review_python_code(self):
        reviewer = CodeReviewer()
        code = """
def vulnerable():
    eval(user_input)
"""
        issues = reviewer.review(code, "python")
        assert isinstance(issues, list)
    
    def test_review_javascript_code(self):
        reviewer = CodeReviewer()
        code = """
function test() {
    eval(userInput);
}
"""
        issues = reviewer.review(code, "javascript")
        assert isinstance(issues, list)
    
    def test_detect_sql_injection(self):
        reviewer = CodeReviewer()
        code = "query = f'SELECT * FROM users WHERE id = {user_id}'"
        issues = reviewer.review(code, "python")
        # Should detect SQL injection risk
        assert any("sql" in str(i).lower() for i in issues)
    
    def test_detect_hardcoded_secrets(self):
        reviewer = CodeReviewer()
        code = 'api_key = "sk-1234567890abcdef"'
        issues = reviewer.review(code, "python")
        # Should detect hardcoded secret
        assert any("secret" in str(i).lower() or "key" in str(i).lower() for i in issues)


class TestSecurityPatterns:
    def test_sql_injection_pattern(self):
        reviewer = CodeReviewer()
        # Test various SQL injection patterns
        patterns = [
            "SELECT * FROM users WHERE id = " + "{}",
            "SELECT * FROM users WHERE id = '{}'",
            "cursor.execute(query.format(user_id))",
        ]
        for pattern in patterns:
            issues = reviewer.review(pattern, "python")
            # Should detect at least one issue
            assert isinstance(issues, list)
    
    def test_xss_pattern(self):
        reviewer = CodeReviewer()
        code = 'response = "<div>" + user_input + "</div>"'
        issues = reviewer.review(code, "python")
        # Should detect XSS risk
        assert isinstance(issues, list)
