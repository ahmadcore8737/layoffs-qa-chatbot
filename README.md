# Layoffs Q&A Bot 📉

An AI chatbot that answers plain-English questions about global tech layoffs, and draws charts when you ask for one.

Instead of digging through a spreadsheet yourself, you just ask a question like *"which company laid off the most people?"* and the bot translates that into real pandas code, runs it on the data, and gives you the answer, with the actual code shown so you can see exactly how it got there.

🔗 **Live demo:** [layoffs-app-chatbot.streamlit.app](https://layoffs-app-chatbot-fuwecimxd6hgqyhlcxe2uv.streamlit.app)

## Try it out

Ask things like:
- "which company laid off the most people?"
- "how many layoffs happened in the United States?"
- "show layoffs by year as a bar chart"
- "which country had the highest total layoffs in 2024?"

## How it works

1. You type a question in plain English.
2. Google's Gemini model reads the question and writes one small pandas (or matplotlib) command to answer it.
3. That command runs safely against the dataset, nothing outside pandas and matplotlib is allowed to execute.
4. You get back an answer or a chart, plus the exact code that produced it.

If the AI can't answer something, or the question isn't related to layoffs, it says so politely instead of crashing.

## Built with

- **Streamlit** – the chat interface
- **Google Gemini API** – turns questions into pandas code
- **pandas** – does the actual data crunching
- **Matplotlib** – draws the charts

## Dataset

Global tech layoffs data (company, location, industry, country, date, and number of people laid off), covering thousands of layoff events from 2020 onward.

## Running it locally

```bash
git clone https://github.com/ahmadcore8737/layoffs-qa-chatbot.git
cd layoffs-qa-chatbot
python -m venv venv
venv\Scripts\activate      # Mac/Linux: source venv/bin/activate
pip install streamlit pandas matplotlib google-genai python-dotenv
```

Create a `.env` file in the project folder with your own Gemini API key:
```
GEMINI_API_KEY=your_key_here
```

Then run:
```bash
streamlit run app.py
```

## Why I built this

I'd already done a full exploratory analysis on this same layoffs dataset ([check that project out here](https://github.com/ahmadcore8737/global-layoffs-analysis)). This project takes it a step further, instead of a static analysis, anyone can now just ask the data questions directly and get answers on the spot.

## About me

I'm Ahmad, a Data Science student building out my portfolio one project at a time. Feel free to explore, fork it, or reach out.
