# Shop Floor Management

Controle de processos de produção com o objetivo de melhorar constantemente os indicadores-chave de desempenho, bem como os processos que são realizados.
Inclui aba de Gestão de Produção.



[![wakatime](https://wakatime.com/badge/github/brunotomaz-dev/stm-shop-floor-management.svg)](https://wakatime.com/badge/github/brunotomaz-dev/stm-shop-floor-management)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Poetry)




## Funcionalidades

- Eficiência de Fábrica
- Performance de Linha
- Indicador de reparos
- Análise de Principais motivos de parada


## Pré-requisitos

Antes de começar, você vai precisar ter instalado em sua máquina as seguintes ferramentas:
[Git](https://git-scm.com), [Python](https://www.python.org/), usando [PIP](https://pip.pypa.io/en/stable/) ou [Poetry](https://python-poetry.org/). 

Além disto é bom ter um editor para trabalhar com o código como [VSCode](https://code.visualstudio.com/)

### 🎲 Rodando o Back End (servidor)

Clone o projeto

```bash
  git clone https://github.com/brunotomaz-dev/stm-shop-floor-management.git
```

Entre no diretório do projeto

```bash
  cd stm-shop-floor-management
```

### Opção 1:

Instale as dependências

```bash
    pip install -r ./requirements.txt
```

Inicie o servidor

```bash
  cd app
  python -u main.py
```

### Opção 2:

Instale as dependências

```bash
    poetry install
```

Inicie o servidor

```bash
  cd app
  poetry run python main.py
```

#### O servidor inciará na porta:8050 - acesse <http://localhost:8050>
## Stack utilizada

**Front-end:** Dash, Dash Bootstrap Components, Plotly

**Back-end:** Python, Pandas, Numpy

### 🛠 Tecnologias

As seguintes ferramentas foram usadas na construção do projeto:

- [Python](https://www.python.org/)
- [Poetry](https://python-poetry.org/)
- [Dash](https://dash.plotly.com/)
- [Plotly](https://plotly.com/)
- [Pandas](https://pandas.pydata.org/docs/index.html#)
- [Numpy](https://numpy.org/)

## Estrutura do app

```bash
├── app
│   ├── main.py
│   ├── app.py
│   ├── assets
│   │   ├── feriados.csv
│   │   ├── style.css
│   ├── components
│   │   ├── modal_efficiency.py
│   │   ├── modal_performance.py
│   │   ├── modal_repair.py
│   │   ├── bar_chart.py
│   │   ├── grid.py
│   │   ├── cards.py
│   ├── database
│   │   ├── connection.py
│   │   ├── db_ready.py
│   │   ├── get_data.py
│   ├── helpers
│   │   ├── cache.py
│   │   ├── path_config.py
│   │   ├── types.py
│   ├── pages
│   │   ├── main_page.py
│   |   ├── grafana.py
│   |   ├── management.py
│   ├── service
│   │   ├── clean_data.py
│   │   ├── join_data.py
│   │   ├── times_data.py
```

