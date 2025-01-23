import streamlit as st 
from streamlit_chat import message
import languagemodels as lm
import time

st.set_page_config(
    page_title="Math Buddy",
    page_icon="🔢",
)

lm.set_max_ram("512mb")

# Hide Streamlit's default menu and footer
hide_streamlit_style = """
            <style>
            header {visibility: hidden;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def check_math_question(query):
    # List of math-related keywords
    math_keywords = ['+', '-', 'x', '÷', 'plus', 'minus', 'times', 'divided', 'add', 'subtract', 'multiply', 'divide', '*', '^']
    return any(keyword in query.lower() for keyword in math_keywords)

def get_math_help(question):
    current_time = time.time()
    
    # Rate limit check
    if 'last_query_time' in st.session_state:
        time_since_last_query = current_time - st.session_state.last_query_time
        if time_since_last_query < 5:
            remaining_time = int(5 - time_since_last_query)
            st.error(f"Please wait {remaining_time} seconds before asking another question! 🔢")
            return None

    st.session_state.last_query_time = current_time

    with st.spinner('🔢 Let me think about this...'):
        # Load the math teacher context
        response = lm.do(question)
        return response

# Initialize session state
if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hi! I'm your math buddy! I can help you with +, -, ×, and ÷ problems! 🔢"]

if 'past' not in st.session_state:
    st.session_state['past'] = ["Hello! 👋"]

# Title and description
st.markdown("<h1 style='text-align: center;'>🔢 Math Buddy</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Your Friendly Math Helper</h3>", unsafe_allow_html=True)

# Add example problems
st.sidebar.markdown("### 📝 Example Math Problems")
example_problems = [
    # Basic Addition
    "What is 5 + 3?",
    # Basic Subtraction
    "What is 8 - 4?",
    # Basic Multiplication
    "What is 3 x 2?",
    # Basic Division
    "What is 6 / 2?",
]

if st.sidebar.button("Clear Chat History"):
    st.session_state['history'] = []
    st.session_state['past'] = ["Hello! 👋"]
    st.session_state['generated'] = ["Hi! I'm your math buddy! I can help you with +, -, ×, and ÷ problems! 🔢"]

for problem in example_problems:
    if st.sidebar.button(problem):
        st.session_state['past'].append(problem)
        output = get_math_help(problem)
        if output:
            st.session_state['generated'].append(output)

# Chat interface
response_container = st.container()
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("Your math question:", 
                                 placeholder="Type your question here! (e.g., What's 5 + 3?)", 
                                 key='input')
        submit_button = st.form_submit_button(label='Ask')
        
        # Show rate limit message under the input box
        current_time = time.time()
        if 'last_query_time' in st.session_state:
            time_since_last_query = current_time - st.session_state.last_query_time
            if time_since_last_query < 5:
                remaining_time = int(5 - time_since_last_query)
                st.error(f"Please wait {remaining_time} seconds before asking another question! 🔢")
        
    if submit_button and user_input:
        output = get_math_help(user_input)
        if output:
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], 
                   is_user=True, 
                   key=str(i) + '_user', 
                   avatar_style="big-smile")
            message(st.session_state["generated"][i], 
                   key=str(i), 
                   avatar_style="bottts",
                   seed="Math")

# Add floating animation CSS
st.markdown("""
    <style>
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }
    
    h1 {
        animation: float 3s ease-in-out infinite;
    }
    </style>
    """, unsafe_allow_html=True)




    


