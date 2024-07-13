# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore

class ImageWindow(QtWidgets.QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.initUI()

    def initUI(self):
        self.setWindowTitle('图片查看器')
        layout = QtWidgets.QVBoxLayout()

        self.imageLabel = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap(self.image_path)
        self.imageLabel.setPixmap(pixmap.scaled(800, 600, QtCore.Qt.KeepAspectRatio))

        layout.addWidget(self.imageLabel)
        self.setLayout(layout)

        self.setFixedSize(800, 600)  # 可根据需要调整窗口大小
