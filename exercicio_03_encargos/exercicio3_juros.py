"""Exercício 3 - Juros por atraso de pagamento.

Descrição
---------
A partir de um valor e de uma data de vencimento, calcula o valor dos juros
**na data de hoje**, considerando uma taxa de **2,5% ao dia**.

Fórmula (juros simples)
-----------------------
    juros = valor x 2,5% x dias_em_atraso

    dias_em_atraso = data_de_hoje - data_de_vencimento

* O juros incide sempre sobre o valor **original** (não sobre juros anteriores).
* Se a conta vence hoje ou ainda não venceu, os juros são zero.

Exemplo
-------
    Valor: R$ 1.000,00 | vencimento há 4 dias
    juros = 1000 x 0,025 x 4 = R$ 100,00  ->  total a pagar: R$ 1.100,00

Entradas aceitas
----------------
* Valor: ``1500,00``, ``1.500,00``, ``1500.00`` ou ``R$ 1.500,00``.
* Vencimento: sempre no formato ``DD/MM/AAAA`` (ex.: ``25/09/2026``).

Decisões de projeto
-------------------
* ``Decimal`` no lugar de ``float``, para evitar erros de arredondamento em
  valores monetários.
* ``hoje`` é um parâmetro opcional de ``calcular_juros``. Em uso normal vale a
  data do sistema, mas permite testar o cálculo com datas fixas e reproduzíveis.
* Se o cálculo desejado for de **juros compostos**, troque a fórmula em
  ``calcular_juros`` por: ``valor * ((1 + TAXA_DIARIA) ** dias_atraso - 1)``.


"""
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

# Taxa de 2,5% ao dia, escrita como fração (0,025). Declarada como constante
# no topo para que seja fácil localizar e alterar a regra.
TAXA_DIARIA = Decimal("0.025")

# Precisão de duas casas decimais, usada para arredondar para centavos.
CENTAVOS = Decimal("0.01")


def _validar_valor(valor: Decimal) -> None:
    """Rejeita valores negativos e não finitos antes de qualquer cálculo."""
    if not valor.is_finite() or valor < 0:
        raise ValueError("O valor deve ser finito e não negativo.")


def calcular_juros(valor: Decimal, vencimento: date, hoje: date | None = None) -> Decimal:
    """Calcula os juros de uma conta em atraso (juros simples).

    Args:
        valor: valor original da conta, em reais.
        vencimento: data de vencimento da conta.
        hoje: data de referência do cálculo. Se omitida, usa a data atual do
            sistema. Útil para testes com datas fixas.

    Raises:
        ValueError: se ``valor`` for negativo ou não finito.

    Returns:
        Valor dos juros, arredondado para centavos. Retorna ``0.00`` se a
        conta ainda não venceu ou vence hoje.

    Exemplos:
        >>> calcular_juros(Decimal("1000"), date(2026, 9, 26), hoje=date(2026, 9, 30))
        Decimal('100.00')
        >>> calcular_juros(Decimal("1000"), date(2026, 10, 5), hoje=date(2026, 9, 30))
        Decimal('0.00')
    """
    _validar_valor(valor)
    hoje = hoje or date.today()

    # A subtração de duas datas resulta em um timedelta; .days dá o número
    # inteiro de dias (negativo se o vencimento ainda está no futuro).
    dias_atraso = (hoje - vencimento).days

    # Sem atraso (vence hoje ou no futuro) não há juros.
    if dias_atraso <= 0:
        return Decimal("0.00")

    juros = valor * TAXA_DIARIA * dias_atraso
    # ROUND_HALF_UP é o arredondamento "comercial" (0,005 -> 0,01).
    return juros.quantize(CENTAVOS, ROUND_HALF_UP)


def ler_valor(texto: str) -> Decimal:
    """Converte o texto digitado pelo usuário em ``Decimal``.

    Aceita o formato brasileiro (``1.234,56``) e o formato com ponto decimal
    (``1234.56``), com ou sem o prefixo ``R$``.

    Regra de interpretação: se o texto contém **vírgula**, ela é tratada como
    separador decimal e os pontos como separador de milhar. Sem vírgula, o
    ponto é tratado como decimal.

    Atenção:
        Um valor como ``1.000`` (sem vírgula) é lido como 1,000 (um real), e
        não como mil. Para mil reais, digite ``1000`` ou ``1.000,00``.

    Args:
        texto: valor digitado, por exemplo ``"R$ 1.500,00"``.

    Returns:
        O valor numérico correspondente.

    Raises:
        decimal.InvalidOperation: se o texto não representar um número.
        ValueError: se o valor for negativo ou não finito.
    """
    texto = texto.strip().replace("R$", "").strip()
    if "," in texto:
        # Formato BR: remove os pontos de milhar e troca a vírgula por ponto,
        # que é o separador que o Decimal entende. "1.234,56" -> "1234.56".
        texto = texto.replace(".", "").replace(",", ".")
    valor = Decimal(texto)
    _validar_valor(valor)
    return valor


def brl(valor: Decimal) -> str:
    """Formata um valor no padrão monetário brasileiro.

    Exemplo:
        >>> brl(Decimal("1234.5"))
        'R$ 1.234,50'
    """
    # O Python formata como "1,234.50" (padrão americano). Para inverter os
    # separadores sem que um troque pelo outro, usamos um marcador temporário:
    #   "," -> "X"   |   "." -> ","   |   "X" -> "."
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> None:
    """Pede valor e vencimento e imprime dias de atraso, juros e total a pagar.

    Raises:
        ValueError: se a data não estiver no formato ``DD/MM/AAAA``.
        decimal.InvalidOperation: se o valor digitado não for um número.
    """
    try:
        valor = ler_valor(input("Valor (ex.: 1500,00): "))
    except ValueError as erro:
        print(f"\nErro: {erro}")
        return
    # strptime converte texto em data conforme o formato informado;
    # .date() descarta a parte de horário, ficando só com dia/mês/ano.
    vencimento = datetime.strptime(input("Vencimento (DD/MM/AAAA): ").strip(), "%d/%m/%Y").date()

    # max(..., 0) evita exibir "dias em atraso" negativos para contas a vencer.
    dias = max((date.today() - vencimento).days, 0)
    juros = calcular_juros(valor, vencimento)

    print(f"\nDias em atraso : {dias}")
    print(f"Juros          : {brl(juros)}")
    print(f"Total a pagar  : {brl(valor + juros)}")


# Só executa main() quando o arquivo é rodado diretamente; ao ser importado,
# as funções ficam disponíveis sem efeito colateral.
if __name__ == "__main__":
    main()