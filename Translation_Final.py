import re
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()
#hello
# Initialize session states
if 'used_words' not in st.session_state:
    st.session_state.used_words = []
    
if 'exercise_question' not in st.session_state:
    st.session_state.exercise_question = ''
    
if 'translated_word' not in st.session_state:
    st.session_state.translated_word = ''

# Function to generate a new exercise question
def generate_exercise():
    used_words_str = ", ".join(st.session_state.used_words)
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a Sanskrit teacher."},
            {
                "role": "user",
                "content": f"""Generate one sanskrit word, its transliteration, and the word's english translation using one word.
                The word should NOT be any of these previously used words: [{used_words_str}].
                Print in this format: Word - Transliteration - Translation """
            }
        ],
        temperature=1.2
    )
    response = completion.choices[0].message.content
    
    completion_1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a Sanskrit teacher. Format your responses in two parts:
                1. The exercise for the user (between <EXERCISE> tags)
                2. The correct answer (between <ANSWER> tags)
                Keep the format consistent and clean."""
            },
            {
                "role": "user",
                "content": f"""Using this Sanskrit word data: {response}
                Create an exercise following this exact format:
                <EXERCISE>
                Instructions: Translate this Sanskrit word into English.
                Sanskrit Word: [Word] ([Transliteration])
                </EXERCISE>
                <ANSWER>
                [Translation]
                </ANSWER>"""
            }
        ],
        temperature=0.7
    )
    response_1 = completion_1.choices[0].message.content
    
    # Extract exercise and answer
    exercise = response_1.split('<EXERCISE>')[1].split('</EXERCISE>')[0].strip()
    answer = response_1.split('<ANSWER>')[1].split('</ANSWER>')[0].strip().lower()
    
    # Store the response in used words
    st.session_state.used_words.append(response)
    
    # Store the question and translated word in session state
    st.session_state.exercise_question = exercise
    st.session_state.translated_word = answer
    print(answer)
    
    return exercise, answer

# Function to handle next question
def next_question():
    generate_exercise()
    st.session_state.text_input_key += 1

# Generate first exercise if needed
if not st.session_state.exercise_question:
    generate_exercise()

# Display the current exercise question
st.write(st.session_state.exercise_question)

# Initialize the text input's key in session state if it doesn't exist
if 'text_input_key' not in st.session_state:
    st.session_state.text_input_key = 0

# User input for their answer
user_response = st.text_input(
    "Your Response:",
    key=f"text_input_{st.session_state.text_input_key}"
).lower()

# Check if there's input and Enter was pressed
if user_response:
    if user_response == st.session_state.translated_word:
        st.write("That's the correct answer!")
        # Only increment the key (clear the input) when the answer is correct
        st.session_state.text_input_key += 1
    else:
        st.write("That's not correct. Try again!")

# Button for moving to the next question
if st.button("Next Question", on_click=next_question):
    pass
