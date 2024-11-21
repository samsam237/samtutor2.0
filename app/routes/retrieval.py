# app/routes/retrieval.py

from flask import Blueprint, request, jsonify
from app  import chromadb_service
#add_books_to_chromadb, retrieve_relevant_book, get_all_books

# Créer un blueprint pour la récupération d'information
bp_retrieval = Blueprint('retrieval', __name__)

# Route pour récupérer le livre pertinent
@bp_retrieval.route('/api/retrieve', methods=['POST'])
def retrieve():
    user_query = request.json.get('message')
    if user_query:
        relevant_book = chromadb_service.retrieve_relevant_book(user_query)
        if relevant_book:
            return jsonify({'relevant_book': relevant_book}), 200
        else:
            return jsonify({'error': 'Aucun livre pertinent trouvé.'}), 404
    return jsonify({'error': 'Aucun message fourni'}), 400

# Route pour ajouter des livres (optionnel)
@bp_retrieval.route('/api/add_books', methods=['POST'])
def add_books():
    books = request.json.get('books')
    if books:
        chromadb_service.add_books_to_chromadb(books)
        return jsonify({'message': 'Livres ajoutés avec succès!'}), 200
    return jsonify({'error': 'Aucun livre fourni'}), 400

# Route pour récupérer tout les livres
@bp_retrieval.route('/api/get_books', methods=['GET'])
def get_books():
    books = chromadb_service.get_all_books()
    if(books):
        return jsonify({'books': books}), 200
    return jsonify({'books': None}), 400