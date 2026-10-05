"""Testes automatizados do Exercício 1 - Cálculo de comissão por vendedor.

Descrição
---------
Verifica o script ``exercicio1_comissoes`` (regra de comissão, leitura do
JSON, agrupamento por vendedor, formatação em reais e saída do programa).

O que é testado
---------------
    +-------------------------------+--------------------------------------------+
    | Classe de teste               | Comportamento coberto                      |
    +===============================+============================================+
    | TestCalcularComissao          | faixas de 0%, 1% e 5% e seus limites       |
    +-------------------------------+--------------------------------------------+
    | TestCarregarVendas            | leitura do JSON, tipo Decimal, erros       |
    +-------------------------------+--------------------------------------------+
    | TestComissaoPorVendedor       | soma por vendedor, regra por venda,        |
    |                               | arredondamento no total                    |
    +-------------------------------+--------------------------------------------+
    | TestBrl                       | formatação monetária brasileira            |
    +-------------------------------+--------------------------------------------+
    | TestMain                      | tabela impressa pelo programa              |
    +-------------------------------+--------------------------------------------+
    | TestArquivoRealDoDesafio      | resultado final com o vendas.json real     |
    +-------------------------------+--------------------------------------------+

Estratégia de teste
-------------------
* **Valores de fronteira:** os limites de cada faixa (99,99 / 100,00 e
  499,99 / 500,00) são onde erros de ``<`` versus ``<=`` aparecem, então são
  testados explicitamente.
* **Isolamento:** testes que precisam de arquivo usam uma pasta temporária,
  apagada ao final. Nenhum teste altera os arquivos do projeto.
* **Decimal:** todas as comparações monetárias usam ``Decimal``, nunca
  ``float``, pelo mesmo motivo do código testado.
* **Integração:** um teste final usa o ``vendas.json`` real e confere o
  resultado completo do desafio.

Como executar
-------------
    python -m unittest test_exercicio1_comissoes -v

    # todos os testes do projeto de uma vez:
    python -m unittest discover -v

    # opcional, se o pytest estiver instalado:
    pytest -v

Resultado esperado
------------------
Cada teste aparece com status ``ok`` e, ao final, a mensagem ``OK``.
"""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from decimal import Decimal as D  # atalho: D("1.50") em vez de Decimal("1.50")
from pathlib import Path

import exercicio1_comissoes as ex1


def escrever_vendas(pasta: Path, vendas: list[dict]) -> Path:
    """Cria um ``vendas.json`` temporário com as vendas informadas.

    Args:
        pasta: pasta onde o arquivo será criado.
        vendas: lista no formato ``{"vendedor": str, "valor": número}``.

    Returns:
        Caminho do arquivo criado.
    """
    caminho = pasta / "vendas.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump({"vendas": vendas}, f, ensure_ascii=False)
    return caminho


class ComPastaTemporaria(unittest.TestCase):
    """Base para testes que precisam de arquivos: cria e limpa uma pasta temporária."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        # addCleanup garante a limpeza mesmo se o teste falhar no meio.
        self.addCleanup(self.tmp.cleanup)
        self.pasta = Path(self.tmp.name)


class TestCalcularComissao(unittest.TestCase):
    """Regra de comissão aplicada a uma única venda."""

    def test_venda_abaixo_de_100_nao_gera_comissao(self):
        """Vendas menores que R$ 100,00 não geram comissão."""
        for valor in ("0.00", "0.01", "75.30", "99.99"):
            with self.subTest(valor=valor):
                self.assertEqual(ex1.calcular_comissao(D(valor)), D("0"))

    def test_venda_de_100_a_499_99_gera_1_por_cento(self):
        """Vendas na faixa intermediária geram 1% de comissão."""
        casos = {"100.00": "1.00", "250.30": "2.503", "400.00": "4.00", "499.99": "4.9999"}
        for valor, esperado in casos.items():
            with self.subTest(valor=valor):
                self.assertEqual(ex1.calcular_comissao(D(valor)), D(esperado))

    def test_venda_a_partir_de_500_gera_5_por_cento(self):
        """Vendas de R$ 500,00 em diante geram 5% de comissão."""
        casos = {"500.00": "25.00", "500.01": "25.0005", "1200.50": "60.025", "10000.00": "500.00"}
        for valor, esperado in casos.items():
            with self.subTest(valor=valor):
                self.assertEqual(ex1.calcular_comissao(D(valor)), D(esperado))

    def test_limite_de_100_ja_entra_na_faixa_de_1_por_cento(self):
        """Exatamente R$ 100,00 já gera comissão (limite inferior é inclusivo)."""
        # Se o código usasse "<=" no lugar de "<", este teste falharia.
        self.assertGreater(ex1.calcular_comissao(D("100.00")), D("0"))
        self.assertEqual(ex1.calcular_comissao(D("99.99")), D("0"))

    def test_limite_de_500_ja_entra_na_faixa_de_5_por_cento(self):
        """Exatamente R$ 500,00 paga 5% (e não 1%), como no caso do Carlos."""
        self.assertEqual(ex1.calcular_comissao(D("500.00")), D("25.00"))
        self.assertEqual(ex1.calcular_comissao(D("499.99")), D("4.9999"))

    def test_resultado_nao_e_arredondado(self):
        """A função devolve o valor exato; o arredondamento é feito só no total."""
        # 100,01 x 1% = 1,0001. Se arredondasse aqui, perderíamos os 0,0001.
        self.assertEqual(ex1.calcular_comissao(D("100.01")), D("1.0001"))

    def test_retorna_decimal(self):
        """O retorno é sempre Decimal, inclusive quando não há comissão."""
        for valor in ("50", "200", "800"):
            with self.subTest(valor=valor):
                self.assertIsInstance(ex1.calcular_comissao(D(valor)), D)


class TestCarregarVendas(ComPastaTemporaria):
    """Leitura do arquivo ``vendas.json``."""

    def test_le_a_lista_de_vendas(self):
        """Devolve uma lista com uma entrada para cada venda do arquivo."""
        caminho = escrever_vendas(self.pasta, [
            {"vendedor": "Ana Lima", "valor": 75.30},
            {"vendedor": "Carlos Oliveira", "valor": 500.00},
        ])
        vendas = ex1.carregar_vendas(caminho)
        self.assertEqual(len(vendas), 2)
        self.assertEqual(vendas[0]["vendedor"], "Ana Lima")

    def test_valores_sao_decimal_sem_perda_de_precisao(self):
        """Os valores são lidos como Decimal exato, e não como float."""
        # 100.1 não tem representação exata em float (vira 100.099999...).
        # Se o JSON fosse lido como float, esta igualdade falharia.
        caminho = escrever_vendas(self.pasta, [{"vendedor": "Ana", "valor": 100.1}])
        valor = ex1.carregar_vendas(caminho)[0]["valor"]
        self.assertIsInstance(valor, D)
        self.assertEqual(valor, D("100.1"))

    def test_preserva_acentos_dos_nomes(self):
        """Nomes com acento são lidos corretamente (arquivo em UTF-8)."""
        caminho = escrever_vendas(self.pasta, [{"vendedor": "João Silva", "valor": 10}])
        self.assertEqual(ex1.carregar_vendas(caminho)[0]["vendedor"], "João Silva")

    def test_arquivo_inexistente_gera_erro(self):
        """Arquivo ausente lança FileNotFoundError, e não falha em silêncio."""
        with self.assertRaises(FileNotFoundError):
            ex1.carregar_vendas(self.pasta / "nao_existe.json")

    def test_json_sem_chave_vendas_gera_erro(self):
        """JSON válido, mas sem a chave "vendas", lança KeyError."""
        caminho = self.pasta / "errado.json"
        caminho.write_text('{"outra_coisa": []}', encoding="utf-8")
        with self.assertRaises(KeyError):
            ex1.carregar_vendas(caminho)


class TestComissaoPorVendedor(unittest.TestCase):
    """Agrupamento das comissões por vendedor."""

    @staticmethod
    def venda(vendedor: str, valor: str) -> dict:
        """Monta uma venda no formato que ``carregar_vendas`` produz."""
        return {"vendedor": vendedor, "valor": D(valor)}

    def test_soma_as_comissoes_de_cada_venda(self):
        """O total do vendedor é a soma das comissões das suas vendas."""
        vendas = [
            self.venda("João", "500.00"),   # 5%  -> 25.00
            self.venda("João", "200.00"),   # 1%  ->  2.00
            self.venda("João", "50.00"),    # 0%  ->  0.00
        ]
        self.assertEqual(ex1.comissao_por_vendedor(vendas), {"João": D("27.00")})

    def test_separa_vendedores_diferentes(self):
        """Cada vendedor acumula apenas as suas próprias vendas."""
        vendas = [
            self.venda("João", "500.00"),
            self.venda("Maria", "200.00"),
            self.venda("João", "500.00"),
        ]
        self.assertEqual(
            ex1.comissao_por_vendedor(vendas),
            {"João": D("50.00"), "Maria": D("2.00")},
        )

    def test_regra_e_aplicada_por_venda_e_nao_pelo_total(self):
        """Muitas vendas pequenas não somam para uma faixa maior."""
        # 10 vendas de R$ 60,00 somam R$ 600,00. Se a regra incidisse sobre o
        # total, pagaria 5%; como é por venda (cada uma abaixo de 100), é zero.
        vendas = [self.venda("João", "60.00") for _ in range(10)]
        self.assertEqual(ex1.comissao_por_vendedor(vendas), {"João": D("0.00")})

    def test_arredonda_somente_no_total(self):
        """O arredondamento ocorre uma vez, no total, e não a cada venda."""
        # Cada venda de 100,50 rende 1,0050. Somando: 3,0150 -> 3,02.
        # Se cada venda fosse arredondada antes (1,0050 -> 1,01), o total
        # seria 3,03. A diferença prova o momento do arredondamento.
        vendas = [self.venda("João", "100.50") for _ in range(3)]
        self.assertEqual(ex1.comissao_por_vendedor(vendas), {"João": D("3.02")})

    def test_arredondamento_comercial_half_up(self):
        """Metade arredonda para cima (1,005 -> 1,01), e não para o par."""
        # O arredondamento "do banqueiro" (ROUND_HALF_EVEN) daria 1,00.
        resultado = ex1.comissao_por_vendedor([self.venda("João", "100.50")])
        self.assertEqual(resultado["João"], D("1.01"))

    def test_total_sempre_com_duas_casas_decimais(self):
        """O total vem com exatamente duas casas, inclusive quando é zero."""
        resultado = ex1.comissao_por_vendedor([self.venda("Ana", "50.00")])
        # as_tuple().exponent == -2 significa "duas casas decimais".
        self.assertEqual(resultado["Ana"].as_tuple().exponent, -2)

    def test_vendedor_sem_comissao_aparece_com_zero(self):
        """Quem só tem vendas pequenas continua na lista, com comissão 0,00."""
        resultado = ex1.comissao_por_vendedor([self.venda("Ana", "75.30")])
        self.assertEqual(resultado, {"Ana": D("0.00")})

    def test_ordem_segue_a_primeira_aparicao_no_arquivo(self):
        """A ordem dos vendedores é a da primeira venda de cada um."""
        vendas = [
            self.venda("Maria", "10"),
            self.venda("João", "10"),
            self.venda("Maria", "10"),
            self.venda("Ana", "10"),
        ]
        self.assertEqual(list(ex1.comissao_por_vendedor(vendas)), ["Maria", "João", "Ana"])

    def test_lista_vazia_devolve_dicionario_vazio(self):
        """Sem vendas, não há vendedores nem erro."""
        self.assertEqual(ex1.comissao_por_vendedor([]), {})


class TestBrl(unittest.TestCase):
    """Formatação de valores no padrão monetário brasileiro."""

    def test_formatos_comuns(self):
        """Ponto para milhar, vírgula para decimal, sempre com duas casas."""
        casos = {
            "0": "R$ 0,00",
            "2.5": "R$ 2,50",
            "999.99": "R$ 999,99",
            "1234.5": "R$ 1.234,50",
            "1234567.89": "R$ 1.234.567,89",
        }
        for entrada, esperado in casos.items():
            with self.subTest(valor=entrada):
                self.assertEqual(ex1.brl(D(entrada)), esperado)


class TestMain(ComPastaTemporaria):
    """Saída impressa pelo programa."""

    def executar_main(self, vendas: list[dict]) -> str:
        """Roda ``main`` com um arquivo de vendas temporário e devolve o texto impresso."""
        caminho = escrever_vendas(self.pasta, vendas)
        saida = io.StringIO()
        # Troca temporariamente o caminho do arquivo usado pelo módulo e
        # captura tudo que seria impresso no terminal.
        original = ex1.ARQUIVO
        ex1.ARQUIVO = caminho
        try:
            with redirect_stdout(saida):
                ex1.main()
        finally:
            ex1.ARQUIVO = original  # sempre restaura, mesmo se main() falhar
        return saida.getvalue()

    def test_imprime_cabecalho_e_uma_linha_por_vendedor(self):
        """A tabela tem cabeçalho, separador e os vendedores na ordem do arquivo."""
        linhas = self.executar_main([
            {"vendedor": "João Silva", "valor": 500.00},
            {"vendedor": "Maria Souza", "valor": 200.00},
            {"vendedor": "João Silva", "valor": 50.00},
        ]).splitlines()

        self.assertEqual(len(linhas), 4)
        self.assertIn("Vendedor", linhas[0])
        self.assertIn("Comissão", linhas[0])
        self.assertEqual(linhas[1], "-" * 34)
        self.assertTrue(linhas[2].startswith("João Silva"))
        self.assertTrue(linhas[2].endswith("R$ 25,00"))
        self.assertTrue(linhas[3].startswith("Maria Souza"))
        self.assertTrue(linhas[3].endswith("R$ 2,00"))

    def test_colunas_alinhadas(self):
        """Todas as linhas da tabela têm a mesma largura (20 + 14 colunas)."""
        linhas = self.executar_main([{"vendedor": "Ana", "valor": 500.00}]).splitlines()
        self.assertEqual({len(linha) for linha in linhas}, {34})


class TestArquivoRealDoDesafio(unittest.TestCase):
    """Teste de integração com o ``vendas.json`` que acompanha o desafio."""

    def test_comissoes_finais_do_desafio(self):
        """Confere o resultado completo, de ponta a ponta."""
        vendas = ex1.carregar_vendas(ex1.ARQUIVO)
        # O desafio traz 36 vendas no total (10 + 9 + 8 + 9).
        self.assertEqual(len(vendas), 36)

        esperado = {
            "João Silva": D("495.68"),
            "Maria Souza": D("465.95"),
            "Carlos Oliveira": D("379.37"),
            "Ana Lima": D("404.98"),
        }
        self.assertEqual(ex1.comissao_por_vendedor(vendas), esperado)


if __name__ == "__main__":
    unittest.main(verbosity=2)