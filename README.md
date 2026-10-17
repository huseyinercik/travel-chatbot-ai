# Travel Chatbot — Promptfoo Evaluation

A hands-on project for evaluating a travel chatbot through API-based testing, deterministic assertions, semantic evaluation, and LLM-as-a-judge techniques.

## 1. Project Overview

This project evaluates a locally hosted travel chatbot through its HTTP API using Promptfoo.

### Evaluation techniques

- **Deterministic assertions:** Validate response content using checks such as `contains`, `not-contains`, `contains-any`, and `contains-all`.
- **Factuality evaluation:** Assess whether responses are consistent with reference information.
- **Answer relevance:** Evaluate whether a response addresses the user's question.
- **Hallucination evaluation:** Check for unsupported or fabricated claims.
- **LLM-as-a-judge:** Use `llm-rubric` with `openai:gpt-4o-mini` to assess semantic criteria.
- **Latency checks:** Evaluate response-time requirements.
- **Negative controls:** Use intentionally incorrect responses to check whether evaluation criteria detect known problems.
- **Source-grounded evaluation:** Assess whether an answer follows a supplied source text without contradicting it.

The project combines deterministic checks with semantic evaluation. Judge-based results may vary between runs, so results should be interpreted alongside the actual responses, test criteria, and judge explanations.

## 2. Project Structure

```text
travel-chatbot-ai/
├── app.py
├── system_prompt.txt
├── README.md
├── .gitignore
└── promptfoo/
    ├── promptfooconfig.yaml
    ├── tests.yaml
    ├── rag-tests.yaml
    └── rag-negative-control.yaml
```

The Python virtual environment, local configuration files containing secrets, caches, and generated evaluation reports are excluded from version control where configured in `.gitignore`.

## 3. Run the Chatbot API

Open PowerShell in the project root:

```powershell
cd C:\Users\ercik\Desktop\travel-chatbot-ai
```

Activate the Python virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start the API server:

```powershell
uvicorn app:app --reload
```

Alternatively:

```powershell
python -m uvicorn app:app --reload
```

The API endpoint is:

`http://127.0.0.1:8000/chat`

Keep the API server running while executing evaluations.

### Check the API

Open a second PowerShell terminal and send a test request:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"input":"Merhaba"}'
```

Verify that the API returns a response before running Promptfoo evaluations.

## 4. Configure the OpenAI API Key

The chatbot and judge-based evaluations require an OpenAI API key.

The application loads its API key from the local `.env` file. Promptfoo judge evaluations can use the `OPENAI_API_KEY` environment variable in the terminal running the evaluations.

Set the variable for the current PowerShell session without displaying the key:

```powershell
$secureKey = Read-Host "Enter your OpenAI API key" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)

try {
    $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    Remove-Variable secureKey
    Remove-Variable ptr
}
```

Verify that the environment variable is defined without printing its value:

```powershell
[PSCustomObject]@{
    Defined = -not [string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)
}
```

**Security notes:**

- The environment variable applies only to the current PowerShell session.
- Never commit API keys, access tokens, or secret-bearing `.env` files.
- Keep local secrets and generated reports out of public repositories unless they have been reviewed and are safe to share.

## 5. Run Promptfoo Evaluations

Navigate to the Promptfoo directory:

```powershell
cd C:\Users\ercik\Desktop\travel-chatbot-ai\promptfoo
```

Check the installed version:

```powershell
npx promptfoo --version
```

Run the main evaluation suite:

```powershell
npx promptfoo eval --no-cache --max-concurrency 1 --verbose -o results.json
```

The `-o` option saves the evaluation report to a JSON file. The report is intended for local inspection and is excluded from version control according to the repository's ignore rules.

### Run a focused semantic evaluation

```powershell
npx promptfoo eval --filter-pattern "Kapadokya cevabının anlamsal doğruluğu" --no-cache --max-concurrency 1 --verbose -o judge-smoke.json
```

`--no-cache` requests fresh evaluation results, and `--max-concurrency 1` runs one evaluation at a time to make troubleshooting easier.

### Run the source-grounded evaluation

Start the API first, then run:

```powershell
npx promptfoo eval -c rag-tests.yaml --no-cache --max-concurrency 1
```

This test supplies a source text and a question to the chatbot, then uses `llm-rubric` to assess whether the response follows the source and avoids contradictions.

**Scope limitation:** This is a source-grounded answer evaluation, not a full RAG pipeline test. It does not independently verify document retrieval, chunking, embedding search, or retrieval quality.

### Run the negative control separately

```powershell
npx promptfoo eval -c rag-negative-control.yaml --no-cache --max-concurrency 1
```

This test intentionally supplies an answer that contradicts the source text. A `FAIL` is the expected outcome because the evaluation should detect the contradiction.

Keep this negative control separate from the normal regression suite when reporting pass rates.

## 6. Assertion Types

| Assertion or check | Purpose |
|---|---|
| `contains` | Checks whether a response contains expected text. |
| `not-contains` | Checks that specified text is absent. |
| `contains-any` | Checks whether at least one expected value is present. |
| `contains-all` | Checks whether all expected values are present. |
| `factuality` | Evaluates consistency with reference information. |
| `llm-rubric` | Uses a judge model to assess natural-language criteria. |
| Answer relevance | Evaluates whether the response addresses the question. |
| Hallucination evaluation | Checks for unsupported claims. |
| Latency | Checks response-time criteria. |

The assertions used depend on the individual test configuration. Rubrics should define observable evaluation criteria rather than rely on vague instructions such as "give a good answer."

## 7. Interpreting Results

- **PASS:** The test satisfied its configured assertion criteria.
- **FAIL:** An assertion did not pass. Inspect the actual response, reference information, rubric, and judge explanation.
- **ERROR:** The test could not complete because of a technical or configuration problem.

A `FAIL` does not automatically mean the chatbot is defective. In a negative-control test, failure is expected when the evaluator correctly identifies the deliberately incorrect response.

Likewise, a passing judge assertion is evidence that the response met the configured criteria; it is not proof of complete factual correctness.

### Inspect the evaluation report

```powershell
npx promptfoo view
```

To use a specific port:

```powershell
npx promptfoo view --port 15501
```

Review failed assertions and judge explanations before changing a test case or rubric.

## 8. Security and Git Hygiene

The repository should not contain:

- `.env` files with secrets
- API keys or access tokens
- Python virtual environments
- Node.js dependencies and runtime caches
- Local evaluation reports that are not intended for publication

The root `.gitignore` excludes sensitive local files, generated files, and selected evaluation reports.

Always review `git status` before committing changes.

## 9. Current Scope and Next Steps

Implemented evaluation areas include API-based testing, deterministic assertions, judge-based semantic evaluation, hallucination-related checks, and source-grounded evaluation with a negative control.

Potential next steps:

1. Strengthen and expand the evaluation dataset.
2. Validate expected outcomes against actual chatbot responses.
3. Add reproducible evaluation summaries and representative test cases.
4. Investigate retrieval-specific metrics if a real RAG pipeline is introduced.
5. Integrate automated evaluations into a CI/CD pipeline.

## 10. Learning Objectives

This project demonstrates hands-on work with:

- API-based chatbot testing
- Promptfoo configuration and test execution
- Deterministic and semantic assertions
- LLM-as-a-judge evaluation
- Evaluation rubric design
- Hallucination-related checks
- Negative controls and test-result analysis
- Source-grounded response evaluation
