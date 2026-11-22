# 🌦️🌾 Pipeline de Dados: Clima Mensal & Agropecuária (2023–2025)

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-4.1%2B-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Parquet](https://img.shields.io/badge/Format-Parquet%20(Snappy)-50C878?style=for-the-badge)

---

## 📖 Descrição do Projeto

Este projeto é um pipeline completo de Engenharia de Dados (ETL) construído em **Python** e **PySpark / Spark SQL** que cruza dados climáticos históricos com indicadores econômicos do setor agropecuário.

A ideia foi juntar duas fontes públicas reais — sem precisar de chaves de API — para responder a uma pergunta bem prática: *como o comportamento mensal de temperatura e chuva se relaciona com o peso da agropecuária na economia de 30 grandes países entre 2023 e 2025?*

Não foi aberto a análise para 2026 pois os resultados acerca da % do PIB ainda não foi finalizado e a API de Clima, a cada vez que se aproxima do momento atual, não computou algumas informações.

Todo o fluxo foi pensado de forma modular e limpa (`config`, `extract`, `transform`, `quality`, `load` e `main`), simulando boas práticas de produção em escala local.

---

## Estrutura do Projeto

```text
.
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── run.sh
└── src/
    ├── __init__.py
    ├── config.py
    ├── extract.py
    ├── transform.py
    ├── quality.py
    ├── load.py
    └── main.py
```

## ⚙️ Funcionalidades e Demonstração da Aplicação

O pipeline roda em **4 etapas principais** orquestradas pelo `src/main.py`:

1. **Extração resiliente (`src/extract.py`)**
   - Consulta a **World Bank API v2** para buscar o indicador `NV.AGR.TOTL.ZS` (valor adicionado da agricultura, silvicultura e pesca em `% do PIB`) com suporte a paginação automática.
   - Consulta a **Open-Meteo Historical Weather API** para coletar temperaturas médias diárias e volume de precipitação de **30 países** (`TOP_30_COUNTRIES`).
   - Conta com controle de *rate limit* e *retry* com *backoff* exponencial para lidar com instabilidades temporárias das APIs.

2. **Transformação e Cruzamento com Spark SQL (`src/transform.py`)**
   - Desaninha os vetores diários da Open-Meteo usando `LATERAL VIEW POSEXPLODE`.
   - Deduplica registros com `ROW_NUMBER()` e consolida os dados climáticos por **país, ano e mês** (média, mínima, máxima de temperatura e chuva total).
   - Cruza (`LEFT JOIN`) a base climática mensal com o indicador anual da agropecuária do World Bank.
   - Enriquecimento de dados com métricas derivadas: `amplitude_termica_c`, `agro_pct_pib_arredondado` e classificação por `faixa_temperatura` (`QUENTE`, `AMENO` ou `FRIO`).

3. **Validação de Data Quality (`src/quality.py`)**
   - Antes de salvar qualquer arquivo final, o pipeline verifica se o *schema* está íntegro, se a chave `(codigo_pais, ano, mes)` é única (sem duplicatas), se os valores estão dentro de intervalos válidos e calcula a proporção de nulos (`null_ratio`).
   - Gera automaticamente o relatório `output/data_quality_report.json` e bloqueia a gravação caso o status não seja `APROVADO`.

4. **Carga Particionada (`src/load.py`)**
   - Salva os **1.080 registros consolidados** (`30 países × 36 meses`) em formato **Parquet** com compressão **Snappy**, particionados por `ano` e `mes` em `output/pib_clima_parquet/`.

### Saída esperada no terminal

```text
[1/4] Início da Extração de dados das APIs (World Bank e Open-Meteo)...
[2/4] Processando e relacionando os dados com PySpark...
[3/4] Validações de dados - Data Quality...
-> Status: APROVADO | Total de registros: 1080
[4/4] Gravação do dataset Parquet particionado em: output/pib_clima_parquet
O Pipeline foi concluído com sucesso!
```

## 🚀 Acesso ao Projeto

Você pode clonar este repositório e rodar tudo localmente na sua máquina seguindo os passos abaixo:

### 1. Clone o repositório e acesse a pasta

```bash
git clone https://github.com/arthurviegasr/pipeline-clima-agropecuaria-pyspark.git
cd PROJETO_PYTHON
```

### 2. Configure o ambiente virtual e instale as dependências

```bash
python -m venv .venv

# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# No Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Variáveis de ambiente (opcional)

O projeto já vem com valores padrão configurados no `src/config.py`, mas se quiser personalizar datas, indicador ou pastas de saída, copie o arquivo de exemplo:

```bash
cp .env.example .env
```

### 4. Execute o pipeline

```bash
python -m src.main
```

*(Caso esteja em ambiente Linux/macOS ou Git Bash, você também pode executar `./run.sh`.)*

---

## 🛠️ Tecnologias Utilizadas

- **Python 3** — Linguagem base do pipeline
- **PySpark & Spark SQL** — Processamento distribuído, desaninhamento (`POSEXPLODE`), agregações e *joins*
- **Requests** — Consumo das APIs REST públicas (World Bank API v2 e Open-Meteo Archive API)
- **PyArrow & Pandas** — Serialização e escrita otimizada em Parquet (`Snappy`) particionado
- **Python-dotenv** — Gerenciamento de configurações via variáveis de ambiente
- **Java 17 (OpenJDK / Temurin)** — Runtime necessário para execução local do Apache Spark