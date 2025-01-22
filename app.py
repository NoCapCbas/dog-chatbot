import streamlit as st 
import pandas as pd
from streamlit_chat import message
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
import time

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
        model="mistral",  # Using Mistral 7B - a powerful open source model
        # model="phi",
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

def is_dog_related(query):
    # List of dog-related keywords
    dog_keywords = [
        'dog', 'breed', 'puppy', 'canine', 'hound', 'terrier', 'shepherd', 
        'retriever', 'poodle', 'bulldog', 'labrador', 'german', 'golden',
        'bark', 'pet', 'training', 'grooming', 'walk', 'leash', 'collar',
        'kennel', 'veterinary', 'vet', 'pup', 'pooch', 'dog breed', 'dog breeds',
        'chew', 'bite', 'paw', 'paws', 'paw print', 'paw print', 'paw print', 'paw print',
    ]
    # read first column of csv file
    df = pd.read_csv(CSV_FILE_PATH)
    df = df.iloc[:, 0]
    # add all the values in the first column to the dog_keywords list as lowercase
    dog_keywords.extend(df.str.lower().tolist())
    # Convert query to lowercase for case-insensitive matching
    query_lower = query.lower()
    
    # Check if any dog-related keyword is in the query
    return any(keyword in query_lower for keyword in dog_keywords)

def conversational_chat(query):
    current_time = time.time()
    
    # Rate limit check
    if 'last_query_time' in st.session_state:
        time_since_last_query = current_time - st.session_state.last_query_time
        if time_since_last_query < 10:
            remaining_time = int(10 - time_since_last_query)
            st.error(f"Rate limit exceeded! ⏳ Please wait {remaining_time} seconds before sending another message! This is to prevent abuse and overload my server. This rate limit is applied to all users. Resend you query to continue and Thanks for your patience!")
            return None

    # Check if query is dog-related
    if not is_dog_related(query):
        return "I am a dog breed expert assistant. I can only answer questions about dogs and dog breeds. Please ask me about dogs! 🐕"

    st.session_state.last_query_time = current_time

    with st.spinner('🐾 Fetching response... Thank you for your patience! 🐕'):
        context = """You are a dog breed expert assistant. You must ONLY answer questions about dogs and dog breeds.
        If the question is not about dogs, respond with "I am a dog breed expert assistant. I can only answer questions about dogs and dog breeds."

        These are the columns in the data:
        Breed Name,Detailed Description Link,Dog Size,Dog Breed Group,Height,"Avg. Height, cm",Weight,"Avg. Weight, kg",Life Span,"Avg. Life Span, years",Adaptability,Adapts Well To Apartment Living,Good For Novice Owners,Sensitivity Level,Tolerates Being Alone,Tolerates Cold Weather,Tolerates Hot Weather,All Around Friendliness,Affectionate With Family,Kid-Friendly,Dog Friendly,Friendly Toward Strangers,Health And Grooming Needs,Amount Of Shedding,Drooling Potential,Easy To Groom,General Health,Potential For Weight Gain,Size,Trainability,Easy To Train,Intelligence,Potential For Mouthiness,Prey Drive,Tendency To Bark Or Howl,Wanderlust Potential,Physical Needs,Energy Level,Intensity,Exercise Needs,Potential For Playfulness

        The data contains ratings on a scale of 1-5 for columns (Adaptability, Adapts Well To Apartment Living, Good For Novice Owners, Sensitivity Level, Tolerates Being Alone, Tolerates Cold Weather, Tolerates Hot Weather, All Around Friendliness, Affectionate With Family, Kid-Friendly, Dog Friendly, Friendly Toward Strangers, Health And Grooming Needs, Amount Of Shedding, Drooling Potential, Easy To Groom, General Health, Potential For Weight Gain, Size, Trainability, Easy To Train, Intelligence, Potential For Mouthiness, Prey Drive, Tendency To Bark Or Howl, Wanderlust Potential, Physical Needs, Energy Level, Intensity, Exercise Needs, Potential For Playfulness) where:
        - 5 is the BEST/HIGHEST score (excellent)
        - 4 is ABOVE AVERAGE
        - 3 is AVERAGE
        - 2 is BELOW AVERAGE
        - 1 is the WORST/LOWEST score (poor)
        
        Important rules:
        1. NEVER answer questions that are not about dogs
        2. Do not mention the data or ratings in your response
        3. If unsure, say "Sorry, I don't know the answer to that question"
        4. Keep responses focused only on dogs and dog breeds
        5. Be friendly and helpful, but stay strictly within dog-related topics
        
        User Question: """
        
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



    


