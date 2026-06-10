# IoT Demo App

This project contains a simple Streamlit dashboard that simulates an IoT device and shows:
- temperature
- humidity
- presence detection

It also includes an optional AI summary feature powered by OpenRouter.

## Features
- Random simulated sensor values updated every 3 seconds
- Color-coded cards for easy understanding
- History table of recent readings
- Optional AI-generated explanation of the current situation

## Requirements
Install dependencies with:

```bash
pip install -r requirements.txt
```

## Run the app

```bash
streamlit run app2.py
```

## AI configuration
Create a `.env` file in the project root with:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

If `OPENROUTER_API_KEY` is not set, the AI section will show a fallback message instead of calling the remote model.
