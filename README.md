# Desafio Target Sistemas

Repositório para desenvolver três exercícios de lógica em Python: comissão de vendas, movimentação de estoque e cálculo de encargos por atraso.

## Status

Em polimento final. Todos os módulos já foram escritos de acordo com os requisitos do desafio, qualquer mudança à partir desse ponto é só refinamento

## Exercícios

### 1. Comissão de vendas

Ler um JSON de vendas, com os campos `vendedor` e `valor`, e calcular a comissão conforme o valor de **cada venda**:

| Valor da venda | Comissão |
| --- | --- |
| Menor que R$ 100,00 | Sem comissão |
| De R$ 100,00 até menos de R$ 500,00 | 1% |
| A partir de R$ 500,00 | 5% |

**Decisão adotada:** calcular a comissão individual de cada venda e somar as comissões por vendedor. A faixa é aplicada a cada venda, não ao total vendido pelo vendedor.

### 2. Movimentação de estoque

Partir do JSON de cinco produtos fornecido no desafio, com os campos `codigoProduto`, `descricaoProduto` e `estoque`, e permitir o registro de entradas e saídas de mercadorias.

Cada movimentação deve ter:

- Um número identificador único.
- Uma descrição que identifique o tipo da movimentação.
- O produto e a quantidade movimentada, necessários para atualizar seu saldo.

Ao concluir cada movimentação, retornar a quantidade final em estoque do produto movimentado.

### 3. Encargos por atraso

Receber um valor e uma data de vencimento e calcular o encargo na data atual, considerando a taxa de 2,5% ao dia indicada no desafio.

**Decisões adotadas:** o enunciado usa os termos "juros" e "multa" para o mesmo cálculo. A solução trata a taxa como um único encargo diário de 2,5%, sem somar uma segunda multa. Os juros são simples (calculados sobre o valor original), contam dias corridos e são zero quando o vencimento é hoje ou no futuro.


## Tecnologia

Python 3.10 ou superior foi escolhido para as soluções. O enunciado não exige uma linguagem, framework, banco de dados ou tipo de interface específico, logo me dei a liberdade de escolher a linguagem que tenho mais proximidade no momento.

## Execução

Execute os scripts a partir da raiz do repositório:

```bash
python exercicio_01_comissoes/exercicio1_comissoes.py
python exercicio_02_estoque/exercicio2_estoque.py
python exercicio_03_encargos/exercicio3_juros.py
```

## Testes

Execute cada conjunto de testes a partir da raiz. O discovery é indicado por pasta:

```bash
python -m unittest discover -s exercicio_01_comissoes -v
python -m unittest discover -s exercicio_02_estoque -v
python -m unittest discover -s exercicio_03_encargos -v
```

## Estrutura planejada

A árvore abaixo representa a organização já finalizada dos arquivos:

```text
desafio-target-sistemas/
├── README.md
├── exercicio_01_comissoes/
│   ├── exercicio1_comissoes.py
│   ├── vendas.json
│   └── test_exercicio1_comissoes.py
├── exercicio_02_estoque/
│   ├── exercicio2_estoque.py
│   ├── estoque.json
│   └── test_exercicio2_estoque.py
└── exercicio_03_encargos/
    ├── exercicio3_juros.py
    └── test_exercicio3_juros.py

```

## Foco do projeto

O desenvolvimento buscará clareza na lógica, organização do código e decisões fáceis de entender. As orientações do processo citam lógica, organização, criatividade e a forma de estruturar e desenvolver as soluções como pontos de avaliação.
