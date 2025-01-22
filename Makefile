build:
	docker build -t dog-breed-assistant-chatbot .

run:
	docker run -p 8501:8501 dog-breed-assistant-chatbot