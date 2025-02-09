import json
import networkx as nx
import os
import matplotlib.pyplot as plt
import spacy
from sentence_transformers import SentenceTransformer, util

def adicionar_nos_arestas(G, tagged_path, titulo, generos):
    # Verifica se o nome do filme é inválido (None ou string vazia)
    if not titulo or titulo.strip() == "":
        print(f"Nome do filme inválido ('{titulo}'). Pulando filme.")
        return G

    tagged_full_path = os.path.join('scripts', 'parsed', 'tagged', tagged_path)
    
    # Verifica se o caminho é de um arquivo existente; caso contrário, pula o filme
    if not os.path.isfile(tagged_full_path):
        print(f"Arquivo {tagged_full_path} não encontrado ou não é um arquivo. Pulando filme '{titulo}'.")
        return G

    if os.path.getsize(tagged_full_path) == 0:
        raise ValueError(f"O arquivo {tagged_full_path} está vazio.")
    
    with open(tagged_full_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    if not G.has_node(titulo):
        G.add_node(titulo, type='title')
    for genero in generos:
        if not G.has_node(genero):
            G.add_node(genero, type='genre')
        if not G.has_edge(titulo, genero):
            G.add_edge(titulo, genero, label='title_to_genre')
    
    dialogues = [line[2:].strip() for line in lines if line.startswith('D:')]
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    nlp = spacy.load("en_core_web_sm")
    
    irrelevant_keywords = [
        "hey", "hi", "hello", "yes", "no", "okay", "huh", "hmm", "bye", "thanks", "sorry", "please", 
        "What", "Who", "Where", "When", "Why", "How", "Which", "Bianca", "Cameron", "Joey", "Walter", 
        "Patrick", "Kat", "Michael", "Mandella", "Chastity", "Derek", "Sharon", "Miss Perky", 
        "Cameron", "Patrick", "Michael", "Kat", "Bianca", "Joey", "Walter", "Mandella", "Chastity", 
        "Derek", "Sharon", "Miss Perky", "What's", "Who's", "Where's", "When's", "Why's", "How's", "Which's"
    ]
    irrelevant_embeddings = model.encode(irrelevant_keywords, convert_to_tensor=True)
    
    def is_irrelevant(dialogue):
        doc = nlp(dialogue)
        words = {token.text.lower().strip("!?.,") for token in doc}
        
        # Verifica se a frase contém apenas nomes próprios
        contains_only_names = all(ent.label_ == "PERSON" for ent in doc.ents) and len(doc.ents) > 0
        
        # Verifica se a frase é composta apenas por palavras irrelevantes
        contains_only_irrelevant = words.issubset(set(irrelevant_keywords))
        
        # Verifica a similaridade com palavras irrelevantes
        dialogue_embedding = model.encode(dialogue, convert_to_tensor=True)
        max_similarity = max(util.pytorch_cos_sim(dialogue_embedding, irrelevant_embeddings).squeeze().tolist())
        
        # Verifica a similaridade com nomes próprios detectados
        name_similarities = []
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name_embedding = model.encode(ent.text, convert_to_tensor=True)
                name_similarities.append(util.pytorch_cos_sim(dialogue_embedding, name_embedding).item())
        
        name_similarity = max(name_similarities) if name_similarities else 0.0
        
        return contains_only_names or contains_only_irrelevant or max_similarity > 0.3 or name_similarity > 0.25
    
    filtered_dialogues = [dialogue for dialogue in dialogues if not is_irrelevant(dialogue)]
    
    embeddings = model.encode(filtered_dialogues, convert_to_tensor=True)
    
    existing_dialogues = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'dialogue']
    existing_embeddings = model.encode(existing_dialogues, convert_to_tensor=True) if existing_dialogues else None
    
    relevant_pairs = []
    for i, dialogue_a in enumerate(filtered_dialogues):
        for j, dialogue_b in enumerate(filtered_dialogues):
            if i < j:
                similarity = util.pytorch_cos_sim(embeddings[i], embeddings[j]).item()
                if similarity > 0.70:
                    relevant_pairs.append((dialogue_a, dialogue_b, similarity))
        
        if existing_embeddings is not None:
            for k, existing_dialogue in enumerate(existing_dialogues):
                similarity = util.pytorch_cos_sim(embeddings[i], existing_embeddings[k]).item()
                if similarity > 0.65:
                    relevant_pairs.append((dialogue_a, existing_dialogue, similarity))
    
    relevant_dialogues = set()
    dialogue_counts = {}

    for dialogue in filtered_dialogues:
        dialogue_counts[dialogue] = max(0, dialogue_counts.get(dialogue, 0))
    
    for dialogue_a, dialogue_b, similarity in relevant_pairs:
        relevant_dialogues.add(dialogue_a)
        relevant_dialogues.add(dialogue_b)
        if not G.has_edge(dialogue_a, dialogue_b):
            G.add_edge(dialogue_a, dialogue_b, weight=similarity, label='similarity')
    
    for dialogue in filtered_dialogues:
        if dialogue in relevant_dialogues:
            dialogue_counts[dialogue] += 1
    
    for dialogue in relevant_dialogues:
        if not G.has_node(dialogue):
            G.add_node(dialogue, type='dialogue')
        else:
            if G.nodes[dialogue].get('type') != 'dialogue':
                G.nodes[dialogue]['type'] = 'dialogue'
        
        if not G.has_edge(dialogue, titulo):
            G.add_edge(dialogue, titulo, label='dialogue_to_title')
        
        for genero in generos:
            if G.has_edge(dialogue, genero):
                if 'weight' not in G[dialogue][genero]:
                    G[dialogue][genero]['weight'] = 1  # Define um peso mínimo inicial
                G[dialogue][genero]['weight'] += max(1, dialogue_counts.get(dialogue, 0))
            else:
                G.add_edge(dialogue, genero, label='dialogue_to_genre', weight=max(1, dialogue_counts.get(dialogue, 0)))
    
    for u, v, data in G.edges(data=True):
        if data.get('weight', -1) >= 0:
            if G.nodes[u].get('type') == 'dialogue' and G.nodes[v].get('type') == 'genre':
                pass
            elif G.nodes[u].get('type') == 'genre' and G.nodes[v].get('type') == 'dialogue':
                pass
                
    for u, v, data in G.edges(data=True):
        if data.get('weight', -1) <= 0:
            weight = data.get('weight', -1)
            if weight <= 0:
                pass
    
    return G