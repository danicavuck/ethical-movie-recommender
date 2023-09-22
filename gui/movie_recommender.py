from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from recommender.main import content_based_filtering, collaborative_filtering

class MovieRecommenderWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, output, id, freeText, parent=None):
        super().__init__(parent)
        self.output = output
        self.id = id
        self.freeText = freeText

    #neko od spolja poziva ovo
    #vracam listu id-eva za filmove
    #proveravam iz koje funkcije se vraca aka koji mod se koristio
    #dajem signal da je worker nasao filmove
    @pyqtSlot()
    def run(self):
        if self.id is not None:
            ids = collaborative_filtering(self.id)
        elif self.freeText is not None:
            ids = content_based_filtering(self.freeText)
        
        for id in ids:
            self.output.append(id)
        self.finished.emit()

class MovieRecommender(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._worker = None
        self._output = None
    
    def start(self, id=None, freeText=None):
        self._output = []

        self._worker = MovieRecommenderWorker(self._output, id, freeText)
            
        self._thread = QThread()
        #zakaci workera na thread
        #kad se to obavi reci da je gotov i quituj
        self._thread.started.connect(self._worker.run)
        self._thread.finished.connect(self._onWorkerFinished)
        self._worker.finished.connect(self._thread.quit)

        self._worker.moveToThread(self._thread)
        self._thread.start()
    
    def results(self):
        return self._output

    @pyqtSlot()
    def _onWorkerFinished(self):
        self._thread = None
        self._worker = None
        self.finished.emit()
