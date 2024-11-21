
from flask import Blueprint, request, jsonify
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain_core.runnables import RunnableLambda  
#from langchain_community.llms import Runnable
#from langchain.runnables import RunnableLambda, Runnable
import torch

bp = Blueprint('chat', __name__)

#model_name = "EleutherAI/gpt-neo-2.7B"  # Modèle local de Hugging Face
model_name = "distilgpt2"

# Charger le modèle et le tokenizer avec transformers
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)


# Fonction de génération de texte
def generate_text(prompt_text):
    # Tokeniser le texte d'entrée
    inputs = tokenizer(prompt_text, return_tensors="pt")
    
    # Générer la réponse en utilisant le modèle
    outputs = model.generate(inputs["input_ids"], max_length=150, num_return_sequences=1)
    
    # Retourner la réponse générée
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Envelopper la fonction generate_text dans un "Runnable"
generate_runnable = RunnableLambda(lambda x, stop=None: generate_text(x))

template = """
Tu es un tuteur intelligent. L'étudiant demande : {question}.
Réponds de manière claire et détaillée avec des exemples pratiques.
"""
prompt = PromptTemplate(input_variables=["question"], template=template)

llm_chain = LLMChain(prompt=prompt, llm=generate_runnable)
""" my_llm = MyLLM(model, tokenizer)  # Pass the model and tokenizer to the class
llm_chain = LLMChain(prompt=prompt, llm=my_llm) """

@bp.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    print (user_input)
    if user_input:
        response = llm_chain.run(user_input)
        return jsonify({'response': response}), 200
    return jsonify({'error': 'No message provided'}), 400
