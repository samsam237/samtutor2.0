# app/models/chromadb_service.py

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Initialisation du modèle d'embeddings (Sentence-BERT)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Créer un client Chromadb et une collection
""" client = chromadb.Client( 
    persist_directory="db/"
) """
client = chromadb.PersistentClient(path="./db")

# Créer une collection pour les livres (si elle n'existe pas déjà)
collection_name = "books_collection"
try:
    collection = client.get_collection(collection_name)
except chromadb.errors.CollectionNotFoundError:
    collection = client.create_collection(collection_name)
#collection = client.create_collection(name=collection_name)

def add_books_to_chromadb(books):
    """
    Ajoute des livres à la base de données Chromadb.
    :param books: Liste de dictionnaires, chaque dictionnaire contient un 'title' et 'content' d'un livre.
    """
    for book in books:
        # Encoder le texte du livre
        embedding = model.encode(book["content"])
        
        # Ajouter le livre à la collection Chromadb
        collection.add(
            documents=[book["content"]],
            metadatas=[{"title": book["title"]}],
            embeddings=[embedding],
            ids = [book["title"]]
        )
        #print(f"Ajouté : {book['title']}")

def retrieve_relevant_book(query):
    """
    Récupère un livre pertinent à partir d'une requête de l'utilisateur.
    :param query: La requête de l'utilisateur (texte).
    :return: Le contenu du livre pertinent ou None si aucun livre n'est trouvé.
    """
    # Encoder la requête de l'utilisateur
    query_embedding = model.encode(query)
    
    # Rechercher le livre le plus pertinent en fonction de l'embeddding de la requête
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1  # Récupérer seulement le livre le plus pertinent
    )
    
    # Retourner le contenu du livre si trouvé
    if results["documents"]:
        return results["documents"][0]
    else:
        return None

def get_all_books():
    """
    Récupère tous les livres dans la base de données Chromadb.
    :return: Liste des livres (contenu + titre).
    """
    results = collection.get()
    #print("Results:", results)
    return [{"title": results["ids"][i], "content": results["documents"][i]} for i in range(len(results["documents"]))]
