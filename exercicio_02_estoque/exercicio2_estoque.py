"""Exercício 2 - Movimentação de estoque.

Descrição
---------
Programa de linha de comando para lançar entradas e saídas de mercadoria no
depósito. Cada movimentação registrada possui:

* um **número identificador único** (``id`` sequencial: 1, 2, 3...);
* uma **descrição** que identifica o tipo da movimentação, informada pelo
  usuário (ex.: "Compra de fornecedor", "Venda", "Devolução", "Perda").

Ao final de cada lançamento, o programa informa a **quantidade final** do
produto movimentado.

Arquivos utilizados (na mesma pasta do script)
----------------------------------------------
``estoque.json``  (entrada e saída)
    Saldo atual de cada produto. É atualizado a cada movimentação.

        {"estoque": [{"codigoProduto": 101,
                      "descricaoProduto": "Caneta Azul",
                      "estoque": 150}, ...]}

``movimentacoes.json``  (criado automaticamente na primeira movimentação)
    Histórico de todos os lançamentos, para consulta e auditoria.

        [{"id": 1, "data": "2026-10-03T19:28:32", "codigoProduto": 101,
          "tipo": "entrada", "quantidade": 50,
          "descricao": "Compra fornecedor",
          "saldoAnterior": 150, "saldoFinal": 200}, ...]

Validações realizadas
---------------------
* o produto precisa existir no estoque;
* o tipo deve ser entrada ou saída;
* a quantidade deve ser maior que zero;
* a descrição é obrigatória;
* uma saída não pode ser maior que o saldo (o estoque nunca fica negativo).

Organização do código
---------------------
O código está dividido em três camadas, o que facilita testes e reaproveitamento:

1. persistência       -> ``carregar_json`` / ``salvar_json``
2. regras de negócio  -> ``registrar_movimentacao`` e auxiliares (sem ``input``/``print``)
3. interface de texto -> ``main`` e funções de leitura/exibição


Uso programático (sem menu)
---------------------------
    estoque = carregar_json(ARQ_ESTOQUE, {"estoque": []})["estoque"]
    historico = carregar_json(ARQ_MOVIMENTACOES, [])
    mov = registrar_movimentacao(estoque, historico, 101, "entrada", 50, "Compra")
    print(mov["saldoFinal"])

Limitação conhecida
-------------------
Devido à simplicidade do desafioa, os dados são gravados em arquivos JSON, adequado
para uso individual. Para vários usuários simultâneos seria necessário um banco de
dados, que controlaria acessos concorrentes e mudanças por usuário.
"""
import json
from datetime import datetime
from pathlib import Path

# Caminhos montados a partir da pasta do script, para funcionar de qualquer
# diretório de execução.
PASTA = Path(__file__).parent
ARQ_ESTOQUE = PASTA / "estoque.json"
ARQ_MOVIMENTACOES = PASTA / "movimentacoes.json"


# =============================================================================
# 1. Persistência
# =============================================================================
def carregar_json(caminho: Path, padrao):
    """Lê um arquivo JSON, ou devolve ``padrao`` se o arquivo não existir.

    O valor padrão permite que o programa funcione na primeira execução, quando
    ``movimentacoes.json`` ainda não foi criado.

    Args:
        caminho: arquivo a ser lido.
        padrao: valor devolvido caso o arquivo não exista (ex.: ``[]``).

    Returns:
        O conteúdo do JSON já convertido para objetos Python.
    """
    if not caminho.exists():
        return padrao
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho: Path, dados) -> None:
    """Grava ``dados`` em um arquivo JSON legível (indentado, com acentos).

    Args:
        caminho: arquivo de destino (sobrescrito se já existir).
        dados: estrutura Python serializável em JSON.
    """
    with open(caminho, "w", encoding="utf-8") as f:
        # ensure_ascii=False mantém acentos legíveis ("Lápis" e não "L\u00e1pis").
        json.dump(dados, f, ensure_ascii=False, indent=2)


# =============================================================================
# 2. Regras de negócio
# =============================================================================
def buscar_produto(estoque: list[dict], codigo: int) -> dict | None:
    """Procura um produto pelo código.

    Args:
        estoque: lista de produtos carregada do ``estoque.json``.
        codigo: código do produto procurado.

    Returns:
        O dicionário do produto, ou ``None`` se não for encontrado. O
        dicionário devolvido é o próprio item da lista (não uma cópia),
        portanto alterá-lo altera o estoque em memória.
    """
    # next() devolve o primeiro item que satisfaz a condição; o segundo
    # argumento (None) é o valor devolvido quando nenhum item satisfaz.
    return next((p for p in estoque if p["codigoProduto"] == codigo), None)


def proximo_id(movimentacoes: list[dict]) -> int:
    """Gera o próximo identificador único de movimentação.

    Usa o maior id já existente + 1. Como o histórico é gravado em arquivo,
    a numeração continua de onde parou mesmo após fechar e reabrir o programa.

    Args:
        movimentacoes: histórico de movimentações já registradas.

    Returns:
        ``1`` se o histórico estiver vazio; caso contrário, maior id + 1.
    """
    return max((m["id"] for m in movimentacoes), default=0) + 1


def registrar_movimentacao(
    estoque: list[dict],
    movimentacoes: list[dict],
    codigo: int,
    tipo: str,          # "entrada" ou "saida"
    quantidade: int,
    descricao: str,
) -> dict:
    """Valida e registra uma movimentação, atualizando o saldo do produto.

    A função altera ``estoque`` e ``movimentacoes`` **em memória**; quem a
    chama é responsável por gravar os arquivos (ver ``main``). Se qualquer
    validação falhar, nada é alterado.

    Args:
        estoque: lista de produtos (será modificada).
        movimentacoes: histórico de movimentações (receberá o novo registro).
        codigo: código do produto movimentado.
        tipo: ``"entrada"`` (soma ao estoque) ou ``"saida"`` (subtrai).
        quantidade: quantidade movimentada, inteiro maior que zero.
        descricao: descrição do tipo da movimentação (ex.: "Venda").

    Returns:
        O registro criado, com ``id``, ``data``, ``saldoAnterior`` e
        ``saldoFinal`` (a quantidade final do produto).

    Raises:
        ValueError: produto inexistente, tipo inválido, quantidade não
            positiva, descrição vazia ou saldo insuficiente para a saída.
    """
    # --- Validações (todas antes de alterar qualquer dado) -------------------
    produto = buscar_produto(estoque, codigo)
    if produto is None:
        raise ValueError(f"Produto {codigo} não encontrado.")
    if tipo not in ("entrada", "saida"):
        raise ValueError("Tipo deve ser 'entrada' ou 'saida'.")
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")
    if not descricao.strip():
        raise ValueError("A descrição da movimentação é obrigatória.")

    saldo_anterior = produto["estoque"]
    if tipo == "saida" and quantidade > saldo_anterior:
        raise ValueError(
            f"Estoque insuficiente: saldo atual {saldo_anterior}, saída de {quantidade}."
        )

    # --- Atualização do saldo -------------------------------------------------
    # Entrada soma; saída subtrai (por isso o sinal negativo).
    produto["estoque"] += quantidade if tipo == "entrada" else -quantidade

    # --- Registro no histórico ------------------------------------------------
    # Guardamos saldo anterior e final para que o histórico seja auditável
    # sem precisar recalcular o estoque a partir de todas as movimentações.
    movimento = {
        "id": proximo_id(movimentacoes),
        "data": datetime.now().isoformat(timespec="seconds"),  # ex.: 2026-10-03T19:28:32
        "codigoProduto": codigo,
        "tipo": tipo,
        "quantidade": quantidade,
        "descricao": descricao.strip(),
        "saldoAnterior": saldo_anterior,
        "saldoFinal": produto["estoque"],
    }
    movimentacoes.append(movimento)
    return movimento


# =============================================================================
# 3. Interface de texto
# =============================================================================
def ler_inteiro(mensagem: str) -> int:
    """Pede um número inteiro ao usuário, repetindo até receber um valor válido.

    Args:
        mensagem: texto exibido na solicitação.

    Returns:
        O número inteiro digitado.
    """
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            # int() lança ValueError para entradas como "abc" ou "3,5".
            print("Digite um número inteiro válido.")


def listar_estoque(estoque: list[dict]) -> None:
    """Imprime uma tabela com código, descrição e saldo de cada produto."""
    # "<6" e "<30" alinham à esquerda; ">8" alinha o saldo à direita.
    print(f"\n{'Cód.':<6}{'Produto':<30}{'Estoque':>8}")
    for p in estoque:
        print(f"{p['codigoProduto']:<6}{p['descricaoProduto']:<30}{p['estoque']:>8}")


def main() -> None:
    """Executa o menu interativo até o usuário escolher sair.

    Fluxo de cada lançamento: escolher entrada/saída -> informar código,
    quantidade e descrição -> validar e registrar -> gravar arquivos -> exibir
    a quantidade final. Erros de validação são mostrados e o menu reaparece,
    sem encerrar o programa.
    """
    estoque = carregar_json(ARQ_ESTOQUE, {"estoque": []})["estoque"]
    movimentacoes = carregar_json(ARQ_MOVIMENTACOES, [])

    while True:
        listar_estoque(estoque)
        print("\n1 - Entrada   2 - Saída   0 - Sair")
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            break
        if opcao not in ("1", "2"):
            print("Opção inválida.")
            continue

        tipo = "entrada" if opcao == "1" else "saida"
        codigo = ler_inteiro("Código do produto: ")
        quantidade = ler_inteiro("Quantidade: ")
        descricao = input("Descrição da movimentação (ex.: Compra, Venda, Devolução): ")

        try:
            mov = registrar_movimentacao(
                estoque, movimentacoes, codigo, tipo, quantidade, descricao
            )
        except ValueError as erro:
            # Erro de validação: mostra o motivo e volta ao menu. Como a função
            # só altera os dados após validar tudo, nada foi modificado.
            print(f"\n⚠ {erro}")
            continue

        # Grava após CADA movimentação, para que nada se perca caso o
        # programa seja encerrado de forma inesperada.
        salvar_json(ARQ_ESTOQUE, {"estoque": estoque})
        salvar_json(ARQ_MOVIMENTACOES, movimentacoes)

        produto = buscar_produto(estoque, codigo)
        print(
            f"\n✔ Movimentação #{mov['id']} registrada ({mov['descricao']}). "
            f"Quantidade final de '{produto['descricaoProduto']}': {mov['saldoFinal']}"
        )


# Só executa o menu quando o arquivo é rodado diretamente; ao ser importado,
# as funções ficam disponíveis sem efeito colateral.
if __name__ == "__main__":
    main()