from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui.movie_list import MovieList
from gui.movie_recommender import MovieRecommender
from gui.movie_lookup import MovieLookup

MOVIES_PER_PAGE = 5

class ResultPage(QWidget):
    back = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # pozadinski
        
        self._recommender = MovieRecommender()
        self._recommender.finished.connect(self._onRecommendationFinished)
        self._recommendedMovies = []
        self._recommendedMovieStartIndex = 0

        self._lookup = MovieLookup()
        self._lookup.finished.connect(self._onMovieLookupFinished)

        # UI

        buttonFont = QFont()
        buttonFont.setPointSize(12)

        self._prevButton = QPushButton("<")
        self._prevButton.clicked.connect(self._onPrevButtonClicked)
        self._prevButton.setMinimumSize(40, 40)
        self._prevButton.setVisible(False)
        self._prevButton.setFont(buttonFont)

        self._nextButton = QPushButton(">")
        self._nextButton.clicked.connect(self._onNextButtonClicked)
        self._nextButton.setMinimumSize(40, 40)
        self._nextButton.setVisible(False)
        self._nextButton.setFont(buttonFont)

        menuLayout = QHBoxLayout()
        menuLayout.addWidget(self._prevButton)
        menuLayout.addSpacerItem(QSpacerItem(0, 0))
        menuLayout.setStretch(menuLayout.count() - 1, 1)
        menuLayout.addWidget(self._nextButton)

        self._waitSubpage = self._initWaitSubpage()
        self._movieSubpage = self._initMovieSubpage()

        self._pageStack = QStackedWidget()
        self._pageStack.addWidget(self._waitSubpage)
        self._pageStack.addWidget(self._movieSubpage)

        button = QPushButton("Back")
        button.clicked.connect(self.back)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(menuLayout)
        mainLayout.addWidget(self._pageStack)
        mainLayout.addWidget(button)
        self.setLayout(mainLayout)

    def _initWaitSubpage(self):
        page = WaitPage()
        return page
    
    def _initMovieSubpage(self):
        page = MovieList()
        return page

    def recommendById(self, id):
        self._waitSubpage.startAnimation()
        self._pageStack.setCurrentWidget(self._waitSubpage)
        self._recommender.start(id=id)

    def recommendByFreeText(self, freeText):
        self._waitSubpage.startAnimation()
        self._pageStack.setCurrentWidget(self._waitSubpage)
        self._recommender.start(freeText=freeText)

    @pyqtSlot()
    def _onRecommendationFinished(self):
        self._recommendedMovies = self._recommender.results()
        self._recommendedMovieStartIndex = 0

        if len(self._recommendedMovies) == 0:
            # there's something for everyone
            self._recommendedMovies.append('0110912')
        
        movieSubset = self._recommendedMovies[self._recommendedMovieStartIndex : self._recommendedMovieStartIndex + MOVIES_PER_PAGE]
        self._lookup.start(movieSubset)

    @pyqtSlot()
    def _onMovieLookupFinished(self):
        results = self._lookup.results()
        self._movieSubpage.clear()
        for movie in results:
            self._movieSubpage.add(
                title=movie['title'],
                description=movie['description'],
                image=movie['image'],
                url=movie['url']
            )


        if self._recommendedMovieStartIndex > 0:
            self._prevButton.setVisible(True)
        else:
            self._prevButton.setVisible(False)

        if self._recommendedMovieStartIndex + MOVIES_PER_PAGE < len(self._recommendedMovies):
            self._nextButton.setVisible(True)
        else:
            self._nextButton.setVisible(False)

        self._pageStack.setCurrentWidget(self._movieSubpage)
        self._waitSubpage.stopAnimation()
   
    def _onPrevButtonClicked(self):
        self._prevButton.setVisible(False)
        self._nextButton.setVisible(False)

        self._waitSubpage.startAnimation()
        self._pageStack.setCurrentWidget(self._waitSubpage)
        
        self._recommendedMovieStartIndex -= MOVIES_PER_PAGE
        movieSubset = self._recommendedMovies[self._recommendedMovieStartIndex : self._recommendedMovieStartIndex + MOVIES_PER_PAGE]
        self._lookup.start(movieSubset)
        
    def _onNextButtonClicked(self):
        self._prevButton.setVisible(False)
        self._nextButton.setVisible(False)

        self._waitSubpage.startAnimation()
        self._pageStack.setCurrentWidget(self._waitSubpage)
        
        self._recommendedMovieStartIndex += MOVIES_PER_PAGE
        movieSubset = self._recommendedMovies[self._recommendedMovieStartIndex : self._recommendedMovieStartIndex + MOVIES_PER_PAGE]
        self._lookup.start(movieSubset)

class WaitPage(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._pixmap = QPixmap(QImage('images/loading.png'))
        self._pixmap = self._pixmap.scaledToHeight(300, Qt.TransformationMode.SmoothTransformation)

        self._timerId = None

        self._label = QLabel()
        self._label.setPixmap(self._pixmap)

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(self._label)
        self.setLayout(mainLayout)

    def startAnimation(self):
        self._timerId = self.startTimer(100)
    
    def stopAnimation(self):
        if self._timerId:
            self.killTimer(self._timerId)
    
    def timerEvent(self, _):
        transform = QTransform()
        transform.rotate(90)
        self._pixmap = self._pixmap.transformed(transform)
        self._label.setPixmap(self._pixmap)
