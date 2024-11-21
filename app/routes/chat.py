
from flask import Blueprint, request, jsonify
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM
from langchain_core.runnables import RunnableLambda  
#from langchain_community.llms import Runnable
#from langchain.runnables import RunnableLambda, Runnable
import torch
import requests

bp = Blueprint('chat', __name__)

#model_name = "EleutherAI/gpt-neo-2.7B"  # Modèle local de Hugging Face
#model_name = "distilgpt2"
model_name = "facebook/bart-base"
#model_name = "gpt2-medium"
#model_name = "EleutherAI/gpt-neo-125M"
#model_name = "EleutherAI/gpt-j-6B" 
#model_name = "t5-small"

# Charger le modèle et le tokenizer avec transformers
#model = AutoModelForCausalLM.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)


# Fonction de génération de texte
def generate_text(prompt_text):
    
    # Tokeniser le texte d'entrée
    inputs = tokenizer(prompt_text.text, return_tensors="pt")
    
    # Générer la réponse en utilisant le modèle
    #outputs = model.generate(inputs["input_ids"], max_length=150, num_return_sequences=1)
    outputs = model.generate(
        inputs["input_ids"],
        max_length=1000,  # Augmenter la longueur
        num_return_sequences=1,  # Garder une seule séquence pour l'instant
        do_sample=True,  # Activer la génération échantillonnée
        top_k=50,  # Limiter les tokens choisis
        top_p=0.9,  # Somme cumulative de probabilité pour la génération
        temperature=0.9  # Température pour varier les réponses
    )

    # Retourner la réponse générée
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Envelopper la fonction generate_text dans un "Runnable"
generate_runnable = RunnableLambda(lambda x, stop=None: generate_text(x))

template = """Tu es un tuteur expert, capable d'expliquer de manière claire et pédagogique. L'étudiant te pose la question suivante : {question}.

Réponds de façon détaillée et structurée, en utilisant des exemples concrets pour rendre ta réponse plus compréhensible. Assure-toi que ton explication soit complète et adaptée au niveau de l'étudiant.

Pour appuyer ta réponse, utilise le contenu suivant : {content} afin de renforcer tes explications et d'offrir un éclairage pertinent sur la question.
"""
prompt = PromptTemplate(input_variables=["question"], template=template)

llm_chain = LLMChain(prompt=prompt, llm=generate_runnable)
""" my_llm = MyLLM(model, tokenizer)  # Pass the model and tokenizer to the class
llm_chain = LLMChain(prompt=prompt, llm=my_llm) """

@bp.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if user_input:
        # Appel du service de récupération d'information pour obtenir le livre pertinent
        response = requests.post(
            'http://localhost:5000/api/retrieve',
            json={'message': user_input}
        )
        
        if response.status_code == 200 and response.json().get('relevant_book'):
            relevant_book = response.json().get('relevant_book')
            input_data = {
                "question": user_input,
                "content": relevant_book
            }
            response = llm_chain.run(input_data)
            return jsonify({'response': response}), 200
        else:
            return jsonify({'error': 'Erreur dans la récupération de livre pertinent.'}), 400
    return jsonify({'error': 'No message provided'}), 400
