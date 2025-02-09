import json
import networkx as nx
import os
from sentence_transformers import SentenceTransformer, util

CUMULATIVE_FILE = "cumulative_data.json"

def load_cumulative_data():
    """
    Tenta carregar os dados acumulados do arquivo externo.
    Se o arquivo não existir, retorna dicionário vazio e contador zero.
    """
    try:
        with open(CUMULATIVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("cumulative_genre_totals", {}), data.get("movies_searched_count", 0)
    except FileNotFoundError:
        return {}, 0

def save_cumulative_data(cumulative_genre_totals, movies_searched_count):
    """
    Salva os dados acumulados em um arquivo JSON.
    """
    data = {
        "cumulative_genre_totals": cumulative_genre_totals,
        "movies_searched_count": movies_searched_count
    }
    with open(CUMULATIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def calcular_generos(G, tagged_full_path, titulo_filme):
    # Carrega os dados acumulados do arquivo externo
    cumulative_genre_totals, movies_searched_count = load_cumulative_data()

    if os.path.getsize(tagged_full_path) == 0:
        raise ValueError(f"The file {tagged_full_path} is empty.")
    
    with open(tagged_full_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    dialogues = [line[2:].strip() for line in lines if line.startswith('D:')]
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(dialogues, convert_to_tensor=True)
    
    existing_dialogues = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'dialogue']
    existing_embeddings = model.encode(existing_dialogues, convert_to_tensor=True) if existing_dialogues else None
    
    for i, dialogue in enumerate(dialogues):
        for j in range(i + 1, len(dialogues)):
            similarity = util.pytorch_cos_sim(embeddings[i], embeddings[j]).item()
            if similarity > 0.74:
                G.add_edge(dialogue, dialogues[j], weight=similarity, type='undirected')
        
        if existing_embeddings is not None:
            for k, existing_dialogue in enumerate(existing_dialogues):
                similarity = util.pytorch_cos_sim(embeddings[i], existing_embeddings[k]).item()
                if similarity > 0.65:
                    G.add_edge(dialogue, existing_dialogue, weight=similarity, type='undirected')
    
    for dialogue in dialogues:
        if not G.has_node(dialogue):
            G.add_node(dialogue, type='new_dialogue', id=f"new_{hash(dialogue)}")
    
    if not G.has_node(titulo_filme):
        G.add_node(titulo_filme, type='movie')
    
    for dialogue in dialogues:
        if not G.has_edge(dialogue, titulo_filme):
            G.add_edge(dialogue, titulo_filme, weight=1.0, type='undirected')
    
    # Inicializa dicionário para armazenar os valores de cada gênero para o filme atual
    genre_percentages = {genre: 0 for genre in G.nodes if G.nodes[genre].get('type') == 'genre'}
    
    # Calcula as contribuições de cada diálogo para os gêneros
    for dialogue in dialogues:
        if dialogue in G:
            total_contribution = 0
            path_details = []
            for neighbor in G.neighbors(dialogue):
                similarity = G[dialogue][neighbor].get('weight', 0)
                if similarity == 0:
                    print(f"Aresta sem peso detectada: {dialogue} -> {neighbor}")
                for genre in genre_percentages:
                    if G.has_edge(neighbor, genre):
                        genre_weight = G[neighbor][genre].get('weight', 0)
                        contribution = similarity * genre_weight
                        genre_percentages[genre] += contribution
                        total_contribution += contribution
                        path_details.append(f"{neighbor} -> {genre}: {similarity:.2f} x {genre_weight:.2f} = {contribution:.2f}")
            path_details_str = ", ".join(path_details)
            print(f"    Diálogo: {dialogue} contribuiu {total_contribution:.2f} através dos caminhos [{path_details_str}]")
    
    print("\nPorcentagens ajustadas de cada diálogo com os gêneros (filme atual):")
    for genre, percentage in genre_percentages.items():
        print(f"Gênero: {genre}, Similaridade acumulada: {percentage:.2f}")
    
    # Atualiza os dados acumulados: incrementa o contador e soma os valores do filme atual
    movies_searched_count += 1
    for genre, value in genre_percentages.items():
        cumulative_genre_totals[genre] = cumulative_genre_totals.get(genre, 0) + value

    # Calcula a média para cada gênero com base nos filmes pesquisados
    average_genres = {genre: cumulative_genre_totals[genre] / movies_searched_count
                      for genre in cumulative_genre_totals}
    
    # Calcula a comparação percentual entre o filme atual e a média acumulada
    print("\nComparação percentual entre o filme atual e a média acumulada:")
    diff_percentages = {}
    for genre, current_value in genre_percentages.items():
        avg_value = average_genres.get(genre, 0)
        if avg_value != 0:
            diff_percentage = ((current_value - avg_value) / avg_value) * 100
        else:
            diff_percentage = 0
        diff_percentages[genre] = diff_percentage
        print(f"Gênero: {genre} - Filme: {current_value:.2f}, Média: {avg_value:.2f}, Diferença: {diff_percentage:.2f}%")
    
    # Calcula a média das diferenças percentuais
    if diff_percentages:
        avg_diff = sum(diff_percentages.values()) / len(diff_percentages)
    else:
        avg_diff = 0
    print(f"\nMédia das diferenças percentuais: {avg_diff:.2f}%")
    
    # Compara cada diferença percentual com a média das diferenças
    print("\nComparação de cada diferença percentual com a média das diferenças:")
    for genre, diff_percentage in diff_percentages.items():
        if avg_diff != 0:
            relative_comparison = ((diff_percentage - avg_diff) / abs(avg_diff)) * 100
        else:
            relative_comparison = 0
        print(f"Gênero: {genre} - Diferença: {diff_percentage:.2f}% (Desvio em relação à média: {relative_comparison:.2f}%)")
    
    # Exporta o grafo atualizado para Gephi
    nx.write_gexf(G, "grafo_generos.gexf")
    print("Grafo exportado para Gephi como 'grafo_generos.gexf'.")
    
    # Salva os dados acumulados atualizados em arquivo externo
    save_cumulative_data(cumulative_genre_totals, movies_searched_count)
    
    return G
