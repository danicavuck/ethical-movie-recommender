from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import recommender.main


class WelcomePage(QWidget):
    nextClicked = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        title = QLabel("Welcome!")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        titleFont = QFont('Times New Roman')
        titleFont.setPointSize(40)
        titleFont.setBold(True)
        titleFont.setStretch(QFont.ExtraExpanded)
        title.setFont(titleFont)

        description = QLabel("""Welcome to DANICADB, demo for a movie recommendation platform that offers two régimes of functioning.\nUser can choose at any point which mode he wants to use to make better and more suited recommendation from himself/herself.\nThere is a more exploratory and more exploitative mode.""")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignJustify)
        descriptionFont = QFont('Times New Roman')
        descriptionFont.setPointSize(15)
        description.setFont(descriptionFont)

        button = QPushButton("Next")
        button.clicked.connect(self.nextClicked)
        button.setMinimumHeight(40)
        buttonFont = QFont()
        buttonFont.setPointSize(13)
        buttonFont.setBold(True)
        button.setFont(buttonFont)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(title)
        mainLayout.addWidget(description)
        mainLayout.addSpacerItem(QSpacerItem(0, 50))
        mainLayout.addWidget(button)
        mainLayout.addSpacerItem(QSpacerItem(0, 0))
        mainLayout.setStretch(mainLayout.count() - 1, 1)

        mainLayout.setContentsMargins(200, 50, 200, 100)
        self.setLayout(mainLayout)
