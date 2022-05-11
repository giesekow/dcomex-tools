def showGui():
  from PyQt5.QtWidgets import QApplication
  from lib.mainwindow import MainWindow

  app = QApplication([])
  window = MainWindow()
  window.showMaximized()
  app.exec()