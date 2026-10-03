# Desafio Target Sistemas

Repositório para desenvolver três exercícios de lógica em Python: comissão de vendas, movimentação de estoque e cálculo de encargos por atraso.

## Status

Em preparação. Este repositório contém o planejamento e a documentação inicial; as soluções ainda serão implementadas. As instruções de execução e os exemplos de uso serão adicionados junto com cada exercício.

## Exercícios

### 1. Comissão de vendas

Ler um JSON de vendas, com os campos `vendedor` e `valor`, e calcular a comissão conforme o valor de **cada venda**:

| Valor da venda | Comissão |
| --- | --- |
| Menor que R$ 100,00 | Sem comissão |
| De R$ 100,00 até menos de R$ 500,00 | 1% |
| A partir de R$ 500,00 | 5% |

**Interpretação planejada:** calcular a comissão individual de cada venda e somar as comissões por vendedor. A faixa será aplicada a cada venda, não ao total vendido pelo vendedor.

### 2. Movimentação de estoque

Partir do JSON de cinco produtos fornecido no desafio, com os campos `codigoProduto`, `descricaoProduto` e `estoque`, e permitir o registro de entradas e saídas de mercadorias.

Cada movimentação deve ter:

- Um número identificador único.
- Uma descrição que identifique o tipo da movimentação.
- O produto e a quantidade movimentada, necessários para atualizar seu saldo.

Ao concluir cada movimentação, retornar a quantidade final em estoque do produto movimentado.

**Pontos a definir durante a implementação:** validação das quantidades, tratamento de produto inexistente, saída maior que o saldo disponível e alcance da unicidade dos identificadores. Essas escolhas serão documentadas aqui, sem apresentá-las como exigências adicionais do enunciado.

### 3. Encargos por atraso

Receber um valor e uma data de vencimento e calcular o encargo na data atual, considerando a taxa de 2,5% ao dia indicada no desafio.

**Interpretação planejada:** o enunciado usa os termos "juros" e "multa" para o mesmo cálculo. A solução tratará a taxa como um único encargo diário de 2,5%, sem somar uma segunda multa.

O enunciado não define capitalização simples ou composta, contagem dos dias nem comportamento no vencimento ou antes dele. Essas regras ainda precisam ser definidas e documentadas antes da implementação, ou confirmadas com a equipe responsável pelo desafio.

## Tecnologia

Python é a linguagem escolhida para as soluções. O enunciado não exige uma linguagem, framework, banco de dados ou tipo de interface específico.

## Estrutura planejada

A árvore abaixo representa a organização proposta, não arquivos já implementados:

```text
desafio-target-sistemas/
├── README.md
├── exercicio_01_comissoes/
│   ├── main.py
│   └── vendas.json
├── exercicio_02_estoque/
│   ├── main.py
│   └── estoque.json
├── exercicio_03_encargos/
│   └── main.py
└── tests/
```

Cada exercício terá sua própria entrada de execução. Os dados de exemplo e os testes serão adicionados durante o desenvolvimento.

## Plano de desenvolvimento

- [ ] Implementar o cálculo por venda e a totalização por vendedor.
- [ ] Implementar entradas e saídas de estoque com identificação das movimentações.
- [ ] Definir as regras pendentes e implementar o cálculo de encargos.
- [ ] Adicionar testes para os limites de comissão, movimentações e datas.
- [ ] Documentar entradas, saídas, decisões e comandos de execução.

## Foco do projeto

O desenvolvimento buscará clareza na lógica, organização do código e decisões fáceis de entender. As orientações do processo citam lógica, organização, criatividade e a forma de estruturar e desenvolver as soluções como pontos de avaliação.
