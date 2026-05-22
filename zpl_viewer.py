import sys
import re
import subprocess
import tempfile
import os
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
    QLabel, QLineEdit, QComboBox, QDialog, QTextEdit, QFileDialog, QCheckBox,
    QSpinBox, QHeaderView, QTableWidget, QTableWidgetItem, QMenu, QAbstractItemView
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, Signal, Slot
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QClipboard, QAction
from functools import partial

import os


def carregar_codigos_zpl(arquivo: str) -> list[str]:
    """Carrega e extrai códigos ZPL únicos de um arquivo texto."""
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    codigos = []
    partes = conteudo.split('^XA')
    for parte in partes:
        if '^XZ' in parte:
            zpl = '^XA' + parte.split('^XZ')[0] + '^XZ'
            zpl = re.sub(r'\s+', ' ', zpl)
            codigos.append(zpl.strip())
    # Remove duplicatas preservando ordem
    vistos = set()
    codigos_unicos = []
    for c in codigos:
        if c not in vistos:
            vistos.add(c)
            codigos_unicos.append(c)
    return codigos_unicos


# Regexes do mapping_fields do Pompeia
MAPPING_FIELDS = {
    "OC": r"\^MD10\^FO35,245\^FB250,1,0,C\^A0N,17,14\^FD ([0-9]+) CORE\^FS",
    "COR": r"\^FO35,265\^FB250,1,0,C\^A0N,18,15\^FD(\w+)\^FS",
    "TAMANHO": r" \^FO35,373\^FB250,1,0,C\^A0N,45,37\^FD (\d+)\^FS",
    "REF": r"\^FO35,285\^FB250,3,0,C\^A0N,13,15\^FD(\d+) - LOVE SECRET\^FS"
}

# Ordem das colunas do MAPPING para exibição na tabela
CAMPOS_TABELA = ["OC", "COR", "TAMANHO", "REF"]


def extrair_campos_zpl(zpl: str) -> dict[str, str]:
    """Extrai os campos mapeados de um código ZPL."""
    campos = {}
    for campo, regex in MAPPING_FIELDS.items():
        m = re.search(regex, zpl)
        campos[campo] = m.group(1) if m else ""
    return campos


class CodigoDialog(QDialog):
    """Diálogo para visualizar o código ZPL completo."""

    def __init__(self, codigo: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle('Visualizar Código ZPL')
        self.resize(700, 400)
        layout = QVBoxLayout(self)
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.textEdit.setPlainText(codigo)
        layout.addWidget(self.textEdit)
        btn_copiar = QPushButton('Copiar', self)
        btn_copiar.clicked.connect(lambda: self.copiar_codigo(codigo))
        layout.addWidget(btn_copiar)

    def copiar_codigo(self, codigo: str) -> None:
        clipboard = QApplication.clipboard()
        clipboard.setText(codigo, QClipboard.Clipboard)
        clipboard.setText(codigo, QClipboard.Selection)
        QMessageBox.information(self, 'Copiado', 'Código ZPL copiado para o clipboard!')


class ZplViewer(QWidget):
    """Widget principal do visualizador de códigos ZPL."""

    COL_CHECKBOX = 0
    COL_OC = 1
    COL_COR = 2
    COL_TAMANHO = 3
    COL_REF = 4
    COL_QUANTIDADE = 5
    NUM_COLUNAS = 6

    def __init__(self, codigos: Optional[list[str]] = None):
        super().__init__()

        # Carrega UI
        loader = QUiLoader()
        ui_file = QFile("zpl_viewer.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setWindowTitle(self.ui.windowTitle())
        self.resize(self.ui.width(), self.ui.height())

        # Widgets da UI
        self.searchEdit: QLineEdit = self.ui.findChild(QLineEdit, "searchEdit")
        self.filterCombo: QComboBox = self.ui.findChild(QComboBox, "filterCombo")
        self.btnAbrir: QPushButton = self.ui.findChild(QPushButton, "btnAbrir")
        self.btnImprimir: QPushButton = self.ui.findChild(QPushButton, "btnImprimir")
        self.tableWidget: QTableWidget = self.ui.findChild(QTableWidget, "tableWidget")
        self.footerLabel: QLabel = self.ui.findChild(QLabel, "footerLabel")

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.ui)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setAcceptDrops(True)
        self._dados: list[dict] = []  # Lista completa de itens (sem filtro)

        # Configura tabela
        self._configurar_tabela()

        # Conecta sinais
        self.searchEdit.textChanged.connect(self._filtrar_lista)
        self.filterCombo.currentIndexChanged.connect(self._filtrar_lista)
        self.btnAbrir.clicked.connect(self._abrir_arquivo)
        self.btnImprimir.clicked.connect(self._enviar_para_impressora)

        # Inicializa filtros
        self.filterCombo.clear()
        self.filterCombo.addItem("Todos os campos")
        for campo in MAPPING_FIELDS.keys():
            self.filterCombo.addItem(campo)

        # Menu de contexto
        self.tableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self._mostrar_menu_contexto)

        if codigos:
            self.set_codigos(codigos)

    # --- Eventos de drag & drop ---

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self._carregar_arquivo(file_path)

    # --- Configuração da tabela ---

    def _configurar_tabela(self) -> None:
        """Configura colunas, cabeçalhos e comportamento da tabela."""
        self.tableWidget.setColumnCount(self.NUM_COLUNAS)
        headers = ["", "OC", "COR", "TAMANHO", "REF", "Quantidade"]
        self.tableWidget.setHorizontalHeaderLabels(headers)

        # Configurar largura das colunas
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(self.COL_CHECKBOX, QHeaderView.ResizeMode.Fixed)
        self.tableWidget.setColumnWidth(self.COL_CHECKBOX, 40)
        header.setSectionResizeMode(self.COL_OC, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(self.COL_COR, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(self.COL_TAMANHO, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(self.COL_REF, QHeaderView.ResizeMode.Interactive)
        # Quantidade: Fixed mas o StretchLastSection garante que não fique borda cortando
        header.setSectionResizeMode(self.COL_QUANTIDADE, QHeaderView.ResizeMode.Fixed)
        self.tableWidget.setColumnWidth(self.COL_QUANTIDADE, 110)
        # Estica a última seção para ocupar espaço extra e evitar borda cortada
        header.setStretchLastSection(True)

        # Comportamento
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # --- Carregamento de dados ---

    def _abrir_arquivo(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Escolher arquivo ZPL", "",
            "Arquivos de texto (*.txt);;Todos arquivos (*)"
        )
        if file_path:
            self._carregar_arquivo(file_path)

    def _carregar_arquivo(self, file_path: str) -> None:
        codigos = carregar_codigos_zpl(file_path)
        self.set_codigos(codigos)

    def set_codigos(self, codigos: list[str]) -> None:
        """Define os códigos ZPL a serem exibidos."""
        self._dados = []
        for zpl in codigos:
            campos = extrair_campos_zpl(zpl)
            self._dados.append({"codigo": zpl, **campos})
        self._filtrar_lista()

    # --- Filtragem e exibição ---

    def _filtrar_lista(self) -> None:
        """Aplica filtro de texto/campo e popula a tabela."""
        texto = self.searchEdit.text().strip().lower()
        filtro = self.filterCombo.currentText()

        # Limpa tabela
        self.tableWidget.setRowCount(0)
        self.tableWidget.clearContents()

        # Lista de checkboxes e spinboxes (indexados pela linha VISÍVEL)
        linha_visivel = 0

        for idx, item in enumerate(self._dados):
            # Verifica se o item corresponde ao filtro
            if texto:
                if filtro == "Todos os campos":
                    match = any(
                        texto in str(item.get(campo, "")).lower()
                        for campo in MAPPING_FIELDS.keys()
                    )
                else:
                    match = texto in str(item.get(filtro, "")).lower()
            else:
                match = True

            if not match:
                continue

            # Adiciona linha na tabela
            self.tableWidget.insertRow(linha_visivel)

            # Coluna 0: Checkbox centralizado
            checkbox = QCheckBox()
            checkbox.setObjectName(f"check_{idx}")
            widget_check = QWidget()
            layout_check = QHBoxLayout(widget_check)
            layout_check.setContentsMargins(0, 0, 0, 0)
            layout_check.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout_check.addWidget(checkbox)

            # Coluna 5: SpinBox de quantidade (desabilitado inicialmente)
            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setMaximum(999)
            spin.setValue(1)
            spin.setEnabled(False)
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            widget_spin = QWidget()
            layout_spin = QHBoxLayout(widget_spin)
            layout_spin.setContentsMargins(0, 0, 0, 0)
            layout_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout_spin.addWidget(spin)

            # Conecta checkbox para habilitar/desabilitar o spin da mesma linha
            checkbox.toggled.connect(lambda checked, s=spin: s.setEnabled(checked))

            # Insere widgets na tabela
            self.tableWidget.setCellWidget(linha_visivel, self.COL_CHECKBOX, widget_check)
            self.tableWidget.setCellWidget(linha_visivel, self.COL_QUANTIDADE, widget_spin)

            # Colunas de texto: OC, COR, TAMANHO, REF (centralizadas)
            for col_idx, campo in enumerate(CAMPOS_TABELA, start=self.COL_OC):
                item_tabela = QTableWidgetItem(item.get(campo, ""))
                item_tabela.setFlags(item_tabela.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item_tabela.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(linha_visivel, col_idx, item_tabela)

            # Armazena o código ZPL como UserRole no primeiro item da linha
            self.tableWidget.item(linha_visivel, self.COL_OC).setData(Qt.ItemDataRole.UserRole, item["codigo"])

            linha_visivel += 1

        # Atualiza footer
        self.footerLabel.setText(f"Itens identificados: {linha_visivel}")

    # --- Seleção e impressão ---

    def _obter_codigos_selecionados(self) -> list[tuple[str, int]]:
        """Retorna lista de (codigo_zpl, quantidade) dos itens com checkbox marcado."""
        selecionados: list[tuple[str, int]] = []
        for row in range(self.tableWidget.rowCount()):
            checkbox_widget = self.tableWidget.cellWidget(row, self.COL_CHECKBOX)
            spin_widget = self.tableWidget.cellWidget(row, self.COL_QUANTIDADE)
            item = self.tableWidget.item(row, self.COL_OC)

            # O checkbox agora está dentro de um QWidget wrapper
            checkbox = checkbox_widget.findChild(QCheckBox) if checkbox_widget else None
            spin = spin_widget.findChild(QSpinBox) if spin_widget else None

            if checkbox and checkbox.isChecked() and item:
                codigo = item.data(Qt.ItemDataRole.UserRole)
                qtd = spin.value() if spin else 1
                selecionados.append((codigo, qtd))

        return selecionados

    def _enviar_para_impressora(self) -> None:
        """Envia os códigos ZPL selecionados como dados brutos para a impressora."""
        codigos_qtd = self._obter_codigos_selecionados()
        if not codigos_qtd:
            QMessageBox.warning(self, "Aviso", "Selecione ao menos um item para imprimir.")
            return

        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        dialog.setWindowTitle("Escolher impressora")
        if dialog.exec() != QDialog.Accepted:
            return

        nome_impressora = printer.printerName()
        if not nome_impressora:
            QMessageBox.warning(self, "Erro", "Nenhuma impressora selecionada.")
            return

        total = 0
        erros = 0
        for codigo, qtd in codigos_qtd:
            for _ in range(qtd):
                if self._imprimir_zpl_raw(nome_impressora, codigo):
                    total += 1
                else:
                    erros += 1

        if erros == 0:
            QMessageBox.information(
                self, "Impressão",
                f"{total} etiqueta(s) enviada(s) para a impressora \"{nome_impressora}\"."
            )
        else:
            QMessageBox.warning(
                self, "Impressão",
                f"{total} etiqueta(s) enviada(s), {erros} falha(s) na impressora \"{nome_impressora}\"."
            )

    def _imprimir_zpl_raw(self, nome_impressora: str, codigo: str) -> bool:
        """
        Envia o código ZPL como dados brutos para a impressora.

        Funciona em:
          - Windows: via win32print.WritePrinter com tipo RAW
          - Linux:   via lp -o raw (CUPS raw queue)
        """
        if sys.platform == "win32":
            return self._imprimir_windows(nome_impressora, codigo)
        else:
            return self._imprimir_linux(nome_impressora, codigo)

    def _imprimir_windows(self, nome_impressora: str, codigo: str) -> bool:
        """Envia código ZPL raw para impressora no Windows usando win32print."""
        try:
            import win32print
        except ImportError:
            QMessageBox.critical(
                self, "Erro",
                "Biblioteca 'pywin32' não encontrada.\n"
                "Instale com: pip install pywin32"
            )
            return False

        try:
            codigo_bytes = codigo.encode('utf-8')
            handle = win32print.OpenPrinter(nome_impressora)
            try:
                win32print.StartDocPrinter(handle, 1, ("ZPL Label", None, "RAW"))
                win32print.StartPagePrinter(handle)
                win32print.WritePrinter(handle, codigo_bytes)
                win32print.EndPagePrinter(handle)
                win32print.EndDocPrinter(handle)
            finally:
                win32print.ClosePrinter(handle)
            return True

        except Exception as e:
            print(f"Erro win32print: {e}")
            return False

    def _imprimir_linux(self, nome_impressora: str, codigo: str) -> bool:
        """Envia código ZPL raw para impressora no Linux via lp (CUPS)."""
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.zpl', delete=False, encoding='utf-8'
            ) as f:
                f.write(codigo)
                arquivo_temp = f.name

            resultado = subprocess.run(
                ['lp', '-d', nome_impressora, '-o', 'raw', arquivo_temp],
                capture_output=True, text=True, timeout=30
            )

            os.unlink(arquivo_temp)

            if resultado.returncode != 0:
                print(f"Erro lp: {resultado.stderr}")
                return False
            return True

        except FileNotFoundError:
            QMessageBox.critical(
                self, "Erro",
                "Comando 'lp' não encontrado. Instale o CUPS:\n"
                "sudo apt install cups"
            )
            return False
        except subprocess.TimeoutExpired:
            QMessageBox.warning(self, "Erro", "Tempo limite excedido ao enviar para impressora.")
            return False
        except Exception as e:
            print(f"Erro ao enviar ZPL: {e}")
            return False

    # --- Menu de contexto ---

    def _mostrar_menu_contexto(self, pos) -> None:
        """Exibe menu de contexto ao clicar com botão direito na tabela."""
        item = self.tableWidget.itemAt(pos)
        if item is None:
            return
        row = item.row()
        codigo_item = self.tableWidget.item(row, self.COL_OC)
        if codigo_item is None:
            return
        codigo = codigo_item.data(Qt.ItemDataRole.UserRole)
        if not codigo:
            return

        menu = QMenu(self.tableWidget)
        action = QAction("Visualizar código", menu)
        action.triggered.connect(partial(self._abrir_dialog_codigo, codigo))
        menu.addAction(action)
        menu.exec(self.tableWidget.mapToGlobal(pos))

    def _abrir_dialog_codigo(self, codigo: str) -> None:
        dlg = CodigoDialog(codigo, self)
        dlg.exec()


def main() -> None:
    app = QApplication(sys.argv)
    viewer = ZplViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
