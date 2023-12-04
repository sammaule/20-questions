"""Streamlit chat app for the frontend."""
import os
import requests

import streamlit as st
from streamlit_chat import message

intro_message = (
    "Let's play 20 questions! You think of an object and I'll try to guess it!"
)
intial_prompt = """
We are playing a game of 20 questions.
I will think of an object and you must ask me yes or no questions to try and guess what it is.
You can ask me up to 20 questions. If you guess the object before you run out of questions, you win!
If you run out of questions before you guess the object, I win! Let's play! Ask your first question.
"""

winning_message = "'Woohoo, I guessed correctly! I win!'"
losing_message = "'Boo, I didn't get it :( You win!)'"

url = "https://candidate-llm.extraction.artificialos.com/v1/chat/completions"
api_key = os.getenv("API_KEY")
headers = {"Content-Type": "application/json", "x-api-key": api_key}


def init_game():
    """Sends the initial prompt to the LLM backend and processes the response."""
    response = send_prompt()
    process_response(response)


def reset_game():
    """Resets the session state to the initial state."""
    st.session_state["question_count"] = 0
    st.session_state["messages"] = [
        {"is_user": False, "text": intro_message, "question_number": 0}
    ]
    st.session_state["prompt_messages"] = [{"role": "user", "content": intial_prompt}]


def send_prompt() -> requests.Response:
    """Sends the prompt to the LLM backend and returns the response."""
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": st.session_state.prompt_messages,
        "temperature": 0.7,
    }

    return requests.post(
        url,
        headers=headers,
        json=payload,
    )


def process_response(response: requests.Response):
    """Takes the request response adds the response message to the session state, increments the question count and updates the UI.

    Args:
        response (requests.Response): LLM response
    """
    # TODO: For now assuming the response is always 200
    assert (
        response.status_code == 200
    ), f"Response status code was {response.status_code}"

    # Update prompt messages
    response_message = response.json().get("choices")[0].get("message")
    st.session_state.prompt_messages.append(response_message)

    # Update question count
    st.session_state.question_count += 1

    # Update UI
    if st.session_state.question_count <= 20:
        text = f"{response_message.get('content')} {st.session_state['question_count']}/20 questions."
    else:
        text = f"{response_message.get('content')}"
    st.session_state.messages.append(
        {
            "is_user": False,
            "text": text,
            "question_number": st.session_state["question_count"],
        }
    )


def process_answer(answer: str):
    """Takes user answer and adds it to the session state to update the UI, sends the prompt to the LLM backend and processes.

    Args:
        answer (str): The users answer to the LLM's question
    """
    st.session_state.messages.append(
        {
            "is_user": True,
            "text": answer,
            "question_number": st.session_state["question_count"],
        }
    )

    # For questions where a specific guess was made and response was yes, let LLM know they won.
    # TODO: This does not work well as the LLM interprets "specfic guess" too broadly
    if st.session_state["question_count"] < 19 and answer == "Yes":
        answer += f". If you made a specific guess, respond with {winning_message}"

    # For questions towards the end of the game, reminds the LLM to make a guess
    if st.session_state["question_count"] == 19:
        answer += ". This is the last question that you can ask before the game is over, make a final guess."

    if st.session_state["question_count"] == 20:
        answer = (
            f"Yes. Respond with {winning_message}"
            if answer == "Yes"
            else f"No. Respond with {losing_message}"
        )

    st.session_state.prompt_messages.append({"role": "user", "content": answer})

    response = send_prompt()
    process_response(response)


# Initialize session state
if "question_count" not in st.session_state:
    st.session_state["question_count"] = 0

st.session_state.setdefault(
    "messages", [{"is_user": False, "text": intro_message, "question_number": 0}]
)

st.session_state.setdefault(
    "prompt_messages", [{"role": "user", "content": intial_prompt}]
)

# Title for the Chat
st.title("20 Questions")

chat_placeholder = st.empty()

# Chat UI
with chat_placeholder.container():
    for message_data in st.session_state.messages:
        message(
            message_data["text"],
            message_data["is_user"],
            key=f"{message_data['question_number']}_{message_data['is_user']}",
        )
        if message_data["question_number"] == 0:
            st.button("Start Game", on_click=init_game)
    st.button("Reset Game", on_click=reset_game)

# Answer buttons
with st.container():
    if message_data["question_number"] != 0 and message_data["question_number"] <= 20:
        st.button("Yes", on_click=process_answer, args=("Yes",))
        st.button("No", on_click=process_answer, args=("No",))
