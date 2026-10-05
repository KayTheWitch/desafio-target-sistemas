"""Exercício 1 - Cálculo de comissão por vendedor.

Descrição
---------
Lê o arquivo ``vendas.json`` (que deve estar na mesma pasta deste script),
calcula a comissão de cada venda e soma o resultado por vendedor.

Regra de comissão
-----------------
A regra é aplicada **venda a venda**, e não sobre o total de cada vendedor:

    +---------------------------+-----------+
    | Valor da venda            | Comissão  |
    +===========================+===========+
    | abaixo de R$ 100,00       | 0% (nada) |
    +---------------------------+-----------+
    | de R$ 100,00 a R$ 499,99  | 1%        |
    +---------------------------+-----------+
    | a partir de R$ 500,00     | 5%        |
    +---------------------------+-----------+

Formato esperado do arquivo de entrada
--------------------------------------
    {
      "vendas": [
        {"vendedor": "João Silva", "valor": 1200.50},
        {"vendedor": "Maria Souza", "valor": 90.75}
      ]
    }

Decisões de projeto
-------------------
* Valores monetários usam ``decimal.Decimal`` em vez de ``float``. Com float,
  somas como 0.1 + 0.2 geram resíduos (0.30000000000000004), o que não é
  aceitável em cálculos de valores financeiros.
* O arredondamento para centavos é feito **somente no final**, sobre o total
  de cada vendedor. Arredondar cada venda antes de somar acumularia erros.



Exemplo de saída esperada
----------------
    Vendedor                Comissão
    ----------------------------------
    João Silva              R$ 495,68
    Maria Souza             R$ 465,95
    Carlos Oliveira         R$ 379,37
    Ana Lima                R$ 404,98
"""
import json
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# O caminho é montado a partir da localização do próprio script (e não do
# diretório de onde o comando foi chamado), para funcionar de qualquer pasta.
ARQUIVO = Path(__file__).with_name("vendas.json")

# Precisão de duas casas decimais, usada para arredondar para centavos.
CENTAVOS = Decimal("0.01")


def calcular_comissao(valor: Decimal) -> Decimal:
    """Calcula a comissão de uma única venda.

    Args:
        valor: valor da venda, em real.

    Returns:
        Comissão devida, **sem arredondamento** (o arredondamento é feito
        depois, no valor total de cada vendedor).

    Exemplos:
        >>> calcular_comissao(Decimal("90.75"))    # abaixo de 100 -> nada
        Decimal('0')
        >>> calcular_comissao(Decimal("400.00"))   # faixa de 1%
        Decimal('4.0000')
        >>> calcular_comissao(Decimal("500.00"))   # 500 já entra na faixa de 5%
        Decimal('25.0000')
    """
    # A ordem dos testes é importante nesse cenário: cada "if" só é alcançado se o anterior
    # falhou, então não é necessário repetir o limite inferior de cada faixa.
    if valor < Decimal("100"):
        return Decimal("0")
    if valor < Decimal("500"):
        return valor * Decimal("0.01")
    return valor * Decimal("0.05")


def carregar_vendas(caminho: Path) -> list[dict]:
    """Lê o arquivo JSON e devolve a lista de vendas.

    Args:
        caminho: caminho do arquivo ``vendas.json``.

    Returns:
        Lista de dicionários no formato ``{"vendedor": str, "valor": Decimal}``.

    Raises:
        FileNotFoundError: se o arquivo não existir.
        KeyError: se o JSON não tiver a chave ``"vendas"``.
    """
    with open(caminho, encoding="utf-8") as f:
        # parse_float=Decimal faz o json converter números decimais direto
        # para Decimal, sem passar por float (que já perderia precisão).
        return json.load(f, parse_float=Decimal)["vendas"]


def comissao_por_vendedor(vendas: list[dict]) -> dict[str, Decimal]:
    """Soma as comissões de todas as vendas de cada vendedor.

    Args:
        vendas: lista de vendas, como devolvida por ``carregar_vendas``.

    Returns:
        Dicionário ``{nome_do_vendedor: comissão_total}``, com o total já
        arredondado para centavos. A ordem segue a primeira aparição de cada
        vendedor no arquivo.
    """
    # defaultdict(Decimal) inicia cada vendedor novo em Decimal() == 0,
    # evitando a checagem "if vendedor not in totais".
    totais: dict[str, Decimal] = defaultdict(Decimal)

    for venda in vendas:
        totais[venda["vendedor"]] += calcular_comissao(venda["valor"])

    # Arredondamos só aqui, no total, para não acumular erro de centavos.
    # ROUND_HALF_UP é o arredondamento "comercial" (0,005 -> 0,01).
    return {v: t.quantize(CENTAVOS, ROUND_HALF_UP) for v, t in totais.items()}


def brl(valor: Decimal) -> str:
    """Formata um valor no padrão monetário brasileiro.

    Exemplo:
        >>> brl(Decimal("1234.5"))
        'R$ 1.234,50'
    """
    # O Python formata por padrão no formato americano "1,234.50". Para inverter os
    # separadores sem que um troque pelo outro, usamos um marcador temporário:
    #   "," -> "X"   |   "." -> ","   |   "X" -> "."
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> None:
    """Executa o fluxo completo: lê as vendas, calcula e imprime a tabela."""
    comissoes = comissao_por_vendedor(carregar_vendas(ARQUIVO))

    # Cabeçalho da tabela: "<20" alinha à esquerda, ">14" alinha à direita.
    print(f"{'Vendedor':<20}{'Comissão':>14}")
    print("-" * 34)
    for vendedor, valor in comissoes.items():
        print(f"{vendedor:<20}{brl(valor):>14}")


# Só executa main() quando o arquivo é rodado diretamente; ao ser importado
# (por exemplo, em testes), as funções ficam disponíveis sem efeito colateral.
if __name__ == "__main__":
    main()