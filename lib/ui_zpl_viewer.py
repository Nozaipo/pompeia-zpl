# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'zpl_viewer.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_ZplViewer(object):
    def setupUi(self, ZplViewer):
        if not ZplViewer.objectName():
            ZplViewer.setObjectName(u"ZplViewer")
        ZplViewer.resize(850, 600)
        self.verticalLayout = QVBoxLayout(ZplViewer)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(12, 12, 12, 12)
        self.barraLayout = QHBoxLayout()
        self.barraLayout.setSpacing(5)
        self.barraLayout.setObjectName(u"barraLayout")
        self.barraLayout.setContentsMargins(9, 9, 9, 9)
        self.labelPesquisar = QLabel(ZplViewer)
        self.labelPesquisar.setObjectName(u"labelPesquisar")

        self.barraLayout.addWidget(self.labelPesquisar)

        self.searchEdit = QLineEdit(ZplViewer)
        self.searchEdit.setObjectName(u"searchEdit")

        self.barraLayout.addWidget(self.searchEdit)

        self.labelFiltro = QLabel(ZplViewer)
        self.labelFiltro.setObjectName(u"labelFiltro")

        self.barraLayout.addWidget(self.labelFiltro)

        self.filterCombo = QComboBox(ZplViewer)
        self.filterCombo.setObjectName(u"filterCombo")

        self.barraLayout.addWidget(self.filterCombo)

        self.btnAbrir = QPushButton(ZplViewer)
        self.btnAbrir.setObjectName(u"btnAbrir")

        self.barraLayout.addWidget(self.btnAbrir)

        self.btnImprimir = QPushButton(ZplViewer)
        self.btnImprimir.setObjectName(u"btnImprimir")

        self.barraLayout.addWidget(self.btnImprimir)


        self.verticalLayout.addLayout(self.barraLayout)

        self.tableWidget = QTableWidget(ZplViewer)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setStyleSheet(u"QTableWidget::item {\n"
"    padding: 4px 8px;\n"
"}\n"
"QTableWidget::item:selected {\n"
"    background-color: #0078D4;\n"
"    color: white;\n"
"}")

        self.verticalLayout.addWidget(self.tableWidget)

        self.footerLabel = QLabel(ZplViewer)
        self.footerLabel.setObjectName(u"footerLabel")
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.verticalLayout.addWidget(self.footerLabel)


        self.retranslateUi(ZplViewer)

        QMetaObject.connectSlotsByName(ZplViewer)
    # setupUi

    def retranslateUi(self, ZplViewer):
        ZplViewer.setWindowTitle(QCoreApplication.translate("ZplViewer", u"Visualizador de C\u00f3digos ZPL", None))
        self.labelPesquisar.setText(QCoreApplication.translate("ZplViewer", u"Pesquisar:", None))
        self.searchEdit.setPlaceholderText(QCoreApplication.translate("ZplViewer", u"Pesquisar por campo...", None))
        self.labelFiltro.setText(QCoreApplication.translate("ZplViewer", u"Filtro:", None))
        self.btnAbrir.setText(QCoreApplication.translate("ZplViewer", u"Escolher arquivo", None))
        self.btnImprimir.setText(QCoreApplication.translate("ZplViewer", u"Enviar para impressora", None))
        self.footerLabel.setText(QCoreApplication.translate("ZplViewer", u"Itens identificados: 0", None))
    # retranslateUi

