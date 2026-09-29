import os
import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"timeout": 15000},  # give up after 15 seconds instead of hanging forever
)

st.set_page_config(page_title="Layoffs Bot", page_icon="📉")
st.title("Layoffs Q&A Bot")
st.caption("Ask me anything about global tech layoffs")


@st.cache_data
def load_data():
    df = pd.read_csv("layoffs.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


df = load_data()
st.sidebar.write("Rows loaded:", len(df))

# describe the data for the AI, so it knows what it's working with
SCHEMA = f"""
Columns: {list(df.columns)}
Sample rows:
{df.head(3).to_string()}
"""

SYSTEM_PROMPT = f"""You are a data assistant. A pandas DataFrame called df is
already loaded with layoffs data. Here is its shape:
{SCHEMA}

Important column notes:
- 'date' is already a real pandas datetime column, not text. To filter by
  year, use df['date'].dt.year == 2024, NOT .str methods.
- 'total_laid_off' and 'percentage_laid_off' may contain missing values
  (NaN), which pandas sum() and mean() already skip automatically.

Chart guidance:
- If a category (like country, industry, or company) has many unique
  values, do NOT plot all of them. Instead, take the top 6-8 by value and
  group everything else into a single "Other" slice/bar.
  Example for a pie chart with many categories:
  counts = df.groupby('country')['total_laid_off'].sum().sort_values(ascending=False)
  top = counts.head(6)
  other = counts[6:].sum()
  top['Other'] = other
  fig, ax = plt.subplots()
  top.plot(kind='pie', ax=ax, autopct='%1.1f%%')
  ax.set_ylabel('')
  ax.set_title('Layoffs by Country')
- Prefer bar charts over pie charts when there are more than ~5 categories,
  since bar charts stay readable with more labels than pie charts do.

You can answer in TWO possible ways:

1. If the question asks for a single fact, number, or short list (e.g. "which
   company laid off the most people?"), respond with ONLY one line of pandas
   code using df, assigning the answer to a variable named result. No
   explanation, no markdown, no backticks.
   Example: result = df['company'].value_counts().head(1)

2. If the question asks to "show", "plot", "chart", "graph", or visualize
   something, respond with a few lines of matplotlib code that builds a
   chart and stores it in a variable named fig. Use plt.subplots() to create
   it. No explanation, no markdown, no backticks.

If the question is unrelated to the layoffs data (e.g. general chit-chat,
opinions, or unrelated topics), respond with:
result = "Please ask a specific question about the layoffs data."

Decide which of the three formats fits the question, and respond with ONLY
the code, nothing else.
"""


def ask_ai_for_code(question):
    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=SYSTEM_PROMPT + "\n\nQuestion: " + question,
            )
            code = response.text.strip()
            # clean up in case the AI adds ```python fences anyway
            code = code.replace("```python", "").replace("```", "").strip()
            return code
        except Exception as e:
            last_error = e
            time.sleep(2)  # wait 2 seconds before trying again
    # if all 3 tries failed, give up cleanly instead of hanging or crashing
    raise Exception(f"AI is busy right now, please try again. ({last_error})")


def run_code_safely(code):
    # only allow df, pandas and matplotlib to be used, nothing else
    allowed = {"df": df, "pd": pd, "plt": plt}
    try:
        exec(code, {"__builtins__": {}}, allowed)
        # if the code created a chart, return that; otherwise return the result
        if "fig" in allowed:
            return allowed["fig"], None
        elif "result" in allowed:
            return allowed["result"], None
        else:
            return None, "The code ran but didn't produce a visible result."
    except Exception as e:
        return None, str(e)


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("Ask a question about the layoffs data")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                code = ask_ai_for_code(question)

            st.caption(f"Running: `{code}`")

            result, error = run_code_safely(code)

            if error:
                reply = "Hmm, I couldn't quite answer that. Try rephrasing your question, or ask something specific about the layoffs data, like a company, country, industry, or year."
                st.write(reply)
                with st.expander("Show technical details"):
                    st.code(error)
            elif hasattr(result, "savefig"):  # it's a matplotlib figure
                st.pyplot(result)
                reply = "Here's the chart you asked for."
            else:
                reply = str(result)
                st.write(reply)
        except Exception as e:
            reply = "Something went wrong on my end. Please try again in a moment."
            st.write(reply)
            with st.expander("Show technical details"):
                st.code(str(e))

        st.session_state.messages.append({"role": "assistant", "content": reply})