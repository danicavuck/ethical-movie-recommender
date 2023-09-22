from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from imdb import IMDb
import urllib

class MovieLookupWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, output, index, id, parent=None):
        super().__init__(parent)
        self.output = output
        self.index = index
        self.id = id
    
    @pyqtSlot()
    def run(self):
        ia = IMDb()
        movie = ia.get_movie(self.id)

        try:
            with urllib.request.urlopen(movie['full-size cover url']) as urlObj:
                imageData = urlObj.read()
            poster = QPixmap()
            poster.loadFromData(imageData, "jpeg")
        except:
            poster = QPixmap()

        if 'title' in movie:
            title = movie['title']
        else:
            title = '?'

        if 'plot outline' in movie:
            description = movie['plot outline']
        else:
            description = '?'

        #id nije fiksne duzine mora se left-paddovati nulama da bi otvorilo stranicu
        id = str(self.id).zfill(7)

        self.output[self.index] = {
            'title': title,
            'description': description,
            'image': poster,
            'url': 'https://www.imdb.com/title/tt'+id
        }

        self.finished.emit()

class MovieLookup(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._threads = []
        self._workers = []
        self._finishedCount = 0
        self._output = None
    
    def start(self, ids):
        self._output = [None] * len(ids)
        self._finishedCount = 0

        for i in range(len(ids)):
            worker = MovieLookupWorker(self._output, i, ids[i])
            self._workers.append(worker)
            
            thread = QThread()
            thread.started.connect(worker.run)
            thread.finished.connect(self._onSingleLookupFinished)
            worker.finished.connect(thread.quit)
            self._threads.append(thread)

            worker.moveToThread(thread)
            thread.start()
    
    def results(self):
        return self._output

    @pyqtSlot()
    def _onSingleLookupFinished(self):
        self._finishedCount += 1
        if self._finishedCount == len(self._threads):
            self._threads = []
            self._workers = []
            self.finished.emit()
