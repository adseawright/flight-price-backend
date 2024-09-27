# Flight Price Predictor - Backend

Este é o repositório do **backend** do projeto **Flight Price Predictor**. O backend é responsável por fornecer dados para o frontend e processar as previsões de preço de passagens aéreas utilizando um modelo de machine learning.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **Flask**: Usado para construção de APIs.
- **SQLite**: Banco de dados para armazenar dados relacionados aos voos importados da base csv baixada do Kaggle.
- **scikit-learn**: Biblioteca de machine learning utilizada para treinar e fazer previsões.
- **Pandas & NumPy**: Bibliotecas para manipulação e análise de dados.

## Estrutura de Arquivos

- **`api/app.py`**:  
  Arquivo principal da aplicação Flask que define as rotas da API e conecta o frontend ao modelo de machine learning e ao banco de dados.

- **`api/MachineLearning/predict.py`**:  
  Contém o código que carrega o modelo de machine learning e faz a previsão dos preços de passagens com base nos dados de entrada do usuário.

- **`api/MachineLearning/modelo_final.pkl`**:  
  O arquivo do modelo de machine learning pré-treinado utilizado para prever o preço de passagens aéreas.

- **`scripts/init_db.py`**:  
  Script responsável por inicializar o banco de dados SQLite, criando as tabelas necessárias (companhias aéreas, cidades, rotas, etc.) e populando-as com dados.

- **`tests/test_model.py`**:  
  Contém os testes para validar as previsões do modelo de machine learning, verificando se a precisão do modelo está dentro de um intervalo aceitável.

## Rotas da API

- **`/dropdown-data`**:  
  Retorna dados para os menus suspensos, como companhias aéreas e outras opções.
  
- **`/departure-cities`** e **`/destination-cities`**:  
  Fornece uma lista de cidades de origem e destino com base nas seleções feitas.

- **`/available-stops-count`**, **`/available-durations`**, **`/available-classes`**:  
  Retorna detalhes sobre o voo, como número de paradas, durações e classes disponíveis.

- **`/predict`**:  
  Recebe os dados enviados pelo frontend (detalhes do voo) e retorna o preço previsto com base no modelo de machine learning.

