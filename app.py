import streamlit as st 
from streamlit_chat import message
from langchain_community.llms import Ollama
import time
import re

st.set_page_config(
    page_title="Math Assistant",
    page_icon="🔢",
)

# Hide Streamlit's default menu and footer
hide_streamlit_style = """
            <style>
            header {visibility: hidden;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def load_llm():
    # Load Phi-2 through Ollama
    llm = Ollama(
        model="phi",  # Using Phi - good balance of size and math capability
        temperature=0.1,  # Lower temperature for more precise math
    )
    return llm

def is_math_related(query):
    # List of math-related keywords and patterns
    math_keywords = [
        'math', 'calculate', 'solve', 'equation', 'problem', 'plus', 'minus',
        'multiply', 'divide', 'sum', 'difference', 'product', 'quotient',
        'algebra', 'geometry', 'trigonometry', 'calculus', 'number',
        'fraction', 'decimal', 'percentage', 'square root', 'power',
        'logarithm', 'factorial', 'series', 'sequence', 'probability',
        'statistics', 'mean', 'median', 'mode', 'variance', 'derivative',
        'integral', 'function', 'graph', 'plot', 'coordinate'
        "add", "subtract"
    ]
    
    # Mathematical symbols and patterns
    math_patterns = [
        r'[\d+\-*/^√∫∑π=]',  # Basic math operators and symbols
        r'\d+',              # Numbers
        r'[xyz]\s*=',        # Variables
        r'\b\d+\s*[\+\-\*/]\s*\d+\b',  # Basic arithmetic
        r'\b\d+\s*%',        # Percentages
        r'sqrt|sin|cos|tan|log|ln',  # Math functions
    ]
    
    query_lower = query.lower()
    
    # Check for math keywords
    if any(keyword in query_lower for keyword in math_keywords):
        return True
        
    # Check for math patterns
    if any(re.search(pattern, query) for pattern in math_patterns):
        return True
        
    return False

def conversational_chat(query):
    current_time = time.time()
    
    # Rate limit check
    if 'last_query_time' in st.session_state:
        time_since_last_query = current_time - st.session_state.last_query_time
        if time_since_last_query < 10:
            remaining_time = int(10 - time_since_last_query)
            st.error(f"Rate limit exceeded! ⏳ Please wait {remaining_time} seconds before sending another message!")
            return None

    # Check if query is math-related
    # if not is_math_related(query):
    #     return "I am a math assistant. I can only help with mathematical questions and calculations. Please ask me about math! 🔢"

    st.session_state.last_query_time = current_time

    with st.spinner('🔢 Computing... Thank you for your patience!'):
        context = """You are a math assistant. You must ONLY answer questions about mathematics.
        If the question is not about math, or about how to solve a math problem, respond with "I am a math assistant. I can only help with mathematical questions."

        Example questions:
        - What is the square root of 16?
        - How do I solve the equation 2x + 3 = 7?
        - What is the sum of 10 and 5?
        - What is the product of 3 and 4?
        - What is the difference between 10 and 5?
        
        Important rules:
        1. NEVER answer questions that are not about math
        2. Show your work step by step
        3. If unsure, say "Sorry, I don't know how to solve this problem"
        4. Use proper mathematical notation
        5. Be precise and accurate
        6. Explain concepts clearly
        7. If the question involves complex calculations, break them down
        8. Use LaTeX notation for complex mathematical expressions
        
        User Question: """
        
        enhanced_query = context + query
        llm = load_llm()
        result = llm.invoke(enhanced_query)
        return result

# Initialize session state
if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hello! I'm your math assistant. Ask me any math question! 🔢"]

if 'past' not in st.session_state:
    st.session_state['past'] = ["Hey! 👋"]

# Title and description
st.markdown("<h1 style='text-align: center; color: white;'>🔢 Math Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>Your Step-by-Step Math Problem Solver</h3>", unsafe_allow_html=True)

# Add suggested questions
st.sidebar.markdown("### 📝 Example Math Problems")
suggested_questions = [
    "What is 15% of 80?",
    "Solve the equation: 2x + 5 = 13",
    "Find the area of a circle with radius 5",
    "What is the square root of 144?",
    "Calculate 3^4",
    "Find the mean of 12, 15, 18, 21, 24"
]

if st.sidebar.button("Clear Chat History"):
    st.session_state['history'] = []
    st.session_state['past'] = ["Hey! 👋"]
    st.session_state['generated'] = ["Hello! I'm your math assistant. Ask me any math question! 🔢"]

for question in suggested_questions:
    if st.sidebar.button(question):
        st.session_state['past'].append(question)
        output = conversational_chat(question)
        if output:
            st.session_state['generated'].append(output)

# Chat interface
response_container = st.container()
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("Query:", placeholder="Enter your math question here! 🔢", key='input')
        submit_button = st.form_submit_button(label='Calculate')
        
    if submit_button and user_input:
        output = conversational_chat(user_input)
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



    


