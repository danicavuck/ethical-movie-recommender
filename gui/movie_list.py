from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MovieList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        scrollArea = QScrollArea()
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollArea.setWidgetResizable(True)
        
        scrollWidget = QWidget()
        scrollArea.setWidget(scrollWidget)

        self._scrollLayout = QVBoxLayout()
        self._scrollLayout.setContentsMargins(0, 0, 0, 0)
        self._scrollLayout.setSpacing(10)
        scrollWidget.setLayout(self._scrollLayout)

        # Add a dummy widget with stretch that's always at the bottom of the layout
        # This makes the remaining widgets packed compactly
        self._scrollLayout.addSpacerItem(QSpacerItem(0, 0))
        self._scrollLayout.setStretch(0, 1)

        containerLayout = QVBoxLayout()
        containerLayout.setContentsMargins(0, 0, 0, 0)
        containerLayout.setSpacing(0)
        containerLayout.addWidget(scrollArea)
        self.setLayout(containerLayout)

    def clear(self):
        while self._scrollLayout.count() > 1:
            item = self._scrollLayout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()

    def add(self, title, description, image, url):
        movie = MovieView(
            title=title,
            image_pixmap=image,
            description=description,
            url=url)
        # Insert before spacer
        self._scrollLayout.insertWidget(self._scrollLayout.count() - 1, movie)
        
class MovieView(QWidget):
    def __init__(self, title, image_pixmap, url, description, parent=None):
        super().__init__(parent)

        imageHeight = 200
        imageToDescriptionSpacing = 20
        titleToDescriptionSpacing = 10
        marginToBorder = 10
        
        self.setStyleSheet("""
        MovieView {
            border: 1px solid;
            background-color: rgb(30, 30, 30);
        }
        """)

        image = QLabel()
        pixmap = image_pixmap.scaledToHeight(imageHeight,  Qt.TransformationMode.SmoothTransformation)
        image.setPixmap(pixmap)

        title = QLabel(f"<a style=text-decoration:none href=\"{url}\">{title}</a>")
        title.setTextFormat(Qt.TextFormat.RichText)
        title.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        title.setOpenExternalLinks(True)
        titleFont = QFont()
        titleFont.setPointSize(16)
        titleFont.setBold(True)
        title.setFont(titleFont)

        description = QLabel(description)
        description.setAlignment(Qt.AlignmentFlag.AlignTop)
        description.setWordWrap(True)

        descriptionLayout = QVBoxLayout()
        descriptionLayout.setContentsMargins(0, 0, 0, 0)
        descriptionLayout.setSpacing(titleToDescriptionSpacing)
        descriptionLayout.addWidget(title)
        descriptionLayout.addWidget(description, stretch=1)

        layout = QHBoxLayout()
        layout.setContentsMargins(marginToBorder, marginToBorder, marginToBorder, marginToBorder)
        layout.setSpacing(imageToDescriptionSpacing)
        layout.addWidget(image)
        layout.addLayout(descriptionLayout, stretch=1)
        self.setLayout(layout)
    
    # Required for stylesheets to work on MovieView widget
    def paintEvent(self, pe):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        s = self.style()
        s.drawPrimitive(QStyle.PE_Widget, opt, p, self)