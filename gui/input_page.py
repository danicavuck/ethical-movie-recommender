from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui.toggle_switch import Switch

class InputPage(QWidget):
    idEntered = pyqtSignal(str)
    freeTextEntered = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        switch = Switch(track_radius=24, thumb_radius=20)
        switch.clicked.connect(self._onToggleSwitchChanged)
        switch.setChecked(True)
        switch.setMinimumWidth(125)

        self._idInputSubpage = self._initIdInputSubpage()
        self._freeTextInputSubpage = self._initFreeTextInputSubpage()

        self._pageStack = QStackedWidget()
        self._pageStack.addWidget(self._idInputSubpage)
        self._pageStack.addWidget(self._freeTextInputSubpage)
        self._onToggleSwitchChanged(switch.isChecked())

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(switch)
        mainLayout.addWidget(self._pageStack)
        mainLayout.addSpacerItem(QSpacerItem(0, 0))
        mainLayout.setStretch(mainLayout.count() - 1, 1)

        mainLayout.setContentsMargins(200, 50, 200, 100)
        self.setLayout(mainLayout)
    
    def onInvalidIdEntered(self, msg=None):
        self._idInputSubpage.showInvalidInputMessage(msg)

    def onInvalidFreeTextEntered(self, msg=None):
        self._freeTextInputSubpage.showInvalidInputMessage(msg)

    def _initIdInputSubpage(self):
        subpage = IdInputPage()
        subpage.inputEntered.connect(self.idEntered)
        return subpage
        
    def _initFreeTextInputSubpage(self):
        subpage = FreeTextInputPage()
        subpage.inputEntered.connect(self.freeTextEntered)
        return subpage
    
    def _onToggleSwitchChanged(self, on):
        if on:
            self._idInputSubpage.clear()
            self._pageStack.setCurrentWidget(self._idInputSubpage)
        else:
            self._freeTextInputSubpage.clear()
            self._pageStack.setCurrentWidget(self._freeTextInputSubpage)

class IdInputPage(QWidget):
    inputEntered = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        title = QLabel("Recommendation based on previous activity")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        titleFont = QFont()
        titleFont.setPointSize(15)
        titleFont.setBold(True)
        title.setFont(titleFont)

        description = QLabel("This is the mode of demo application that uses input users history aswell as history of other users on the platform into consideration to make recommendations.\n\nThis type of model is called collaborative filltering and it is more exploitative versus the other regime that uses free input text.\n\nIn the input text box below you should type in the ID of the user that you want to make recommendations for.""")
        description.setAlignment(Qt.AlignmentFlag.AlignJustify)
        description.setWordWrap(True)
        descriptionFont = QFont()
        descriptionFont.setPointSize(13)
        description.setFont(descriptionFont)
        
        self._input = QLineEdit()
        self._input.setValidator(QIntValidator(0, 2147483647))

        self._invalidInputLabel = QLabel()
        self._invalidInputLabel.setStyleSheet("color: red")
        self._invalidInputLabel.setHidden(True)

        inputEntryLayout = QFormLayout()
        inputEntryLayout.addRow("User ID:", self._input)
        inputEntryLayout.addRow(None, self._invalidInputLabel)

        acceptButton = QPushButton("Recommend")
        acceptButtonFont = QFont()
        acceptButtonFont.setPointSize(13)
        acceptButtonFont.setBold(True)
        acceptButton.setFont(acceptButtonFont)
        acceptButton.clicked.connect(self._onAcceptButtonClicked)
        acceptButton.setMinimumHeight(40)

        helpButton = QPushButton("Wanna know more?")
        helpButton.setStyleSheet("color: #2980b9; padding: 0")
        helpButton.setFlat(True)
        helpButton.clicked.connect(self._showHelp)

        helpLayout = QHBoxLayout()
        helpLayout.addWidget(helpButton)
        helpLayout.addSpacerItem(QSpacerItem(0, 0))
        helpLayout.setStretch(helpLayout.count() - 1, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(title)
        mainLayout.addWidget(description)
        mainLayout.addLayout(helpLayout)
        mainLayout.addSpacerItem(QSpacerItem(0, 50))
        mainLayout.addLayout(inputEntryLayout)
        mainLayout.addWidget(acceptButton)
        self.setLayout(mainLayout)
    
    def clear(self):
        self.hideInvalidInputMessage()
        self._input.clear()

    def showInvalidInputMessage(self, msg=None):
        if msg is None:
            self._invalidInputLabel.setText("Unknown user ID!")
        else:
            self._invalidInputLabel.setText(msg)
        self._invalidInputLabel.setVisible(True)
    
    def hideInvalidInputMessage(self):
        self._invalidInputLabel.setVisible(False)

    def _showHelp(self):
        msg = QMessageBox()
        msgFont = QFont('Times New Roman')
        msgFont.setPointSize(13)
        msg.setText("More details:")
        msg.setInformativeText("Collaborative filtering mode of the demo uses ratings and movies tables.\nFrom the ratings table user-item matrix is made.\nThen we used K-Nearest Neighbors algorithm to train the model with the matrix vectors as input data.\nK-Nearest Neighbor uses cosine similarity to calculate similarity between user vectors.\nAfter we found 6 most similar users you remove the user with the given id and remove the movie id-s from similar users vectors for the movies that the selected user has already watched.\nLast step is to recommend highly rated movies from the users with similar taste.")
        msg.setWindowTitle("Explained")
        msg.setFont(msgFont)
        msg.exec_()

    @pyqtSlot()
    def _onAcceptButtonClicked(self):
        self.inputEntered.emit(self._input.text())

class FreeTextInputPage(QWidget):
    inputEntered = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        title = QLabel("Recommendation based on free text input")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        titleFont = QFont()
        titleFont.setPointSize(15)
        titleFont.setBold(True)
        title.setFont(titleFont)

        description = QLabel("Idea behind this mode of the demo is to develop more of a chance for exploration of movies and to prevent bias creation.\nThis regime doesn't use users previous activity on the platform but just the text provided to make recommendations.\n\nUser should type in in the text box bellow words that come to mind about the movie he wants to see.\nHe/She is encouraged to use genres, release year approximation or just random words that could describe the movie,vibe or plot aswell as actors that he/she would like to see.\n\nSome examples of the most helpful input would be: comedy adam sandler, drama thriller, adventure family christmas, drugs drama, 2005 comedy, etc... """)
        description.setAlignment(Qt.AlignmentFlag.AlignJustify)
        description.setWordWrap(True)
        descriptionFont = QFont()
        descriptionFont.setPointSize(11)
        description.setFont(descriptionFont)

        self._input = QLineEdit()
        
        self._invalidInputLabel = QLabel()
        self._invalidInputLabel.setStyleSheet("color: red")
        self._invalidInputLabel.setHidden(True)

        inputEntryLayout = QFormLayout()
        inputEntryLayout.addRow("Free text entry:", self._input)
        inputEntryLayout.addRow(None, self._invalidInputLabel)

        acceptButton = QPushButton("Recommend")
        acceptButtonFont = QFont()
        acceptButtonFont.setPointSize(13)
        acceptButtonFont.setBold(True)
        acceptButton.setFont(acceptButtonFont)
        acceptButton.clicked.connect(self._onAcceptButtonClicked)
        acceptButton.setMinimumHeight(40)

        helpButton = QPushButton("Wanna know more?")
        helpButton.setStyleSheet("color: #2980b9; padding: 0")
        helpButton.setFlat(True)
        helpButton.clicked.connect(self._showHelp)

        helpLayout = QHBoxLayout()
        helpLayout.addWidget(helpButton)
        helpLayout.addSpacerItem(QSpacerItem(0, 0))
        helpLayout.setStretch(helpLayout.count() - 1, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(title)
        mainLayout.addWidget(description)
        mainLayout.addLayout(helpLayout)
        mainLayout.addSpacerItem(QSpacerItem(0, 50))
        mainLayout.addLayout(inputEntryLayout)
        mainLayout.addWidget(acceptButton)
        self.setLayout(mainLayout)
    
    def clear(self):
        self.hideInvalidInputMessage()
        self._input.clear()

    def showInvalidInputMessage(self, msg=None):
        if msg is None:
            self._invalidInputLabel.setText("Invalid input!")
        else:
            self._invalidInputLabel.setText(msg)
        self._invalidInputLabel.setVisible(True)
    
    def hideInvalidInputMessage(self):
        self._invalidInputLabel.setVisible(False)

    def _showHelp(self):
        msg = QMessageBox()
        msgFont = QFont('Times New Roman')
        msgFont.setPointSize(13)
        msg.setText("More details:")
        msg.setInformativeText( "This is content based recommendation because it uses information about the item(in our case a movie) to make most accurate recommendations.\nThis mode of the demo uses tags and movie datasets.\nPriority is set on tags because it is the most specific description of plot/feel/theme of the movie then it is filtrated also by genre and year.")
        msg.setWindowTitle("Explained")
        msg.setFont(msgFont)
        msg.exec_()

    @pyqtSlot()
    def _onAcceptButtonClicked(self):
        self.inputEntered.emit(self._input.text())
