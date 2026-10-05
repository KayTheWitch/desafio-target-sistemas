"""Testes automatizados do Exercício 3 - Juros por atraso de pagamento.

Descrição
---------
Verifica o script ``exercicio3_juros``: cálculo dos juros (2,5% ao dia,
juros simples), interpretação do valor digitado, formatação em reais e o
fluxo completo do programa.

O que é testado
---------------
    +-------------------------------+--------------------------------------------+
    | Classe de teste               | Comportamento coberto                      |
    +===============================+============================================+
    | TestCalcularJuros             | fórmula, contas em dia, arredondamento,    |
    |                               | datas especiais (bissexto, virada de ano)  |
    +-------------------------------+--------------------------------------------+
    | TestLerValor                  | formatos aceitos e entradas inválidas      |
    +-------------------------------+--------------------------------------------+
    | TestBrl                       | formatação monetária brasileira            |
    +-------------------------------+--------------------------------------------+
    | TestMain                      | fluxo completo com entrada simulada        |
    +-------------------------------+--------------------------------------------+

Estratégia de teste
-------------------
* **Data controlada:** o resultado depende de "hoje", que muda todo dia. Por
  isso os testes passam ``hoje`` explicitamente para ``calcular_juros`` ou, nos
  casos em que o código consulta o relógio do sistema, fixam a data com
  ``fixar_hoje``. Assim os testes dão o mesmo resultado em qualquer dia.
* **Valores fáceis de conferir à mão:** R$ 1.000,00 a 2,5% ao dia rende
  R$ 25,00 por dia de atraso, o que torna os resultados esperados evidentes.
* **Fronteiras:** vence hoje (0 dias), 1 dia de atraso e vencimento futuro.
* **Decimal:** comparações monetárias usam ``Decimal``, nunca ``float``.

Como executar
-------------
    python -m unittest test_exercicio3_juros -v

    # discovery dos testes deste exercício, a partir da raiz do repositório:
    python -m unittest discover -s exercicio_03_encargos -v

    # opcional, se o pytest estiver instalado:
    pytest -v

Resultado esperado
------------------
Cada teste aparece com status ``ok`` e, ao final, a mensagem ``OK``.
"""
import io
import unittest
from contextlib import redirect_stdout
from datetime import date
from decimal import Decimal as D, InvalidOperation  # D("1.50") em vez de Decimal("1.50")
from unittest import mock

import exercicio3_juros as ex3

# Data fixa usada como "hoje" nos testes que dependem do relógio do sistema.
HOJE_FIXO = date(2026, 10, 4)


def fixar_hoje(teste: unittest.TestCase, hoje: date = HOJE_FIXO) -> None:
    """Faz ``date.today()`` do módulo testado devolver sempre ``hoje``.

    A substituição vale somente durante o teste e é desfeita automaticamente
    ao final (``addCleanup``).

    Args:
        teste: o teste em execução (dono da limpeza).
        hoje: data que o programa deve enxergar como "hoje".
    """
    patcher = mock.patch.object(ex3, "date")
    mock_date = patcher.start()
    mock_date.today.return_value = hoje
    teste.addCleanup(patcher.stop)


class TestCalcularJuros(unittest.TestCase):
    """Cálculo dos juros: juros = valor x 2,5% x dias em atraso."""

    def test_quatro_dias_de_atraso(self):
        """R$ 1.000,00 com 4 dias de atraso rende R$ 100,00 (exemplo da documentação do script)."""
        juros = ex3.calcular_juros(D("1000"), date(2026, 9, 30), hoje=date(2026, 10, 4))
        self.assertEqual(juros, D("100.00"))

    def test_um_dia_de_atraso(self):
        """Limite inferior do atraso: 1 dia já gera juros (2,5% do valor)."""
        juros = ex3.calcular_juros(D("1000"), date(2026, 10, 3), hoje=date(2026, 10, 4))
        self.assertEqual(juros, D("25.00"))

    def test_conta_que_vence_hoje_nao_tem_juros(self):
        """Com 0 dias de atraso, os juros são zero."""
        juros = ex3.calcular_juros(D("1000"), date(2026, 10, 4), hoje=date(2026, 10, 4))
        self.assertEqual(juros, D("0.00"))

    def test_conta_a_vencer_nao_tem_juros(self):
        """Vencimento no futuro (dias negativos) nunca gera juros nem valor negativo."""
        juros = ex3.calcular_juros(D("1000"), date(2026, 10, 20), hoje=date(2026, 10, 4))
        self.assertEqual(juros, D("0.00"))

    def test_rejeita_valor_negativo_e_nao_finito(self):
        """Valores negativos, NaN e Infinity são rejeitados antes do cálculo."""
        for valor in (D("-100"), D("NaN"), D("Infinity")):
            with self.subTest(valor=valor):
                with self.assertRaisesRegex(ValueError, "finito e não negativo"):
                    ex3.calcular_juros(valor, date(2026, 9, 30), hoje=date(2026, 10, 4))

    def test_juros_crescem_linearmente_com_os_dias(self):
        """Juros simples: dobrar os dias dobra os juros (não há "juros sobre juros")."""
        um = ex3.calcular_juros(D("1000"), date(2026, 9, 24), hoje=date(2026, 10, 4))     # 10 dias
        dois = ex3.calcular_juros(D("1000"), date(2026, 9, 14), hoje=date(2026, 10, 4))   # 20 dias
        self.assertEqual(um, D("250.00"))
        self.assertEqual(dois, D("500.00"))
        self.assertEqual(dois, um * 2)

    def test_juros_podem_ultrapassar_o_valor_original(self):
        """Não há teto: após 40 dias os juros igualam o valor, e depois passam dele."""
        # 40 dias x 2,5% = 100% do valor; 50 dias x 2,5% = 125%.
        self.assertEqual(
            ex3.calcular_juros(D("1000"), date(2026, 8, 25), hoje=date(2026, 10, 4)),  # 40 dias
            D("1000.00"),
        )
        self.assertEqual(
            ex3.calcular_juros(D("1000"), date(2026, 8, 15), hoje=date(2026, 10, 4)),  # 50 dias
            D("1250.00"),
        )

    def test_valor_com_centavos(self):
        """Valor quebrado: 1.500,50 x 2,5% x 2 dias = 75,025 -> 75,03."""
        juros = ex3.calcular_juros(D("1500.50"), date(2026, 10, 2), hoje=date(2026, 10, 4))
        self.assertEqual(juros, D("75.03"))

    def test_arredondamento_comercial_half_up(self):
        """Metade arredonda para cima (0,005 -> 0,01), e não para o par (0,00)."""
        # 0,20 x 2,5% x 1 dia = 0,005 exato. O arredondamento "do banqueiro"
        # (ROUND_HALF_EVEN) daria 0,00; o comercial (HALF_UP) dá 0,01.
        juros = ex3.calcular_juros(D("0.20"), date(2026, 10, 3), hoje=date(2026, 10, 4))
        self.assertEqual(juros, D("0.01"))

    def test_resultado_com_duas_casas_decimais_e_tipo_decimal(self):
        """O retorno é Decimal com exatamente duas casas, inclusive quando é zero."""
        for vencimento in (date(2026, 10, 3), date(2026, 10, 4), date(2026, 10, 20)):
            with self.subTest(vencimento=vencimento):
                juros = ex3.calcular_juros(D("1000"), vencimento, hoje=date(2026, 10, 4))
                self.assertIsInstance(juros, D)
                self.assertEqual(juros.as_tuple().exponent, -2)

    def test_ano_bissexto_conta_o_dia_29_de_fevereiro(self):
        """De 28/02 a 01/03 são 2 dias em 2028 (bissexto) e 1 dia em 2027."""
        bissexto = ex3.calcular_juros(D("1000"), date(2028, 2, 28), hoje=date(2028, 3, 1))
        comum = ex3.calcular_juros(D("1000"), date(2027, 2, 28), hoje=date(2027, 3, 1))
        self.assertEqual(bissexto, D("50.00"))   # 2 dias
        self.assertEqual(comum, D("25.00"))      # 1 dia

    def test_virada_de_ano(self):
        """De 31/12 a 02/01 são 2 dias, mesmo cruzando de um ano para o outro."""
        juros = ex3.calcular_juros(D("1000"), date(2025, 12, 31), hoje=date(2026, 1, 2))
        self.assertEqual(juros, D("50.00"))

    def test_sem_informar_hoje_usa_a_data_do_sistema(self):
        """Quando ``hoje`` é omitido, a data de referência é a do relógio do sistema."""
        fixar_hoje(self)  # "hoje" passa a ser 04/10/2026
        juros = ex3.calcular_juros(D("1000"), date(2026, 9, 30))
        self.assertEqual(juros, D("100.00"))     # 4 dias


class TestLerValor(unittest.TestCase):
    """Interpretação do valor digitado pelo usuário."""

    def test_formatos_aceitos(self):
        """Formato BR, formato com ponto, com ou sem "R$" e espaços nas pontas."""
        casos = {
            "1500": "1500",
            "1500,00": "1500.00",
            "1.500,00": "1500.00",
            "1500.00": "1500.00",
            "R$ 1.500,00": "1500.00",
            "R$1.500,00": "1500.00",
            "   R$ 1.500,00   ": "1500.00",
            "0,5": "0.5",
            "1.234.567,89": "1234567.89",
        }
        for texto, esperado in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(ex3.ler_valor(texto), D(esperado))

    def test_retorna_decimal(self):
        self.assertIsInstance(ex3.ler_valor("10,50"), D)

    def test_ponto_sem_virgula_e_tratado_como_decimal(self):
        """Limitação documentada: "1.000" (sem vírgula) vale 1, e não mil."""
        # Este teste registra o comportamento atual. Se o código passar a
        # rejeitar esse formato ambíguo, o teste deve ser atualizado.
        self.assertEqual(ex3.ler_valor("1.000"), D("1"))
        self.assertEqual(ex3.ler_valor("1.000,00"), D("1000"))    # forma correta para mil

    def test_texto_invalido_gera_erro(self):
        """Entradas que não são números lançam InvalidOperation."""
        for texto in ("abc", "", "R$", "12a", "1,2,3"):
            with self.subTest(texto=texto):
                with self.assertRaises(InvalidOperation):
                    ex3.ler_valor(texto)

    def test_rejeita_valor_negativo_e_nao_finito(self):
        """O valor digitado precisa ser finito e não negativo."""
        for texto in ("-100", "NaN", "Infinity"):
            with self.subTest(texto=texto):
                with self.assertRaisesRegex(ValueError, "finito e não negativo"):
                    ex3.ler_valor(texto)


class TestBrl(unittest.TestCase):
    """Formatação de valores no padrão monetário brasileiro."""

    def test_formatos_comuns(self):
        """Ponto para milhar, vírgula para decimal, sempre com duas casas."""
        casos = {
            "0": "R$ 0,00",
            "25": "R$ 25,00",
            "999.99": "R$ 999,99",
            "1100": "R$ 1.100,00",
            "1234567.89": "R$ 1.234.567,89",
        }
        for entrada, esperado in casos.items():
            with self.subTest(valor=entrada):
                self.assertEqual(ex3.brl(D(entrada)), esperado)


class TestMain(unittest.TestCase):
    """Fluxo completo do programa: perguntas, cálculo e resultado impresso."""

    def setUp(self) -> None:
        # Todos os testes do fluxo usam a mesma data fictícia: 04/10/2026.
        fixar_hoje(self)

    def executar(self, valor: str, vencimento: str) -> str:
        """Roda ``main`` digitando ``valor`` e ``vencimento`` e devolve o que foi impresso.

        Args:
            valor: texto digitado na pergunta do valor.
            vencimento: texto digitado na pergunta do vencimento.
        """
        saida = io.StringIO()
        with mock.patch("builtins.input", side_effect=[valor, vencimento]), redirect_stdout(saida):
            ex3.main()
        return saida.getvalue()

    def test_conta_em_atraso_mostra_dias_juros_e_total(self):
        saida = self.executar("1000,00", "30/09/2026")   # 4 dias de atraso
        self.assertIn("Dias em atraso : 4", saida)
        self.assertIn("Juros          : R$ 100,00", saida)
        self.assertIn("Total a pagar  : R$ 1.100,00", saida)

    def test_conta_a_vencer_mostra_zero_dias_e_nenhum_juros(self):
        """Vencimento futuro: 0 dias (e não negativo), sem juros, total igual ao valor."""
        saida = self.executar("500,00", "10/10/2026")
        self.assertIn("Dias em atraso : 0", saida)
        self.assertIn("Juros          : R$ 0,00", saida)
        self.assertIn("Total a pagar  : R$ 500,00", saida)

    def test_valor_digitado_com_simbolo_e_milhar(self):
        saida = self.executar("R$ 1.500,00", "03/10/2026")   # 1 dia -> 2,5% de 1.500
        self.assertIn("Juros          : R$ 37,50", saida)
        self.assertIn("Total a pagar  : R$ 1.537,50", saida)

    def test_data_inexistente_gera_erro(self):
        """31/02 não existe: strptime recusa com ValueError."""
        with self.assertRaises(ValueError):
            self.executar("100,00", "31/02/2026")

    def test_data_em_formato_errado_gera_erro(self):
        """Só o formato DD/MM/AAAA é aceito."""
        for texto in ("2026-09-30", "30-09-2026", "30/09/26", ""):
            with self.subTest(data=texto):
                with self.assertRaises(ValueError):
                    self.executar("100,00", texto)

    def test_valor_invalido_gera_erro(self):
        with self.assertRaises(InvalidOperation):
            self.executar("abc", "30/09/2026")

    def test_valores_negativos_e_nao_finitos_mostram_erro_amigavel(self):
        for valor in ("-100", "NaN", "Infinity"):
            with self.subTest(valor=valor):
                saida = self.executar(valor, "30/09/2026")
                self.assertIn("Erro: O valor deve ser finito e não negativo.", saida)
                self.assertNotIn("Traceback", saida)


if __name__ == "__main__":
    unittest.main(verbosity=2)