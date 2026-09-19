"""Unit tests for AI Code Reviewer"""

import pytest
import json
from unittest.mock import patch, MagicMock
from reviewer import CodeReviewer


class TestCodeReviewer:
    def test_initialization(self):
        reviewer = CodeReviewer()
        assert reviewer is not None
        assert reviewer.model == 'gpt-4o-mini'
    
    @patch('reviewer.litellm.completion')
    def test_review_python_code(self, mock_completion):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({"issues": [{"line": 2, "severity": "high", "message": "eval usage", "code": "eval(user_input)"}]})))
        ]
        mock_completion.return_value = mock_response

        reviewer = CodeReviewer()
        code = """
def vulnerable():
    eval(user_input)
"""
        issues = reviewer.review(code, "python")
        assert isinstance(issues, list)
        assert len(issues) == 1
        assert issues[0]['severity'] == 'high'
    
    @patch('reviewer.litellm.completion')
    def test_review_javascript_code(self, mock_completion):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({"issues": [{"line": 2, "severity": "high", "message": "eval usage", "code": "eval(userInput);"}]})))
        ]
        mock_completion.return_value = mock_response

        reviewer = CodeReviewer()
        code = """
function test() {
    eval(userInput);
}
"""
        issues = reviewer.review(code, "javascript")
        assert isinstance(issues, list)
        assert len(issues) == 1
    
    @patch('reviewer.litellm.completion')
    def test_detect_sql_injection(self, mock_completion):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({"issues": [{"line": 1, "severity": "high", "message": "SQL injection risk", "code": "query = f'SELECT * FROM users WHERE id = {user_id}'"}]})))
        ]
        mock_completion.return_value = mock_response

        reviewer = CodeReviewer()
        code = "query = f'SELECT * FROM users WHERE id = {user_id}'"
        issues = reviewer.review(code, "python")
        assert any("sql" in str(i).lower() for i in issues)
    
    @patch('reviewer.litellm.completion')
    def test_detect_hardcoded_secrets(self, mock_completion):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({"issues": [{"line": 1, "severity": "high", "message": "Hardcoded secret key", "code": "api_key = \"sk-1234567890abcdef\""}]})))
        ]
        mock_completion.return_value = mock_response

        reviewer = CodeReviewer()
        code = 'api_key = "sk-1234567890abcdef"'
        issues = reviewer.review(code, "python")
        assert any("secret" in str(i).lower() or "key" in str(i).lower() for i in issues)


class TestSecurityPatterns:
    @patch('reviewer.litellm.completion')
    def test_sql_injection_pattern(self, mock_completion):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({"issues": [{"line": 1, "severity": "high", "message": "SQL injection risk", "code": "SELECT * FROM users WHERE id = {}"}]})))
        ]
        mock_completion.return_value = mock_response

        reviewer = CodeReviewer()
        patterns = [
            "SELECT * FROM users WHERE id = " + "{}",
            "SELECT * FROM users WHERE id = '{}'",
            "cursor.execute(query.format(user_id))",
        ]
        for pattern in patterns:
            issues = reviewer.review(pattern, "python")
            assert isinstance(issues, list)
            assert len(issues) > 0
    
    @patch('reviewer.litellm.completion')
    def test_xss_pattern(self, mock_completion):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({"issues": [{"line": 1, "severity": "high", "message": "XSS risk", "code": "response = \"<div>\" + user_input + \"</div>\""}]})))
        ]
        mock_completion.return_value = mock_response

        reviewer = CodeReviewer()
        code = 'response = "<div>" + user_input + "</div>"'
        issues = reviewer.review(code, "python")
        assert isinstance(issues, list)
        assert len(issues) > 0

