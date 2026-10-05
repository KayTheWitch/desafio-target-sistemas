"""Testes automatizados do Exercício 2 - Movimentação de estoque.

Descrição
---------
Verifica o script ``exercicio2_estoque`` nas suas três camadas:
persistência (JSON), regras de negócio (movimentações) e interface de texto
(menu interativo).

O que é testado
---------------
    +-----------------------------------+----------------------------------------+
    | Classe de teste                   | Comportamento coberto                  |
    +===================================+========================================+
    | TestBuscarProduto                 | localizar produto por código           |
    +-----------------------------------+----------------------------------------+
    | TestProximoId                     | geração do id sequencial único         |
    +-----------------------------------+----------------------------------------+
    | TestRegistrarMovimentacao         | entradas e saídas válidas, campos do   |
    |                                   | registro, ids, saldos                  |
    +-----------------------------------+----------------------------------------+
    | TestRegistrarMovimentacaoInvalida | todas as validações e garantia de que  |
    |                                   | nada é alterado quando falham          |
    +-----------------------------------+----------------------------------------+
    | TestPersistencia                  | leitura e gravação dos arquivos JSON   |
    +-----------------------------------+----------------------------------------+
    | TestInterface                     | leitura de inteiros e listagem         |
    +-----------------------------------+----------------------------------------+
    | TestMain                          | menu completo, de ponta a ponta        |
    +-----------------------------------+----------------------------------------+

Estratégia de teste
-------------------
* **Dados sempre novos:** cada teste recebe um estoque recém-criado por
  ``estoque_exemplo()``. Como a função de negócio altera os dados em memória,
  compartilhar a mesma lista entre testes faria um interferir no outro.
* **Isolamento do disco:** os testes do menu redirecionam ``ARQ_ESTOQUE`` e
  ``ARQ_MOVIMENTACOES`` para uma pasta temporária. Os arquivos reais do
  projeto nunca são lidos nem alterados.
* **Entrada simulada:** ``input()`` é substituído por uma lista de respostas
  (``mock.patch``), e o que seria impresso é capturado com ``redirect_stdout``.
* **Falhas não alteram nada:** todo cenário inválido compara o estado antes e
  depois (cópia profunda), garantindo que não houve alteração parcial.

Como executar
-------------
    python -m unittest test_exercicio2_estoque -v

    # discovery dos testes deste exercício, a partir da raiz do repositório:
    python -m unittest discover -s exercicio_02_estoque -v

    # opcional, se o pytest estiver instalado:
    pytest -v

Resultado esperado
------------------
Cada teste aparece com status ``ok`` e, ao final, a mensagem ``OK``.
"""
import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import exercicio2_estoque as ex2


def estoque_exemplo() -> list[dict]:
    """Cria um estoque novo a cada chamada.

    Returns:
        Lista com dois produtos: Caneta Azul (código 101, saldo 150) e
        Caderno Universitário (código 102, saldo 75).
    """
    return [
        {"codigoProduto": 101, "descricaoProduto": "Caneta Azul", "estoque": 150},
        {"codigoProduto": 102, "descricaoProduto": "Caderno Universitário", "estoque": 75},
    ]


class ComPastaTemporaria(unittest.TestCase):
    """Base para testes que precisam de arquivos: cria e limpa uma pasta temporária."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        # addCleanup garante a limpeza mesmo se o teste falhar no meio.
        self.addCleanup(self.tmp.cleanup)
        self.pasta = Path(self.tmp.name)


class TestBuscarProduto(unittest.TestCase):
    """Localização de produtos pelo código."""

    def test_encontra_produto_existente(self):
        """Devolve o produto cujo código foi informado."""
        produto = ex2.buscar_produto(estoque_exemplo(), 102)
        self.assertEqual(produto["descricaoProduto"], "Caderno Universitário")

    def test_codigo_inexistente_devolve_none(self):
        """Código que não está no estoque resulta em None, e não em erro."""
        self.assertIsNone(ex2.buscar_produto(estoque_exemplo(), 999))

    def test_estoque_vazio_devolve_none(self):
        """Lista vazia não causa erro."""
        self.assertIsNone(ex2.buscar_produto([], 101))

    def test_devolve_o_proprio_item_e_nao_uma_copia(self):
        """Alterar o produto devolvido altera o estoque em memória."""
        # É esse comportamento que permite a registrar_movimentacao atualizar
        # o saldo diretamente no produto.
        estoque = estoque_exemplo()
        ex2.buscar_produto(estoque, 101)["estoque"] = 1
        self.assertEqual(estoque[0]["estoque"], 1)


class TestProximoId(unittest.TestCase):
    """Geração do identificador único de movimentação."""

    def test_historico_vazio_comeca_em_1(self):
        self.assertEqual(ex2.proximo_id([]), 1)

    def test_soma_um_ao_maior_id(self):
        self.assertEqual(ex2.proximo_id([{"id": 1}, {"id": 2}]), 3)

    def test_usa_o_maior_id_e_nao_a_quantidade_de_registros(self):
        """Com ids fora de ordem ou com lacunas, nunca reaproveita um id."""
        # Há 2 registros, mas o maior id é 5: o próximo precisa ser 6 (e não 3).
        self.assertEqual(ex2.proximo_id([{"id": 5}, {"id": 2}]), 6)


class TestRegistrarMovimentacao(unittest.TestCase):
    """Movimentações válidas: efeito no saldo e conteúdo do registro."""

    def setUp(self) -> None:
        self.estoque = estoque_exemplo()
        self.historico: list[dict] = []

    def mover(self, codigo=101, tipo="entrada", quantidade=10, descricao="Compra") -> dict:
        """Atalho para chamar ``registrar_movimentacao`` com os dados do teste."""
        return ex2.registrar_movimentacao(
            self.estoque, self.historico, codigo, tipo, quantidade, descricao
        )

    def saldo(self, codigo: int) -> int:
        """Saldo atual do produto no estoque em memória."""
        return ex2.buscar_produto(self.estoque, codigo)["estoque"]

    def test_entrada_soma_ao_saldo(self):
        mov = self.mover(tipo="entrada", quantidade=50)
        self.assertEqual(self.saldo(101), 200)       # 150 + 50
        self.assertEqual(mov["saldoFinal"], 200)

    def test_saida_subtrai_do_saldo(self):
        mov = self.mover(tipo="saida", quantidade=30, descricao="Venda")
        self.assertEqual(self.saldo(101), 120)       # 150 - 30
        self.assertEqual(mov["saldoFinal"], 120)

    def test_saida_de_todo_o_saldo_e_permitida(self):
        """Retirar exatamente o saldo zera o estoque, sem erro."""
        # Limite da regra: só é recusada a saída MAIOR que o saldo. Se o
        # código usasse ">=" no lugar de ">", este teste falharia.
        mov = self.mover(tipo="saida", quantidade=150, descricao="Venda total")
        self.assertEqual(mov["saldoFinal"], 0)
        self.assertEqual(self.saldo(101), 0)

    def test_nao_altera_outros_produtos(self):
        """Movimentar um produto não mexe no saldo dos demais."""
        self.mover(codigo=101, tipo="entrada", quantidade=50)
        self.assertEqual(self.saldo(102), 75)

    def test_registro_contem_todos_os_campos(self):
        """O registro traz exatamente os campos documentados."""
        mov = self.mover(codigo=102, tipo="saida", quantidade=10, descricao="Venda")
        self.assertEqual(
            set(mov),
            {"id", "data", "codigoProduto", "tipo", "quantidade",
             "descricao", "saldoAnterior", "saldoFinal"},
        )
        self.assertEqual(mov["codigoProduto"], 102)
        self.assertEqual(mov["tipo"], "saida")
        self.assertEqual(mov["quantidade"], 10)
        self.assertEqual(mov["descricao"], "Venda")

    def test_registro_guarda_saldo_anterior_e_final(self):
        mov = self.mover(tipo="entrada", quantidade=50)
        self.assertEqual(mov["saldoAnterior"], 150)
        self.assertEqual(mov["saldoFinal"], 200)

    def test_registro_e_adicionado_ao_historico(self):
        """O mesmo registro devolvido fica guardado no histórico."""
        mov = self.mover()
        self.assertEqual(self.historico, [mov])

    def test_ids_sao_sequenciais_e_unicos(self):
        """Três movimentações recebem os ids 1, 2 e 3."""
        ids = [self.mover()["id"] for _ in range(3)]
        self.assertEqual(ids, [1, 2, 3])

    def test_movimentacoes_encadeadas_mantem_coerencia_dos_saldos(self):
        """O saldo anterior de uma movimentação é o saldo final da anterior."""
        primeira = self.mover(tipo="entrada", quantidade=50)
        segunda = self.mover(tipo="saida", quantidade=20, descricao="Venda")
        self.assertEqual(segunda["saldoAnterior"], primeira["saldoFinal"])
        self.assertEqual(segunda["saldoFinal"], 180)  # 150 + 50 - 20

    def test_descricao_tem_espacos_das_pontas_removidos(self):
        mov = self.mover(descricao="  Venda balcão  ")
        self.assertEqual(mov["descricao"], "Venda balcão")

    def test_data_esta_em_formato_iso_e_e_recente(self):
        """A data é gravada em ISO 8601 e corresponde ao momento do registro."""
        mov = self.mover()
        momento = datetime.fromisoformat(mov["data"])   # falha se o formato for inválido
        self.assertLess(abs(datetime.now() - momento), timedelta(minutes=1))


class TestRegistrarMovimentacaoInvalida(unittest.TestCase):
    """Validações: cada caso inválido gera erro e deixa tudo como estava."""

    def test_cada_validacao_gera_erro_com_mensagem_clara(self):
        """Tabela de casos inválidos: (código, tipo, quantidade, descrição, trecho da mensagem)."""
        casos = [
            (999, "entrada", 10, "Compra", "não encontrado"),     # produto inexistente
            (101, "transferencia", 10, "Compra", "Tipo deve ser"),  # tipo desconhecido
            (101, "entrada", 0, "Compra", "maior que zero"),       # quantidade zero
            (101, "entrada", -5, "Compra", "maior que zero"),      # quantidade negativa
            (101, "entrada", 10, "", "obrigatória"),               # descrição vazia
            (101, "entrada", 10, "   ", "obrigatória"),            # descrição só com espaços
            (101, "saida", 151, "Venda", "insuficiente"),          # saída maior que o saldo
        ]
        for codigo, tipo, quantidade, descricao, trecho in casos:
            with self.subTest(codigo=codigo, tipo=tipo, quantidade=quantidade, descricao=descricao):
                estoque, historico = estoque_exemplo(), []

                with self.assertRaisesRegex(ValueError, trecho):
                    ex2.registrar_movimentacao(
                        estoque, historico, codigo, tipo, quantidade, descricao
                    )

                # Nada pode ter sido alterado: nem o saldo, nem o histórico.
                self.assertEqual(estoque, estoque_exemplo())
                self.assertEqual(historico, [])

    def test_mensagem_de_saldo_insuficiente_informa_os_numeros(self):
        """A mensagem mostra o saldo atual e a quantidade pedida."""
        with self.assertRaises(ValueError) as contexto:
            ex2.registrar_movimentacao(estoque_exemplo(), [], 101, "saida", 999, "Venda")
        mensagem = str(contexto.exception)
        self.assertIn("150", mensagem)
        self.assertIn("999", mensagem)

    def test_erro_nao_consome_id(self):
        """Uma tentativa recusada não "queima" um número de id."""
        estoque, historico = estoque_exemplo(), []
        with self.assertRaises(ValueError):
            ex2.registrar_movimentacao(estoque, historico, 101, "saida", 999, "Venda")
        mov = ex2.registrar_movimentacao(estoque, historico, 101, "entrada", 1, "Compra")
        self.assertEqual(mov["id"], 1)


class TestPersistencia(ComPastaTemporaria):
    """Leitura e gravação dos arquivos JSON."""

    def test_arquivo_inexistente_devolve_o_valor_padrao(self):
        """Na primeira execução (sem movimentacoes.json), usa o padrão informado."""
        padrao = []
        resultado = ex2.carregar_json(self.pasta / "nao_existe.json", padrao)
        self.assertIs(resultado, padrao)

    def test_arquivo_existente_devolve_o_conteudo(self):
        caminho = self.pasta / "dados.json"
        caminho.write_text('{"a": 1}', encoding="utf-8")
        self.assertEqual(ex2.carregar_json(caminho, {}), {"a": 1})

    def test_salvar_e_carregar_devolve_os_mesmos_dados(self):
        """Ida e volta: o que foi gravado é exatamente o que se lê depois."""
        caminho = self.pasta / "dados.json"
        dados = {"estoque": estoque_exemplo()}
        ex2.salvar_json(caminho, dados)
        self.assertEqual(ex2.carregar_json(caminho, None), dados)

    def test_salvar_mantem_acentos_legiveis_no_arquivo(self):
        """O arquivo contém "Universitário" e não a sequência "Universit\\u00e1rio"."""
        caminho = self.pasta / "dados.json"
        ex2.salvar_json(caminho, {"estoque": estoque_exemplo()})
        texto = caminho.read_text(encoding="utf-8")
        self.assertIn("Caderno Universitário", texto)
        self.assertNotIn("\\u00", texto)

    def test_salvar_sobrescreve_o_conteudo_anterior(self):
        caminho = self.pasta / "dados.json"
        ex2.salvar_json(caminho, {"versao": 1})
        ex2.salvar_json(caminho, {"versao": 2})
        self.assertEqual(ex2.carregar_json(caminho, None), {"versao": 2})


class TestInterface(unittest.TestCase):
    """Funções de interação com o usuário (entrada e exibição)."""

    def test_ler_inteiro_aceita_numero_valido(self):
        with mock.patch("builtins.input", return_value="42"):
            self.assertEqual(ex2.ler_inteiro("Quantidade: "), 42)

    def test_ler_inteiro_repete_ate_receber_valor_valido(self):
        """Entradas inválidas geram aviso e nova pergunta, sem encerrar."""
        saida = io.StringIO()
        # Três respostas inválidas (texto, decimal com vírgula, vazio) e depois "7".
        with mock.patch("builtins.input", side_effect=["abc", "3,5", "", "7"]), redirect_stdout(saida):
            resultado = ex2.ler_inteiro("Quantidade: ")
        self.assertEqual(resultado, 7)
        self.assertEqual(saida.getvalue().count("Digite um número inteiro válido."), 3)

    def test_ler_inteiro_nao_valida_o_sinal(self):
        """Números negativos passam por aqui; quem recusa é a regra de negócio."""
        # A responsabilidade de rejeitar quantidade <= 0 é de
        # registrar_movimentacao (testada acima), e não da leitura.
        with mock.patch("builtins.input", return_value="-3"):
            self.assertEqual(ex2.ler_inteiro("Quantidade: "), -3)

    def test_listar_estoque_mostra_codigo_nome_e_saldo(self):
        saida = io.StringIO()
        with redirect_stdout(saida):
            ex2.listar_estoque(estoque_exemplo())
        texto = saida.getvalue()
        for esperado in ("Cód.", "Produto", "Estoque", "101", "Caneta Azul", "150",
                         "102", "Caderno Universitário", "75"):
            with self.subTest(trecho=esperado):
                self.assertIn(esperado, texto)


class TestMain(ComPastaTemporaria):
    """Menu interativo completo, simulando um usuário digitando."""

    def setUp(self) -> None:
        super().setUp()
        self.arq_estoque = self.pasta / "estoque.json"
        self.arq_movimentacoes = self.pasta / "movimentacoes.json"

        # Cria o estoque inicial direto com json (sem usar o código testado).
        with open(self.arq_estoque, "w", encoding="utf-8") as f:
            json.dump({"estoque": estoque_exemplo()}, f, ensure_ascii=False)

        # Redireciona as constantes do módulo para a pasta temporária. Assim,
        # os arquivos reais do projeto nunca são tocados pelos testes.
        for nome, caminho in (("ARQ_ESTOQUE", self.arq_estoque),
                              ("ARQ_MOVIMENTACOES", self.arq_movimentacoes)):
            patcher = mock.patch.object(ex2, nome, caminho)
            patcher.start()
            self.addCleanup(patcher.stop)

    def executar(self, entradas: list[str]) -> str:
        """Roda ``main`` respondendo às perguntas com ``entradas``, na ordem.

        Args:
            entradas: respostas que o "usuário" digita, uma por ``input()``.
                Se o programa pedir mais respostas do que as fornecidas, o
                teste falha (StopIteration), sinal de fluxo inesperado.

        Returns:
            Todo o texto que o programa imprimiu.
        """
        saida = io.StringIO()
        with mock.patch("builtins.input", side_effect=entradas), redirect_stdout(saida):
            ex2.main()
        return saida.getvalue()

    def saldos_gravados(self) -> dict[int, int]:
        """Lê o estoque.json temporário e devolve ``{código: saldo}``."""
        with open(self.arq_estoque, encoding="utf-8") as f:
            return {p["codigoProduto"]: p["estoque"] for p in json.load(f)["estoque"]}

    def historico_gravado(self) -> list[dict]:
        """Lê o movimentacoes.json temporário."""
        with open(self.arq_movimentacoes, encoding="utf-8") as f:
            return json.load(f)

    def test_entrada_valida_atualiza_saldo_e_informa_quantidade_final(self):
        saida = self.executar(["1", "101", "50", "Compra fornecedor", "0"])

        self.assertIn("Movimentação #1 registrada (Compra fornecedor)", saida)
        self.assertIn("Quantidade final de 'Caneta Azul': 200", saida)
        self.assertEqual(self.saldos_gravados()[101], 200)

        historico = self.historico_gravado()
        self.assertEqual(len(historico), 1)
        self.assertEqual(historico[0]["descricao"], "Compra fornecedor")
        self.assertEqual(historico[0]["tipo"], "entrada")

    def test_saida_valida_subtrai_do_saldo(self):
        saida = self.executar(["2", "102", "10", "Venda", "0"])

        self.assertIn("Quantidade final de 'Caderno Universitário': 65", saida)
        self.assertEqual(self.saldos_gravados()[102], 65)
        self.assertEqual(self.historico_gravado()[0]["tipo"], "saida")

    def test_saida_maior_que_saldo_mostra_aviso_e_nao_grava_nada(self):
        saida = self.executar(["2", "101", "999", "Venda", "0"])

        self.assertIn("Estoque insuficiente", saida)
        self.assertEqual(self.saldos_gravados()[101], 150)           # saldo intacto
        self.assertFalse(self.arq_movimentacoes.exists())            # nem criou histórico

    def test_produto_inexistente_mostra_aviso(self):
        saida = self.executar(["1", "999", "5", "Teste", "0"])

        self.assertIn("Produto 999 não encontrado", saida)
        self.assertFalse(self.arq_movimentacoes.exists())

    def test_programa_continua_apos_um_erro(self):
        """Após uma recusa o menu reaparece e um novo lançamento funciona."""
        saida = self.executar([
            "2", "101", "999", "Venda",       # recusado: saldo insuficiente
            "2", "101", "10", "Venda",        # aceito logo em seguida
            "0",
        ])
        self.assertIn("Estoque insuficiente", saida)
        self.assertIn("Quantidade final de 'Caneta Azul': 140", saida)

    def test_opcao_de_menu_invalida_e_ignorada(self):
        saida = self.executar(["9", "0"])
        self.assertIn("Opção inválida", saida)

    def test_codigo_nao_numerico_e_perguntado_de_novo(self):
        """Digitar texto no lugar do código não derruba o programa."""
        saida = self.executar(["1", "abc", "101", "10", "Compra", "0"])
        self.assertIn("Digite um número inteiro válido.", saida)
        self.assertEqual(self.saldos_gravados()[101], 160)

    def test_sair_de_imediato_nao_grava_historico(self):
        self.executar(["0"])
        self.assertFalse(self.arq_movimentacoes.exists())
        self.assertEqual(self.saldos_gravados(), {101: 150, 102: 75})

    def test_ids_continuam_de_onde_pararam_entre_execucoes(self):
        """Fechar e reabrir o programa não repete nem reinicia os ids."""
        self.executar(["1", "101", "10", "Compra", "0"])    # 1ª execução
        self.executar(["1", "101", "10", "Compra", "0"])    # 2ª execução (recarrega os arquivos)

        ids = [m["id"] for m in self.historico_gravado()]
        self.assertEqual(ids, [1, 2])
        self.assertEqual(self.saldos_gravados()[101], 170)

    def test_varias_movimentacoes_na_mesma_execucao(self):
        saida = self.executar([
            "1", "101", "50", "Compra", "2", "101", "20", "Venda", "0",
        ])
        self.assertIn("Movimentação #1", saida)
        self.assertIn("Movimentação #2", saida)
        self.assertEqual(self.saldos_gravados()[101], 180)   # 150 + 50 - 20


if __name__ == "__main__":
    unittest.main(verbosity=2)