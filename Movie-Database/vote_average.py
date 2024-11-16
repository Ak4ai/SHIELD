import json
import requests

# Defina sua API Key do TMDB aqui
TMDB_API_KEY = "3fe6d185392ba999d9b62c6377636b6e"

# Função para buscar informações do filme no TMDB
def buscar_vote_average(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        dados = response.json()
        return dados.get("vote_average", None)
    else:
        print(f"Erro ao buscar o ID {tmdb_id}: {response.status_code}")
        return None

# Função principal para processar o arquivo
def processar_metadados(arquivo_entrada, arquivo_saida):
    # Ler o arquivo de metadados
    with open(arquivo_entrada, "r", encoding="utf-8") as f:
        metadados = json.load(f)
    
    # Dicionário para armazenar as notas dos filmes
    notas_filmes = {}

    # Processar cada filme no arquivo de metadados
    for chave, dados in metadados.items():
        tmdb_id = dados.get("tmdb", {}).get("id")
        if tmdb_id:
            vote_average = buscar_vote_average(tmdb_id)
            if vote_average is not None:
                notas_filmes[chave] = vote_average
                print(f"Filme: {dados['tmdb']['title']} | Nota: {vote_average}")
            else:
                print(f"Não foi possível obter a nota para o filme {dados['tmdb']['title']}")
        else:
            print(f"ID TMDB ausente para o filme com chave: {chave}")
    
    # Atualizar o arquivo de metadados com as notas
    for chave, nota in notas_filmes.items():
        metadados[chave]["tmdb"]["vote_average"] = nota
    
    # Salvar o novo arquivo com as notas
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        json.dump(metadados, f, indent=4, ensure_ascii=False)
    
    print(f"Arquivo atualizado salvo em: {arquivo_saida}")

# Nome dos arquivos de entrada e saída
arquivo_entrada = "scripts/metadata/clean_parsed_meta.json"
arquivo_saida = "scripts/metadata/clean_parsed_vote_meta.json"

# Executar o programa
processar_metadados(arquivo_entrada, arquivo_saida)
