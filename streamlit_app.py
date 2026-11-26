# Workshop edition: explanatory comments have been added.
# 1. Import the tools used by the app.
# os reads environment variables; Streamlit builds the interface;
# Groq connects to the models and provides readable error types.
import os

import streamlit as st
from groq import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    Groq,
    RateLimitError,
)
from streamlit.errors import StreamlitSecretNotFoundError


# 2. Match each menu label to its Groq model identifier.
# The label is shown to the student; the identifier is sent to Groq.
MODELS = {
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
    "Qwen 3.8 27B": "qwen/qwen3.8-27b",
}

# 3. Give the model instructions for its answers.
# These instructions encourage clear study support and honest uncertainty.
# The app has no document retrieval or web browsing tools.
SYSTEM_PROMPT = (
    "You are a helpful study assistant. Explain ideas clearly and answer "
    "the user's question directly. Admit uncertainty and do not invent "
    "references. You have no access to uploaded documents or live web "
    "search. Keep answers under 150 words unless the user requests more."
)


# 4. Look for a key configured by the person running the app.
# Check the environment first, then Streamlit Secrets. Return an empty
# string when neither is set so the sidebar can be used instead.
def configured_api_key():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if key:
        return key

    try:
        return st.secrets.get("GROQ_API_KEY", "").strip()
    except StreamlitSecretNotFoundError:
        return ""


# 5. Create a Groq client and send one question.
# A timeout limits waiting; automatic retries are turned off so a failed
# request can be shown clearly to the user.
def request_answer(api_key, model_id, history, question):
    client = Groq(api_key=api_key, timeout=60.0, max_retries=0)

    # 6. Use the reasoning settings supported by the selected model.
    # Show the final answer rather than internal reasoning text.
    if model_id.startswith("openai/gpt-oss-"):
        options = {
            "reasoning_effort": "low",
            "include_reasoning": False,
        }
    else:
        options = {
            "reasoning_effort": "default",
            "reasoning_format": "hidden",
        }

    # 7. Send the instructions, recent conversation and new question.
    # Keep the last 12 messages to limit the conversation sent each time.
    # The token limit gives the model space to produce its response.
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *history[-12:],
            {"role": "user", "content": question},
        ],
        max_completion_tokens=4096,
        **options,
    )

    # 8. Check that Groq returned a usable answer.
    # An empty response becomes a readable message in the interface.
    if not response.choices:
        raise ValueError("No answer was returned. Please try again.")

    answer = (response.choices[0].message.content or "").strip()

    if not answer:
        raise ValueError("The model returned an empty answer. Please try again.")

    return answer


# 9. Set up the page and explain what the chatbot does.
# main groups the interface and conversation logic in one place.
def main():
    st.set_page_config(
        page_title="Research and Study Assistant \u2014 Without RAG",
        page_icon="\U0001F4AC",
    )

    st.title("Research and Study Assistant \u2014 Without RAG")
    st.write("Choose a model and ask a study question.")
    st.caption(
        "Answers use the model's learned knowledge and recent conversation. "
        "No documents are uploaded or retrieved."
    )

    # 10. Put the model selector and controls in the sidebar.
    # This keeps the main area available for the conversation.
    with st.sidebar:
        st.header("Choose your LLM")
        model_name = st.selectbox("Language model", list(MODELS))

        st.caption("All three models are hosted by Groq.")
        st.caption("Changing the model starts a new conversation.")

        # 11. Allow a personal Groq key for this session.
        # The password field masks what is typed. Leave it blank when
        # a key is already configured for the deployed app.
        with st.expander("Groq API key (optional)"):
            personal_key = st.text_input(
                "Groq API key",
                type="password",
                key="personal_groq_key",
                help="Leave blank if a key is already configured for this app.",
            )

        # 12. Provide a button for starting a fresh conversation.
        clear_chat = st.button("Clear conversation")

    model_id = MODELS[model_name]

    # 13. Store messages in Streamlit session state across screen updates.
    # Reset them when the user changes model or clears the conversation.
    if st.session_state.get("active_model") != model_id or clear_chat:
        st.session_state["messages"] = []
        st.session_state["active_model"] = model_id

    # 14. Use the sidebar key when supplied; otherwise use the configured key.
    # Explain what is needed when no key is available.
    api_key = personal_key.strip() or configured_api_key()

    if not api_key:
        st.info(
            "Add GROQ_API_KEY to the app's Secrets, or enter your key "
            "in the sidebar to test this preview."
        )

    # 15. Draw the saved conversation each time Streamlit runs the script.
    # The role determines whether a message appears as user or assistant.
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 16. Create the message box and limit the length of each question.
    # Keep it disabled until a key is available and while submitting.
    question = st.chat_input(
        "Ask a study question",
        max_chars=4000,
        disabled=not bool(api_key),
        submit_mode="disable",
    )

    # 17. Remove extra spaces and reject a question containing only spaces.
    # Display a valid question immediately so the user can see it was sent.
    if question:
        question = question.strip()

        if not question:
            st.warning("Please enter a question.")
            st.stop()

        with st.chat_message("user"):
            st.markdown(question)

        # 18. Show a waiting message while the chosen model answers.
        # Send the selected model and this session's conversation.
        with st.chat_message("assistant"):
            try:
                with st.spinner(f"{model_name} is answering..."):
                    answer = request_answer(
                        api_key,
                        model_id,
                        st.session_state["messages"],
                        question,
                    )

            # 19. Translate common API failures into readable messages.
            # This avoids exposing a technical error page to the user.
            except AuthenticationError:
                st.error("The Groq API key was not accepted. Check the key.")

            except RateLimitError:
                st.warning(
                    "Groq's usage limit was reached. Please try again later."
                )

            except APITimeoutError:
                st.warning("The request timed out. Please try again.")

            except APIConnectionError:
                st.error("Could not connect to Groq. Please try again.")

            except APIError:
                st.error(
                    "Groq could not complete the request. "
                    "Try again or choose another model."
                )

            except ValueError as error:
                st.warning(str(error))

            # 20. Display and save the question and successful answer.
            # They will be included when the user asks a follow-up question.
            else:
                st.markdown(answer)
                st.session_state["messages"].extend([
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer},
                ])


# 21. Start the app when Streamlit executes this Python file.
if __name__ == "__main__":
    main()
