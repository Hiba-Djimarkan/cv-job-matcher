# CV & Job Matcher

A generative-AI web app that analyses a CV, matches it against a job offer and writes a tailored cover letter. It also has a standalone **CV review** mode that scores a CV and says what is missing.

**Live demo:** https://cv-job-matcher-hiba.streamlit.app/  
**Video demo:** _add your video link here_

## Features
- **Match with a job**: extraction, matching score, strengths, missing skills and a cover letter
- **CV review**: quality score, missing sections and concrete improvements
- **Prompt engineering**: few-shot extraction, persona and chain-of-thought prompts
- **Robust LLM layer**: retries with exponential backoff, JSON validation, clear error messages
- **Demo mode**: runs without any API key, with example results

## Tech stack
Python, Streamlit, Groq API (LLM), pypdf

## Screenshots
_Add images in a `screenshots/` folder and link them:_  
`![Match](screenshots/match.png)`

## Run it locally
1. Clone the repository and open the folder
2. Install the dependencies: `pip install -r requirements.txt`
3. Start the app: `streamlit run app.py`
4. Either tick **Demo mode** in the sidebar, or paste your own Groq API key (free at console.groq.com)

Optional: copy `.env.example` to `.env` and put your key there so you don't have to type it each time.

## Project structure
- `app.py`: Streamlit interface
- `llm.py`: all communication with the API (calls, retries, JSON parsing)
- `prompts.py`: all prompts
- `demo_data.py`: example results for demo mode

## Privacy
The API key you type stays in memory for your session only. In real mode, the CV text is sent to the API provider: do not upload sensitive personal data. Use demo mode to just explore the interface.
