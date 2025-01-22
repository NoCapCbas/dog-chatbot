build:
	docker build -f dockerfile.prod -t math-assistant-chatbot .

run:
	docker run -p 8080:8080 math-assistant-chatbot

local:
	streamlit run app.py --server.port=8080
