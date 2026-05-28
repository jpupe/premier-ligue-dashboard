# Premier League Analytics Dashboard

Plataforma interativa de análise estatística e scouting da Premier League (2014–2024), construída com Streamlit, Plotly, DuckDB e scikit-learn.

## Funcionalidades

### Páginas

| Página | Descrição |
|--------|-----------|
| **Home** | Tabela da liga, KPIs da temporada, top marcadores e gráficos históricos |
| **Players** | Comparação entre jogadores, radar de percentis, histórico de carreira |
| **Teams** | Tabela completa, TDI, comparação visual de times, heatmaps |
| **Scores** | Rankings PPS e TDI com gauges, evolução temporal e metodologia |
| **Advanced** | Similar player finder, clustering K-Means + PCA, análise de percentis |

### Scores

**Player Performance Score (PPS)**
- Normalização por percentil dentro de posição e temporada
- Pesos específicos por posição (FW, MF, DF, GK)
- Escala 0–100 com interpretação qualitativa

**Team Dominance Index (TDI)**
- 4 componentes: Ataque, Defesa, Controle, Resultados
- Normalização por percentil por temporada
- Decompõe o desempenho em dimensões independentes

### Analytics Avançado

- **Similar Player Finder**: Cosine Similarity sobre métricas per-90 normalizadas
- **Clustering**: K-Means (k=5) com visualização PCA 2D e rótulos por perfil
- **Percentis**: Barras visuais + radar + evolução histórica por temporada

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/premier-league-dashboard.git
cd premier-league-dashboard

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar
streamlit run app.py
```

O dashboard abre em `http://localhost:8501`.

## Estrutura do Projeto

```
premier-league-dashboard/
├── app.py                          # Página inicial (Home)
├── pages/
│   ├── 1_🏃_Players.py            # Análise de jogadores
│   ├── 2_🏆_Teams.py              # Análise de times
│   ├── 3_⭐_Scores.py             # PPS & TDI
│   └── 4_🔬_Advanced.py           # Analytics avançado
├── src/
│   ├── data/
│   │   ├── generator.py           # Gerador de dados sintéticos
│   │   ├── loader.py              # Cache Streamlit + DuckDB
│   │   └── processor.py          # Filtros e transformações
│   ├── metrics/
│   │   ├── player_metrics.py      # Métricas de jogadores
│   │   ├── team_metrics.py        # Métricas de times
│   │   └── scores.py             # Cálculo PPS e TDI
│   ├── visualizations/
│   │   ├── charts.py              # Factory de gráficos Plotly
│   │   └── styles.py             # CSS e tema dark
│   └── utils/
│       ├── constants.py           # Constantes globais
│       └── helpers.py            # Utilitários
├── data/                          # Pasta para CSVs reais (opcional)
├── .streamlit/config.toml         # Configuração do tema
└── requirements.txt
```

## Dados

Por padrão, o dashboard usa dados sintéticos gerados com padrões estatísticos reais da Premier League. Jogadores em destaque (Salah, Kane, Haaland, De Bruyne, etc.) possuem perfis de carreira historicamente embasados.

### Usar Dados Reais

1. Baixe os datasets do [FBref](https://fbref.com) ou [Kaggle](https://www.kaggle.com/search?q=premier+league+stats)
2. Coloque os CSVs na pasta `data/`
3. Adapte `src/data/loader.py` para ler os arquivos CSV ao invés de chamar o gerador

## Tecnologias

| Lib | Uso |
|-----|-----|
| **Streamlit** | Framework web e multipage |
| **Plotly** | Radar, scatter, heatmap, gauge, barras |
| **DuckDB** | Queries analíticas eficientes sobre DataFrames |
| **scikit-learn** | K-Means, PCA, StandardScaler, Cosine Similarity |
| **pandas / numpy** | Manipulação de dados |

## Deploy

### Streamlit Community Cloud

1. Fork este repositório no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositório e configure `app.py` como entry point

### Heroku / Railway / Render

```bash
# Procfile
web: streamlit run app.py --server.port=$PORT --server.headless=true
```

## Licença

MIT
