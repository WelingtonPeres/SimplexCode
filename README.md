# SimplexCode

Implementação do **Método Simplex** (Uma Fase e Duas Fases) para resolução de Problemas de Programação Linear, com interface gráfica Tkinter, visualização passo a passo dos tableaus, gráfico da região viável e exportação de relatório em PDF.

## Fluxo do Algoritmo

```mermaid
flowchart TD
    A["Entrada do Problema\n(variáveis, restrições, FO, tipo)"] --> B["PPL\nConversão para forma padrão"]
    B --> B1["Max → Min: negar FO"]
    B --> B2["b &lt; 0: normalizar linha"]
    B --> B3{"Tipo da restrição"}
    B3 -->|"≤"| B4["+ folga (s)"]
    B3 -->|"≥"| B5["+ excesso (e)\n+ artificial (a)"]
    B3 -->|"="| B6["+ artificial (a)"]
    B4 --> C["Tableau Inicial"]
    B5 --> C
    B6 --> C
    C --> D{"eh_DuasEtapas?"}
    D -->|Sim| E["Fase I\nMinimizar Z' = Σ artificiais"]
    D -->|Não| H["Fase II\nMinimizar Z original"]
    E --> E1["1. Coluna pivô: 1º coef &lt; 0 em Z' (Bland)"]
    E1 --> E2["2. Linha pivô: menor razão b/a (a > 0)"]
    E2 --> E3["3. Pivotamento:\nLp ← Lp / pivô\nLi ← Li − a × Lp"]
    E3 --> E4{"Coeficientes Z' ≥ 0?"}
    E4 -->|Não| E1
    E4 -->|Sim| F{"Z'* = 0?"}
    F -->|Não| G["Problema Inviável"]
    F -->|Sim| T["Transição Fase I → II\nRemover Z', colunas artificiais\nRe-canonicalizar Z"]
    T --> H
    H --> H1["1. Coluna pivô: 1º coef &lt; 0 em Z (Bland)"]
    H1 --> H2["2. Linha pivô: menor razão b/a (a > 0)"]
    H2 --> H3{"Existe a > 0\nna coluna pivô?"}
    H3 -->|Não| I["Problema Ilimitado"]
    H3 -->|Sim| H4["3. Pivotamento"]
    H4 --> H5{"Coeficientes Z ≥ 0?"}
    H5 -->|Não| H1
    H5 -->|Sim| J["Solução Ótima\nExtrair valores das básicas\nZ* = −tableau[-1][-1]"]
```

## Instalação

```bash
# Requisitos: Python 3.11+

# Clonar o repositório
git clone <repo-url>
cd SimplexCode

# Instalar dependências
pip install matplotlib reportlab
```

## Como Usar

```bash
# Executar a aplicação
python main.py
```

1. Preencha os dados do problema na tela inicial (variáveis, restrições, função objetivo, tipo)
2. Clique em **Resolver** para executar o algoritmo
3. Navegue pelos quadros com `<<` `<` `>` `>>` para acompanhar cada iteração
4. O painel abaixo do tableau mostra o **teste da razão** e as **operações de linha**
5. Se o problema tiver 2 variáveis, o **gráfico da região viável** abre automaticamente
6. Use **Exportar PDF** para gerar um relatório completo com todas as etapas

### Executar Testes

```bash
python -m pytest test\ -v
```
