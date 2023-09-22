#!/usr/bin/env python3

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui.welcome_page import WelcomePage
from gui.input_page import InputPage
from gui.result_page import ResultPage

from recommender.main import is_valid_user

class MainForm(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("DANICADb")
        self.setWindowIcon(QIcon('images/icon.png'))
            
        logoPixmap = QPixmap('images/danicadb.png')
        logoPixmap = logoPixmap.scaledToHeight(40, Qt.TransformationMode.SmoothTransformation)
        logo = QLabel()
        logo.setPixmap(logoPixmap)
        
        menuLayout = QHBoxLayout()
        menuLayout.addWidget(logo)
        menuLayout.addSpacerItem(QSpacerItem(0, 0))
        menuLayout.setStretch(menuLayout.count() - 1, 1)

        self.welcomePage = self.initWelcomePage()
        self.inputPage = self.initInputPage()
        self.resultPage = self.initResultPage()

        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.welcomePage)
        self.stackedWidget.addWidget(self.inputPage)
        self.stackedWidget.addWidget(self.resultPage)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(menuLayout)
        mainLayout.addSpacerItem(QSpacerItem(0, 10))
        mainLayout.addWidget(self.stackedWidget, stretch=1)
        self.setLayout(mainLayout)

    def initWelcomePage(self):
        page = WelcomePage()
        page.nextClicked.connect(self.welcomePage_onNextClicked)
        return page
    
    @pyqtSlot()
    def welcomePage_onNextClicked(self):
        self.stackedWidget.setCurrentWidget(self.inputPage)
    
    def initInputPage(self):
        page = InputPage()
        page.idEntered.connect(self.inputPage_onIdEntered)
        page.freeTextEntered.connect(self.inputPage_onFreeTextEntered)
        return page
    
    @pyqtSlot(str)
    def inputPage_onIdEntered(self, id):
        if id != "" and is_valid_user(id):
            self.resultPage.recommendById(id)
            self.stackedWidget.setCurrentWidget(self.resultPage)
        else:
            self.inputPage.onInvalidIdEntered()
    
    @pyqtSlot(str)
    def inputPage_onFreeTextEntered(self, text):
        if text == "":
            self.inputPage.onInvalidFreeTextEntered()
        else:
            self.resultPage.recommendByFreeText(text)
            self.stackedWidget.setCurrentWidget(self.resultPage)
    
    def initResultPage(self):
        page = ResultPage()
        page.back.connect(lambda: self.stackedWidget.setCurrentWidget(self.welcomePage))
        return page

if __name__ == '__main__':
    qApp.setStyle(QStyleFactory.create("Fusion"))

    newPalette = QPalette()
    newPalette.setColor(QPalette.Window,          QColor( 37,  37,  37))
    newPalette.setColor(QPalette.WindowText,      QColor(212, 212, 212))
    newPalette.setColor(QPalette.Base,            QColor( 60,  60,  60))
    newPalette.setColor(QPalette.AlternateBase,   QColor( 45,  45,  45))
    newPalette.setColor(QPalette.PlaceholderText, QColor(127, 127, 127))
    newPalette.setColor(QPalette.Text,            QColor(212, 212, 212))
    # newPalette.setColor(QPalette.Link,            QColor(255, 255, 0))
    newPalette.setColor(QPalette.Button,          QColor( 45,  45,  45))
    newPalette.setColor(QPalette.ButtonText,      QColor(212, 212, 212))
    newPalette.setColor(QPalette.BrightText,      QColor(240, 240, 240))
    newPalette.setColor(QPalette.Highlight,       QColor( 38,  79, 120))
    newPalette.setColor(QPalette.HighlightedText, QColor(240, 240, 240))

    newPalette.setColor(QPalette.Light,           QColor( 60,  60,  60))
    newPalette.setColor(QPalette.Midlight,        QColor( 52,  52,  52))
    newPalette.setColor(QPalette.Dark,            QColor( 30,  30,  30) )
    newPalette.setColor(QPalette.Mid,             QColor( 37,  37,  37))
    newPalette.setColor(QPalette.Shadow,          QColor( 0,    0,   0))

    app = QApplication(sys.argv)
    app.setPalette(newPalette)

    form = MainForm()
    form.show()

    app.exec_()
