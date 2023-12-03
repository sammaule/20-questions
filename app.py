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



def reset_game():
    st.session_state["question_count"] = 0
    st.session_state["messages"] = [
        {"is_user": False, "text": intro_message, "question_number": 0}
    ]
    st.session_state["prompt_messages"] = [{"role": "user", "content": intial_prompt}]


def send_prompt():
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


def init_game():
    response = send_prompt()
    process_response(response)


def process_response(response):
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


def process_answer(answer):
    st.session_state.messages.append(
        {
            "is_user": True,
            "text": answer,
            "question_number": st.session_state["question_count"],
        }
    )
    if st.session_state["question_count"] < 19 and answer == "Yes":
        answer += f". If you made a specific guess, respond with {winning_message}"

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


if "question_count" not in st.session_state:
    st.session_state["question_count"] = 0

st.session_state.setdefault(
    "messages", [{"is_user": False, "text": intro_message, "question_number": 0}]
)

st.session_state.setdefault(
    "prompt_messages", [{"role": "user", "content": intial_prompt}]
)

st.title("20 Questions")

chat_placeholder = st.empty()

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


with st.container():
    if message_data["question_number"] != 0 and message_data["question_number"] <= 20:
        st.button("Yes", on_click=process_answer, args=("Yes",))
        st.button("No", on_click=process_answer, args=("No",))
