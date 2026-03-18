# Caiena Teste - Weather Comment API

Integração com OpenWeatherMap e GitHub para publicar comentários com informações de tempo em Gists.

## Funcionalidades

- **SDK OpenWeatherMap**: Biblioteca para integração com a API de previsão do tempo
- **API FastAPI**: Endpoint HTTP para publicar comentários em Gists
- **Integração GitHub**: Usa PyGithub para interagir com Gists
- **Testes Automatizados**: Suite de testes com pytest
- **Docker**: Containerização da aplicação
- **Type Hints**: Tipagem completa
- **Tratamento de Erros**: Exceções customizadas

## Requisitos

- Python 3.11+
- OpenWeatherMap API key
- GitHub Personal Access Token (com permissão em Gists)
- Docker (opcional)

## Instalação Rápida

### Local

```bash
# 1. Clone e entre no diretório
git clone git@github.com:anderson9212/caiena-teste.git
cd caiena-teste

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure .env
cp .env.example .env
# Edite .env com suas chaves: OPENWEATHER_API_KEY, OPENWEATHER_API_URL e GITHUB_TOKEN

# 5. Execute
uvicorn main:app --reload
```

### Docker

```bash
# Configure .env com suas chaves
docker-compose up --build
```

A API estará em `http://localhost:8000`

## Documentação da API

A documentação interativa da API está disponível após rodar a aplicação nos seguintes endereços:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/
```

### Publicar Comentário no Gist
```bash
curl -X POST "http://localhost:8000/weather-comment/São%20Paulo"
```

## Testes

```bash
# Executar testes
pytest tests/ -v
```


## Exemplo Completo

1. Configure o arquivo `.env` com suas credenciais (`OPENWEATHER_API_KEY`, `OPENWEATHER_API_URL` e `GITHUB_TOKEN`).
2. Inicie a aplicação com o uvicorn:
```bash
uvicorn main:app --reload
```
3. Teste a criação de um comentário enviando o nome da cidade:
```bash
curl -X POST "http://localhost:8000/weather-comment/São%20Paulo"
```
4. A API automaticamente irá criar o Gist com a informação do clima. A resposta devolvida irá conter o `gist_url`. Clique no link e verifique o comentário recém-criado.

## Arquitetura e Padrões de Projeto

O projeto foi desenhado sob fortes princípios de engenharia de software para garantir testabilidade, coesão e baixo acoplamento. As principais abordagens, princípios e padrões adotados incluem:

- **Princípios SOLID:**
  - **Single Responsibility Principle (SRP):** Cada classe e módulo possui uma responsabilidade única e bem delimitada – como realizar conexões HTTP, criar comentários de clima, ou expor apenas rotas.
  - **Dependency Inversion Principle (DIP):** Dependências de infraestrutura são injetadas em serviços superiores via construtor, desacoplando a lógica core das implementações concretas dos SDKs de terceiros.

- **Conceitos de Domain-Driven Design (DDD):**
  - O design estabelece fronteiras sólidas e direcionadas entre a **Camada de Domínio/Application** (entidades, DTOs de dados de clima e validações internas) e a **Camada de Infraestrutura/Integrações externas** (adaptações puras das chamadas HTTP), isolando a lógica de negócio do transporte.

- **Data Transfer Objects (DTO):**
  - Foco na utilização de estruturas modeladas e robustas no tráfego das informações. Modelos consistem nas fronteiras do tráfego das respostas das APIs e de envios para formatações no arquivo final do Gist.

- **Arquitetura em Camadas (Layered Architecture):**
  - Existência de separações claras entre Apresentação (recebimento e validação HTTP da requisição local), Lógica de Aplicação (orquestração do serviço central) e Comunicação Externa.

- **Gateway / Adapters:**
  - O trato da comunicação com as plataformas (OpenWeather e GitHub) são isoladas em classes especializadas, que atuam como Gateway. Elas capturam erros brutos (erros e códigos HTTP) de fora, adaptando para exceções de Domínio seguras e tipadas de dentro do projeto.

## Dependências

A aplicação e testes são suportados pelas seguintes bibliotecas principais:

- **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web moderno, de alto desempenho.
- **[Uvicorn](https://www.uvicorn.org/)**: Servidor ASGI rápido.
- **[Pydantic](https://docs.pydantic.dev/) e [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)**: Validação e gerenciamento de configurações modernas baseadas em tipagem (type hints).
- **[Requests](https://requests.readthedocs.io/en/latest/)**: Cliente HTTP para uso geral.
- **[PyGithub](https://pygithub.readthedocs.io/en/latest/)**: Integração poderosa com a API REST do GitHub.
- **[python-dotenv](https://saurabh-kumar.com/python-dotenv/)**: Leitura automatizada de arquivos `.env`.
- **[pytest](https://docs.pytest.org/)**, **[pytest-cov](https://pytest-cov.readthedocs.io/)** e **[pytest-mock](https://pytest-mock.readthedocs.io/)**: Suite completo e ferramentas úteis para testes na aplicação.


## Licença

Projeto de teste técnico.
