# Research and Study Assistant - Without RAG

A study chatbot built with Python, Streamlit and Groq.

## Features

- Choose between three language models.
- Ask study questions and follow-up questions.
- Clear the conversation to start again.

## Models

- GPT-OSS 120B
- GPT-OSS 20B
- Qwen 3.8 27B

All three models are accessed through Groq.

## How it works

The chatbot uses the selected model's learned knowledge and recent
conversation. It does not upload documents or browse the web.

## Live app

[Open the app](YOUR_APP_URL)

Replace YOUR_APP_URL with your own deployed app's full https address.

## Use these files in your workshop project

1. Extract this ZIP on your computer.
2. Open the Streamlit blank-template project you created in Codespaces.
3. Upload streamlit_app.py, pyproject.toml, uv.lock and .python-version
   into the project's root folder, replacing the template copies.
4. Open a Bash terminal in that folder and run the commands below.

```bash
uv sync
uv run streamlit run streamlit_app.py
```

Python 3.12 is selected in .python-version. Install uv first if you are
running outside the workshop Codespaces environment.

## API key

For a Codespaces preview, expand Groq API key (optional) in the sidebar,
enter your own Groq key and press Enter.

For the deployed app, add the following in Streamlit Settings > Secrets:

```toml
GROQ_API_KEY = "paste_your_groq_key_here"
```

Once a deployed app has a key in Secrets, leave its sidebar key field blank.
Keep API keys out of your code and GitHub repository.

## Publish changes from Codespaces

```bash
git add streamlit_app.py pyproject.toml uv.lock .python-version
git commit -m "Add study assistant without RAG"
git push origin main
```

Streamlit Community Cloud updates the deployed app after the push.

## Files

| File | Purpose |
| --- | --- |
| streamlit_app.py | Complete app with comments explaining each block |
| pyproject.toml | Project settings and direct dependencies |
| uv.lock | Resolved dependency versions |
| .python-version | Python version for the workshop |
| .gitignore | Keeps credentials and generated files out of Git |
| LICENSE | License retained from the original project |

Workshop edition: explanatory code comments, project metadata and this
README have been updated for teaching. App behavior is unchanged.
