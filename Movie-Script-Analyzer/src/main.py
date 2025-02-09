import json
import networkx as nx
import random
from grafo import adicionar_nos_arestas
from graphsearch import calcular_generos
import sys
import time

# Definindo a estrutura do filme
class Filme:
    def __init__(self, nome, nota, data, dialogue, charinfo, tagged, generos):
        self.nome = nome
        self.nota = nota
        self.data = data
        self.dialogue = dialogue
        self.charinfo = charinfo
        self.tagged = tagged
        self.generos = generos

# Função para carregar e processar os dados do arquivo JSON
def carregar_filmes(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='utf-8') as file:
        dados = json.load(file)
    
    filmes = []
    for key, item in dados.items():
        filme = Filme(
            nome=item['file']['name'],
            nota=item.get('tmdb', {}).get('vote_average', 0),
            data=item.get('tmdb', {}).get('release_date', ''),
            dialogue=item.get('parsed', {}).get('dialogue', ''),
            charinfo=item.get('parsed', {}).get('charinfo', ''),
            tagged=item.get('parsed', {}).get('tagged', ''),
            generos=item.get('tmdb', {}).get('genres', [])
        )
        filmes.append(filme)
    
    return filmes

# Função para carregar o grafo inicial caso exista
def carregar_grafo_inicial(caminho_grafo):
    try:
        grafo = nx.read_gexf(caminho_grafo)
        print(f"Grafo carregado com sucesso de {caminho_grafo}.")
        return grafo
    except FileNotFoundError:
        print("Nenhum grafo inicial encontrado. Criando um novo grafo vazio.")
        return nx.Graph()

# Função para exportar o grafo
def exportar_grafo(grafo, caminho_grafo):
    try:
        nx.write_gexf(grafo, caminho_grafo)
        print(f"Grafo exportado com sucesso para {caminho_grafo}.")
    except Exception as e:
        print(f"Erro ao exportar o grafo: {e}")

# Caminhos dos arquivos
caminho_arquivo = 'scripts/metadata/clean_parsed_vote_meta.json'
caminho_grafo = 'grafo_filmes.gexf'

# Carregar o grafo inicial
grafo_completo = carregar_grafo_inicial(caminho_grafo)

# Obter os títulos já adicionados ao grafo inicial
titulos_adicionados = {n for n, data in grafo_completo.nodes(data=True) if data.get('type') == 'title'}
print("Títulos já adicionados ao grafo inicial:")
for titulo in titulos_adicionados:
    print(titulo)
print(f"Total de filmes já carregados no grafo: {len(titulos_adicionados)}")

# Carregar os filmes do arquivo JSON
filmes = carregar_filmes(caminho_arquivo)
print(f"Total de filmes disponíveis no arquivo JSON: {len(filmes)}")

# Embaralhar a lista para processar os filmes em ordem aleatória
random.shuffle(filmes)

# Permitir que o usuário defina quantos filmes serão processados (ex: 1500)
try:
    num_filmes = int(input("Quantos filmes deseja carregar? (ex: 1500): "))
except ValueError:
    print("Número inválido. Carregando todos os filmes disponíveis.")
    num_filmes = len(filmes)

# Contador de filmes processados nesta execução
filmes_processados = 0

# Processar os filmes, sem repetir os que já estão no grafo
for filme in filmes[:num_filmes]:
    if filme.nome not in titulos_adicionados:
        adicionar_nos_arestas(grafo_completo, filme.tagged, filme.nome, filme.generos)
        titulos_adicionados.add(filme.nome)
        filmes_processados += 1
        
        print(f'Nome: {filme.nome}, Nota: {filme.nota}, Data: {filme.data}')
        print(f'Dialogue: {filme.dialogue}, Charinfo: {filme.charinfo}, Tagged: {filme.tagged}')
        print(f'Generos: {filme.generos}')
        exportar_grafo(grafo_completo, caminho_grafo)

print(f"Total de filmes processados nesta execução: {filmes_processados}")

# Função para pesquisar gêneros de um filme
def pesquisar_generos(grafo_completo):
    filmesall = carregar_filmes(caminho_arquivo)
    nome_filme = input("Digite o nome do filme que deseja pesquisar: ")
    
    # Procurar o filme na lista de filmes
    filme_encontrado = next((filme for filme in filmesall if filme.nome == nome_filme), None)
    
    if not filme_encontrado:
        print("Filme não encontrado.")
        return
    
    tagged_path = f'scripts/parsed/tagged/{filme_encontrado.tagged}'
    print(f'Dialogue: {filme_encontrado.dialogue}')
    print(f'Charinfo: {filme_encontrado.charinfo}')
    print(f'Tagged: {tagged_path}')

    # Chamar a função que calcula os gêneros com base nos diálogos
    generos = calcular_generos(grafo_completo, tagged_path, nome_filme)
    
    print(f'Gêneros do filme "{nome_filme}": {filme_encontrado.generos}')

# Exportar o grafo ao final do carregamento
exportar_grafo(grafo_completo, caminho_grafo)

# Loop para pesquisa de gêneros, permitindo a pesquisa de vários filmes
while True:
    pesquisar_generos(grafo_completo)
    opcao = input("Deseja pesquisar outro filme? (s/n): ").strip().lower()
    if opcao != 's':
        break
