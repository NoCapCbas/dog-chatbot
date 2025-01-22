import streamlit as st 
from streamlit_chat import message
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain

DB_FAISS_PATH = 'vectorstore/db_faiss'
CSV_FILE_PATH = r'dogs_cleaned.csv'  # Replace with your CSV file path
st.set_page_config(
    page_title="Dog Breed Assistant",
    page_icon="🐕",
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


#Loading the model
def load_llm():
    # Load Mistral through Ollama
    llm = Ollama(
        # model="mistral",  # Using Mistral 7B - a powerful open source model
        model="phi",
        temperature=0.5,
    )
    return llm

@st.cache_resource  # This ensures the data is loaded only once
def load_and_process_data():
    loader = CSVLoader(file_path=CSV_FILE_PATH, encoding="utf-8", csv_args={
                'delimiter': ','})
    data = loader.load()
    
    embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2',
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    db = FAISS.from_documents(data, embeddings)
    llm = load_llm()
    chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=db.as_retriever())
    return chain

st.markdown("<h1 style='text-align: center; color: white;'>🐕 Dog Breed Assistant 🦮</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>Your Friendly Guide to Dog Breeds</h3>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: red;'> This chatbot uses open source model Phi due to its smaller size and faster response time</h3>", unsafe_allow_html=True)

# Load the chain once at startup
chain = load_and_process_data()

def conversational_chat(query):
    with st.spinner('🐾 Fetching response... Thank you for your patience! 🐕'):
        # Add context about ratings to the query
        context = """In the data, ratings are on a scale where higher numbers (like 5) mean the breed performs 
        better in that category, and lower numbers (like 1) mean the breed performs worse in that category. 
        Please consider this when answering. """
        enhanced_query = context + query
        
        result = chain({"question": enhanced_query, "chat_history": st.session_state['history']})
        st.session_state['history'].append((query, result["answer"]))
        return result["answer"]

if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Woof! I'm your friendly dog breed expert! Ask me anything about dogs! 🐕"]

if 'past' not in st.session_state:
    st.session_state['past'] = ["Hey! 👋"]

# Add suggested questions
st.sidebar.markdown("### 📝 Suggested Questions")
suggested_questions = [
    "What dog breeds are best for beginners?",
    "What are some rare or unusual dog breeds?",
    "What are the largest dog breeds?",
    "Which breeds are best with children?",
    "What are the most low-maintenance dog breeds?",
    "Which breeds are best for apartment living?"
]

if st.sidebar.button("Clear Chat History"):
    st.session_state['history'] = []
    st.session_state['past'] = ["Hey! 👋"]
    st.session_state['generated'] = ["Woof! I'm your friendly dog breed expert! Ask me anything about dogs! 🐕"]

for question in suggested_questions:
    if st.sidebar.button(question):
        st.session_state['past'].append(question)
        output = conversational_chat(question)
        st.session_state['generated'].append(output)

#container for the chat history
response_container = st.container()
#container for the user's text input
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("Query:", placeholder="Ask me anything about dogs! 🐕", key='input')
        submit_button = st.form_submit_button(label='Send')
        
    if submit_button and user_input:
        output = conversational_chat(user_input)
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
                   avatar_style="bottts-neutral",  # This gives a more dog-like cartoon avatar
                   seed="Buddy")  # This helps maintain consistent avatar appearance



    


