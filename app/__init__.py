from flask import Flask

# Initialisation de Flask
app = Flask(__name__)

# Importation des models
from app.models import chromadb_service

# Importation des routes
from app.routes import chat, retrieval

# Enregistrement des routes
app.register_blueprint(chat.bp)
app.register_blueprint(retrieval.bp_retrieval)