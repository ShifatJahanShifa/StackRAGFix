from models.models import MistralModel, OllamaModel

ollama_model = OllamaModel()
ollama_embedding_model = ollama_model.ollama_embeddings
ollama_chat_model = ollama_model.ollama_chat

mistral_model = MistralModel()
mistral_embedding_model = mistral_model.mistral_embeddings
mistral_chat_model = mistral_model.mistral_chat
