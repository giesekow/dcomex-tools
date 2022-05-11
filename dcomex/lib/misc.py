from PyQt5.QtWidgets import QFrame

class QHLine(QFrame):
    def __init__(self, parent=None):
        super(QHLine, self).__init__(parent=parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVLine(QFrame):
    def __init__(self, parent=None):
        super(QVLine, self).__init__(parent=parent)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)