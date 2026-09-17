# -*- coding: utf-8 -*-
import io
import unittest

from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

from pyboleto.data import BoletoData, BoletoException, LIMITE_ENDERECO_CEDENTE
from pyboleto.pdf import BoletoPDF

ENDERECO_LONGO = ('AVENIDA PRESIDENTE JUSCELINO KUBITSCHEK, 1909 TORRE NORTE '
                  'CONJUNTO 142 - VILA NOVA CONCEICAO - SAO PAULO - SP - '
                  '04543-907')


class TestEnderecoCedente(unittest.TestCase):
    def setUp(self):
        self.boleto_pdf = BoletoPDF(io.BytesIO())
        self.boleto_pdf.pdf_canvas.setFont('Helvetica', 9)
        self.largura_recibo_caixa = (self.boleto_pdf.width - (45 * mm) -
                                     self.boleto_pdf.space)

    def _truncar(self, texto):
        return self.boleto_pdf._truncar_preservando_cep(
            texto, self.largura_recibo_caixa)

    def test_endereco_curto_nao_e_alterado(self):
        endereco = 'RUA XV, 100 - CENTRO - CURITIBA - PR - 80020-310'
        self.assertEqual(self._truncar(endereco), endereco)

    def test_endereco_longo_cabe_na_largura_disponivel(self):
        truncado = self._truncar(ENDERECO_LONGO)
        self.assertLessEqual(stringWidth(truncado, 'Helvetica', 9),
                             self.largura_recibo_caixa)

    def test_endereco_longo_mantem_o_cep(self):
        self.assertTrue(self._truncar(ENDERECO_LONGO).endswith('04543-907'))

    def test_endereco_longo_sem_cep_e_cortado_no_fim(self):
        truncado = self._truncar('A CASA DE PALHA ' * 20)
        self.assertTrue(truncado.endswith('...'))
        self.assertLessEqual(stringWidth(truncado, 'Helvetica', 9),
                             self.largura_recibo_caixa)

    def test_endereco_acima_do_limite_e_recusado(self):
        boleto_dados = BoletoData()
        with self.assertRaises(BoletoException):
            boleto_dados.cedente_endereco = 'X' * (LIMITE_ENDERECO_CEDENTE + 1)

    def test_endereco_no_limite_e_aceito(self):
        boleto_dados = BoletoData()
        boleto_dados.cedente_endereco = 'X' * LIMITE_ENDERECO_CEDENTE
        self.assertEqual(len(boleto_dados.cedente_endereco),
                         LIMITE_ENDERECO_CEDENTE)
