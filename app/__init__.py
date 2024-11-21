from flask import Flask

# Initialisation de Flask
app = Flask(__name__)

# Importation des routes
from app.routes import chat

# Enregistrement des routes
app.register_blueprint(chat.bp)