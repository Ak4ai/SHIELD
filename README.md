# Projeto de Análise de Gêneros Cinematográficos  

Este repositório contém um sistema baseado em grafos para análise de gêneros cinematográficos, utilizando dados extraídos de roteiros de filmes e modelados com técnicas de PLN e aprendizado de máquina.  

## Link do Overleaf !

https://www.overleaf.com/7387278264vpqyvsgvfwvb#4cffcaz


## Estrutura do Workspace  

O projeto está organizado da seguinte forma:  

```
MOVIE_PROJECT/  
│── scripts/               # Scripts de pré-processamento dos dados  
│   ├── filtered/          # Arquivos filtrados após processamento inicial  
│   ├── metadata/          # Metadados associados aos filmes  
│   │   ├── clean_parsed_vote_meta.json  # Metadados processados  
│   ├── parsed/            # Arquivos processados e estruturados  
│   │   ├── tagged/        # Roteiros de filmes anotados para análise  
│   ├── unprocessed/       # Dados brutos antes do tratamento  
│  
│── src/                   # Código-fonte principal do projeto  
│   ├── __pycache__/       # Cache dos arquivos Python compilados  
│   ├── models/            # Modelos treinados e estruturas auxiliares  
│   ├── grafo.py           # Implementação da estrutura de grafos  
│   ├── graphsearch.py     # Algoritmos de busca e análise no grafo  
│   ├── main.py            # Arquivo principal para execução do sistema  
│   ├── AdicionadorGeneros.py # Script para adicionar gêneros aos grafos  
│  
│── cumulative_data.json   # Dados cumulativos para análise  
│── grafo_filmes.gexf      # Grafo de relações entre filmes  
│── grafo_generos.gexf     # Grafo de relações entre gêneros  
│── README.md              # Documentação do projeto  
│── requirements.txt       # Lista de dependências do projeto  
```

## Dependências  

Antes de executar o projeto, instale as dependências listadas no arquivo `requirements.txt` usando:  

```sh
pip install -r requirements.txt
```

## Como Executar  

Para rodar o programa, certifique-se de que os seguintes arquivos estão corretamente posicionados:  

- Os roteiros de filmes devem estar na pasta:  
  ```
  scripts/parsed/tagged/
  ```  
- O arquivo de metadados deve estar em:  
  ```
  scripts/metadata/clean_parsed_vote_meta.json
  ```  

### Execução  

Após garantir que os arquivos necessários estão no local correto, basta executar o seguinte comando:  

```sh
python src/main.py
```

## Formatos de Dados  

- **JSON (`clean_parsed_vote_meta.json`)**  
  Contém os metadados processados dos filmes.  

- **GEXF (`grafo_filmes.gexf`, `grafo_generos.gexf`)**  
  Representação dos grafos para visualização em softwares como Gephi.  

## Como Abrir o Projeto no VS Code ou Terminal

Para abrir a pasta `MOVIE_PROJECT` como root no VS Code ou terminal, siga os passos abaixo:

### No VS Code

1. Abra o VS Code.
2. Clique em `File` > `Open Folder...`.
3. Navegue até a pasta `MOVIE_PROJECT` e selecione-a.
4. O projeto será carregado no VS Code.

### No Terminal

1. Abra o terminal.
2. Navegue até a pasta `MOVIE_PROJECT` usando o comando:
    ```sh
    cd /caminho/para/MOVIE_PROJECT
    ```
3. Agora você pode executar os comandos do projeto a partir dessa pasta.

## Interagindo com o Código

Para interagir com o código, você pode definir o número de filmes a serem carregados no grafo e pesquisar por um filme específico. Veja o exemplo abaixo:

```sh
Total de filmes já carregados no grafo: 236
Total de filmes disponíveis no arquivo JSON: 1121
Quantos filmes deseja carregar? (ex: 1500): 0
Total de filmes processados nesta execução: 0
Grafo exportado com sucesso para grafo_filmes.gexf.
Digite o nome do filme que deseja pesquisar: 50-50
Dialogue: 50-50_dialogue.txt
Charinfo: 50-50_charinfo.txt
Tagged: scripts/parsed/tagged/50-50_parsed.txt

---
```
