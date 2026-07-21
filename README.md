# SimplexCode

Implementacao do **Metodo Simplex** para resolucao de Problemas de Programacao Linear (PPL), com interface grafica em Tkinter e visualizacao passo a passo dos tableaus.

## Estrutura do Projeto

```
SimplexCode/
├── main.py              # Ponto de entrada da aplicacao
├── PPL.py               # Modelagem e conversao do problema para forma padrao
├── Simplex.py           # Controlador do algoritmo Simplex (Fases I e II)
├── Tableau.py           # Representacao e operacoes sobre o tableau Simplex
├── ui/
│   ├── __init__.py
│   ├── app.py           # Janela principal (Tkinter) e navegacao entre paineis
│   ├── input_panel.py   # Formulario de entrada do PPL
│   ├── step_panel.py    # Visualizacao passo a passo dos tableaus
│   └── result_panel.py  # Exibicao da solucao otima
├── test/
│   ├── test_ppl.py      # Testes unitarios para PPL
│   └── test_tableau.py  # Testes unitarios para Tableau
└── README.md
```

## Fluxo de Execucao

### 1. Entrada do Problema (`ui/input_panel.py`)

O usuario define:
- **Numero de variaveis** de decisao (x1, x2, ..., xn)
- **Numero de restricoes**
- **Tipo do problema**: Maximizacao ou Minimizacao
- **Matriz de coeficientes** das restricoes
- **Vetor de sinais**: `<=`, `>=` ou `=`
- **Vetor b** (lado direito das restricoes)
- **Coeficientes da funcao objetivo**

### 2. Conversao para Forma Padrao (`PPL.py`)

Ao instanciar `PPL`, o problema e convertido automaticamente para a forma padrao de minimizacao:

- **Maximizacao → Minimizacao**: os coeficientes da funcao objetivo sao multiplicados por -1
- **b[i] < 0**: a linha i e multiplicada por -1 e o sinal da restricao e invertido
- **Restricao `<=`**: adiciona variavel de **folga** `s_i` (coeficiente +1)
- **Restricao `>=`**: adiciona variavel de **excesso** `e_i` (coeficiente -1) e variavel **artificial** `a_i` (coeficiente +1)
- **Restricao `=`**: adiciona variavel **artificial** `a_i` (coeficiente +1)

Se houver variaveis artificiais, o problema exige **Duas Etapas** (Metodo do M Grande / Funcao Objetivo Artificial `Z' = Σ a_i`).

### 3. Construcao do Tableau Inicial (`Tableau.py` → `Simplex.py`)

`Simplex.InicarSimpex()`:
- Cria o `Tableau` inicial a partir da `PPL` convertida
- Monta a matriz tableau: coeficientes das restricoes + coluna b, linha da funcao objetivo `Z` (e `Z'` se houver)
- Identifica as **variaveis basicas** iniciais (colunas com exatamente um `1` e demais `0`)
- **Canonicaliza** o tableau: zera os coeficientes das variaveis basicas nas linhas `Z` e `Z'`

### 4. Fase I — Viabilidade (`Simplex.py`, stage 1)

Executada apenas quando ha variaveis artificiais (`eh_DuasEtapas == True`).

Em cada iteracao:
1. **Coluna pivo**: primeira coluna com coeficiente negativo na linha `Z'` (Regra de Bland)
2. **Linha pivo**: menor razao `b[i] / coeficiente[i][coluna]` para coeficientes positivos; empates resolvidos por Bland
3. **Pivotamento** (`Tableau._realizar_pivo()`): normaliza a linha pivo e zera as demais linhas na coluna pivo
4. O novo tableau e armazenado em `tableaus_list`

A Fase I termina quando todos os coeficientes de `Z'` sao ≥ 0. Se o valor otimo de `Z'` nao for zero, o problema e **inviavel**.

### 5. Transicao Fase I → Fase II (`Tableau.transitar_para_fase_ii()`)

- Remove a linha `Z'` do tableau
- Expulsa variaveis artificiais residuais da base (pivoteamento forcado)
- Remove as colunas das variaveis artificiais
- Re-canonicaliza a linha `Z`

### 6. Fase II — Otimalidade (`Simplex.py`, stage 2)

Itera sobre o tableau da mesma forma que a Fase I, mas usando a linha `Z` original.

Criterio de parada: todos os coeficientes da linha `Z` ≥ 0 (solucao **otima** encontrada).

Se nao houver coeficiente positivo na coluna pivo em nenhuma linha de restricao, o problema e **ilimitado**.

### 7. Solucao Final (`Simplex.__extrair_solucao()`)

Extrai do tableau final:
- **Valores das variaveis**: para cada variavel basica `x_i`, o valor e `b[i]` da sua linha
- **Valor otimo de Z**: `-tableau[-1][-1]` (com correcao de sinal se houve inversao maximizacao→minimizacao)

Se o problema original era de maximizacao, o valor de Z e invertido novamente.

### 8. Visualizacao (`ui/step_panel.py` e `ui/result_panel.py`)

- **StepPanel**: exibe cada tableau da lista `tableaus_list` com navegacao (`<<`, `<`, `>`, `>>`). Destaca coluna pivo (verde), linha pivo (azul), elemento pivo (amarelo) e variaveis basicas (cinza). Mostra qual variavel entra/sai e o valor do pivo.
- **ResultPanel**: exibe a tabela final com os valores das variaveis de decisao e o valor otimo de Z.

## Diagrama de Fluxo

```
┌─────────────────┐
│  InputPanel     │  Usuario define o PPL (variaveis, restricoes,
│  (entrada)      │  sinais, b, funcao objetivo, tipo)
└────────┬────────┘
         ▼
┌─────────────────┐
│  PPL            │  Conversao para forma padrao:
│  (conversao)    │  • Maximizacao → Minimizacao
│                 │  • b[i] < 0 → normalizacao
│                 │  • Adicao de folga / excesso / artificiais
│                 │  • Define se eh Duas Etapas
└────────┬────────┘
         ▼
┌─────────────────┐
│  Tableau        │  Construcao do tableau inicial:
│  (inicial)      │  • Identificacao de variaveis basicas
│                 │  • Canonicalizacao (linhas Z e Z')
└────────┬────────┘
         ▼
   ┌───────────┐     Sim
   │ Duas Etapas? ├────────┐
   └─────┬─────┘         │
         │ Nao            ▼
         │         ┌─────────────────┐
         │         │  Fase I         │  Itera ate Z' otimo.
         │         │  (viabilidade)  │  Se Z'* ≠ 0 → Problema Inviavel
         │         └────────┬────────┘
         │                  ▼
         │         ┌─────────────────┐
         │         │  Transicao      │  Remove Z', colunas artificiais,
         │         │  Fase I → II    │  re-canonicaliza Z
         │         └────────┬────────┘
         │                  │
         ▼                  ▼
   ┌─────────────────────────────────┐
   │  Fase II                        │  Itera ate todos coef. Z ≥ 0.
   │  (otimalidade)                  │  Se coluna pivo sem coef. > 0
   │                                 │  → Problema Ilimitado
   └────────────────┬────────────────┘
                    ▼
   ┌─────────────────────────────────┐
   │  Extracao da Solucao            │  Valores das variaveis basicas,
   │                                 │  valor otimo de Z
   └────────────────┬────────────────┘
                    ▼
   ┌─────────────────────────────────┐
   │  StepPanel / ResultPanel        │  Visualizacao passo a passo
   │  (exibicao)                     │  e resultado final
   └─────────────────────────────────┘
```

## Como Executar

```bash
# Executar a interface grafica
python main.py

# Executar os testes
python -m unittest discover test -v
```

## Requisitos

- Python 3.10+
- Tkinter (incluido na instalacao padrao do Python no Windows; no Linux: `sudo apt install python3-tk`)
