import os
import sys
from datetime import datetime

import mysql.connector
from PyQt6 import QtCore, QtWidgets
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from agencia_turismo import Ui_MainWindow


class AgenciaTurismo(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        try:
            self.conectar_banco()
            self.carregar_destinos()
            self.carregar_vendas()
        except Exception as e:
            self.alerta(f"Erro ao conectar ao banco:\n{e}")
            return

        # Botões da aba Destinos
        self.ui.btnInserirDest.clicked.connect(self.cadastrar_destino)
        self.ui.btnEditarDest.clicked.connect(self.editar_destino)
        self.ui.btnExcluir.clicked.connect(self.excluir_destino)
        self.ui.tabelaDestinos.cellClicked.connect(self.linha_destino_selecionada)

        # Botões da aba Vendas
        self.ui.btnRegistrar.clicked.connect(self.registrar_venda)
        self.ui.btnExcluirVenda.clicked.connect(self.excluir_venda)
        self.ui.tabelaVendas.cellClicked.connect(self.linha_venda_selecionada)

        # Relatório
        self.ui.btnRelatorio.clicked.connect(self.gerar_relatorio_pdf)

    def conectar_banco(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='131609',
            database='agencia_turismo'
        )
        self.cursor = self.conn.cursor()

    def alerta(self, mensagem):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Atenção")
        msg.setText(mensagem)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.exec()

    # === DESTINOS ===
    def cadastrar_destino(self):
        nome = self.ui.inputNome.text()
        preco = self.ui.inputPreco.text()
        descricao = self.ui.inputDescricao.toPlainText()
        data_viagem = self.ui.inputData.date().toString("yyyy-MM-dd")
        quantidade = self.ui.inputQuantidade.text()

        if nome and preco and data_viagem and quantidade:
            sql = "INSERT INTO destinos (nome, preco, descricao, data_viagem, quantidade) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.execute(sql, (nome, preco, descricao, data_viagem, quantidade))
            self.conn.commit()
            self.ui.inputNome.clear()
            self.ui.inputPreco.clear()
            self.ui.inputDescricao.clear()
            self.ui.inputData.setDate(QtCore.QDate.currentDate())
            self.ui.inputQuantidade.clear()
            self.carregar_destinos()
        else:
            self.alerta("Preencha todos os campos do destino.")

    def carregar_destinos(self):
        self.ui.tabelaDestinos.setRowCount(0)
        self.cursor.execute("SELECT * FROM destinos")
        for row_index, row_data in enumerate(self.cursor.fetchall()):
            self.ui.tabelaDestinos.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.ui.tabelaDestinos.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(str(data)))

        self.ui.comboDestinos.clear()
        self.destinos_ids = []
        self.cursor.execute("SELECT * FROM destinos WHERE quantidade > 0")
        for row in self.cursor.fetchall():
            self.ui.comboDestinos.addItem(row[1])
            self.destinos_ids.append(row[0])

    def linha_destino_selecionada(self, row):
        self.destino_id = self.ui.tabelaDestinos.item(row, 0).text()
        self.ui.inputNome.setText(self.ui.tabelaDestinos.item(row, 1).text())
        self.ui.inputPreco.setText(self.ui.tabelaDestinos.item(row, 2).text())
        self.ui.inputDescricao.setPlainText(self.ui.tabelaDestinos.item(row, 3).text())
        self.ui.inputData.setDate(QtCore.QDate.fromString(self.ui.tabelaDestinos.item(row, 4).text(), "yyyy-MM-dd"))
        self.ui.inputQuantidade.setText(self.ui.tabelaDestinos.item(row, 5).text())

    def editar_destino(self):
        if not hasattr(self, 'destino_id'):
            self.alerta("Selecione um destino na tabela para editar.")
            return

        nome = self.ui.inputNome.text().strip()
        preco = self.ui.inputPreco.text().strip()
        descricao = self.ui.inputDescricao.toPlainText().strip()
        data_viagem = self.ui.inputData.date().toString("yyyy-MM-dd")
        quantidade = self.ui.inputQuantidade.text().strip()

        if not nome or not preco or not data_viagem or not quantidade:
            self.alerta("Preencha todos os campos obrigatórios do destino.")
            return

        try:
            float(preco)
            int(quantidade)
        except ValueError:
            self.alerta("Verifique se o preço e a quantidade são válidos.")
            return

        sql = "UPDATE destinos SET nome=%s, preco=%s, descricao=%s, data_viagem=%s, quantidade=%s WHERE id=%s"
        self.cursor.execute(sql, (nome, preco, descricao, data_viagem, quantidade, self.destino_id))
        self.conn.commit()
        self.carregar_destinos()
        self.ui.inputNome.clear()
        self.ui.inputPreco.clear()
        self.ui.inputDescricao.clear()
        self.ui.inputData.setDate(QtCore.QDate.currentDate())
        self.ui.inputQuantidade.clear()

    def excluir_destino(self):
        if not hasattr(self, 'destino_id'):
            self.alerta("Selecione um destino para excluir.")
            return

        confirm = QtWidgets.QMessageBox.question(
            self, "Confirmar Exclusão", "Deseja realmente excluir este destino?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                sql = "DELETE FROM destinos WHERE id = %s"
                self.cursor.execute(sql, (self.destino_id,))
                self.conn.commit()
                self.carregar_destinos()
                self.destino_id = None
                self.ui.inputNome.clear()
                self.ui.inputPreco.clear()
                self.ui.inputDescricao.clear()
                self.ui.inputData.setDate(QtCore.QDate.currentDate())
                self.ui.inputQuantidade.clear()

                QtWidgets.QMessageBox.information(self, "Sucesso", "Destino excluído com sucesso.")
            except mysql.connector.Error as erro:
                if erro.errno == 1451:
                    QtWidgets.QMessageBox.warning(
                        self, "Erro", "Não é possível excluir este destino porque ele já possui vendas registradas."
                    )
                else:
                    QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao excluir destino:\n{erro}")

    # === VENDAS ===
    def registrar_venda(self):
        nome = self.ui.inputCliente.text()
        telefone = self.ui.inputTelefone.text()
        forma_pagamento = self.ui.comboPagamento.currentText()
        destino_index = self.ui.comboDestinos.currentIndex()

        if nome and telefone and destino_index >= 0:
            destino_id = self.destinos_ids[destino_index]

            sql = "INSERT INTO vendas (cliente_nome, telefone, destino_id, forma_pagamento) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(sql, (nome, telefone, destino_id, forma_pagamento))

            sql_update = "UPDATE destinos SET quantidade = quantidade - 1 WHERE id = %s AND quantidade > 0"
            self.cursor.execute(sql_update, (destino_id,))
            self.conn.commit()

            self.ui.inputCliente.clear()
            self.ui.inputTelefone.clear()
            self.carregar_vendas()
            self.carregar_destinos()
        else:
            self.alerta("Preencha todos os campos da venda.")

    def carregar_vendas(self):
        self.ui.tabelaVendas.setRowCount(0)
        sql = """
        SELECT vendas.id, vendas.cliente_nome, vendas.telefone, destinos.nome, vendas.forma_pagamento
        FROM vendas
        JOIN destinos ON vendas.destino_id = destinos.id
        """
        self.cursor.execute(sql)
        for row_index, row_data in enumerate(self.cursor.fetchall()):
            self.ui.tabelaVendas.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.ui.tabelaVendas.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(str(data)))

    def linha_venda_selecionada(self, row):
        self.venda_id = self.ui.tabelaVendas.item(row, 0).text()

    def excluir_venda(self):
        if not hasattr(self, 'venda_id'):
            self.alerta("Selecione uma venda para excluir.")
            return

        confirm = QtWidgets.QMessageBox.question(
            self, "Excluir Venda", "Tem certeza que deseja excluir esta venda?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            sql = "DELETE FROM vendas WHERE id = %s"
            self.cursor.execute(sql, (self.venda_id,))
            self.conn.commit()
            self.carregar_vendas()
            self.venda_id = None

    # === RELATÓRIO PDF ===
    def gerar_relatorio_pdf(self):
        try:
            nome_arquivo = f"relatorio_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf = canvas.Canvas(nome_arquivo, pagesize=A4)
            largura, altura = A4
            y = altura - 50
            total_vendas = 0.0

            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(180, y, "Relatório de Vendas")
            y -= 30

            self.cursor.execute("""
                SELECT v.cliente_nome, v.telefone, d.nome, v.forma_pagamento, d.preco
                FROM vendas v
                JOIN destinos d ON v.destino_id = d.id
                ORDER BY v.cliente_nome
            """)
            vendas = self.cursor.fetchall()

            if not vendas:
                pdf.setFont("Helvetica", 12)
                pdf.drawString(50, y, "Nenhuma venda registrada.")
                y -= 30
            else:
                headers = ["Cliente", "Telefone", "Destino", "Pagamento", "Preço (R$)"]
                x_positions = [30, 150, 280, 400, 500]

                pdf.setFont("Helvetica-Bold", 10)
                for i, header in enumerate(headers):
                    pdf.drawString(x_positions[i], y, header)
                y -= 20

                pdf.setFont("Helvetica", 10)
                for venda in vendas:
                    nome, telefone, destino, pagamento, preco = venda
                    total_vendas += float(preco)
                    valores = [nome, telefone, destino, pagamento, f"{float(preco):.2f}"]
                    for i, val in enumerate(valores):
                        pdf.drawString(x_positions[i], y, str(val))
                    y -= 20
                    if y < 100:
                        pdf.showPage()
                        y = altura - 50

                y -= 10
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(30, y, f"Total arrecadado: R$ {total_vendas:.2f}")
                y -= 30

            # NOVA PÁGINA
            pdf.showPage()
            y = altura - 50
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(150, y, "Resumo de Vagas por Destino")
            y -= 30

            self.cursor.execute("""
                SELECT d.nome, d.data_viagem, d.quantidade,
                    (SELECT COUNT(*) FROM vendas v WHERE v.destino_id = d.id) AS vendidos
                FROM destinos d
            """)
            destinos = self.cursor.fetchall()

            if not destinos:
                pdf.setFont("Helvetica", 12)
                pdf.drawString(50, y, "Nenhum destino cadastrado.")
            else:
                headers = ["Destino", "Data", "Total", "Vendidos", "Disponíveis"]
                x_positions = [30, 200, 300, 370, 450]

                pdf.setFont("Helvetica-Bold", 10)
                for i, header in enumerate(headers):
                    pdf.drawString(x_positions[i], y, header)
                y -= 20

                pdf.setFont("Helvetica", 10)
                for destino in destinos:
                    nome_destino, data_viagem, disponiveis, vendidos = destino
                    total_ofertado = disponiveis + vendidos

                    valores = [
                        nome_destino,
                        data_viagem.strftime("%d/%m/%Y"),
                        str(total_ofertado),
                        str(vendidos),
                        str(disponiveis)
                    ]

                    for i, val in enumerate(valores):
                        pdf.drawString(x_positions[i], y, val)
                    y -= 20
                    if y < 100:
                        pdf.showPage()
                        y = altura - 50

            pdf.save()
            os.startfile(nome_arquivo) if sys.platform.startswith('win') else os.system(f"open '{nome_arquivo}'")

        except Exception as e:
            self.alerta(f"Erro ao gerar relatório: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    janela = AgenciaTurismo()
    janela.show()
    sys.exit(app.exec())
