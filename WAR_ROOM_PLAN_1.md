# Issue #1 Plan

- [x] Add `litellm` to `requirements.txt`
- [x] Update `reviewer.py` to accept `--model` parameter for local/remote LLMs (defaulting to a sensible model like `gpt-4o-mini` or `ollama/llama3`)
- [x] Replace `CodeAnalyzer` logic to use `litellm` for generating code reviews based on file contents, returning a parsed JSON into `ReviewResult`
- [x] Update `test_reviewer.py` to mock `litellm.completion` and fix any broken references (e.g., `CodeReviewer` vs `CodeAnalyzer`)
