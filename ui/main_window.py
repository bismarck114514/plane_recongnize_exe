# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore
from model import AirplaneClassifier
import sqlite3
import torch
import os
from ui.image_window import ImageWindow  # 确保导入 ImageWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()
        self.history_displayed = False  # 标记历史记录是否显示过
        self.anchorClickedConnected = False  # 标记是否已连接 anchorClicked 信号

    def initUI(self):
        self.setFixedSize(1280, 720)  # 设置窗口大小
        self.setWindowTitle('飞机分类器')
        self.center()

        # 创建主布局
        mainLayout = QtWidgets.QHBoxLayout()

        # 左侧布局
        leftLayout = QtWidgets.QVBoxLayout()

        formLayout = QtWidgets.QFormLayout()

        self.imagePathInput = QtWidgets.QLineEdit(self)
        self.imagePathInput.setFixedSize(320, 60)  # 16:3 ratio
        self.browseButton = QtWidgets.QPushButton('浏览', self)
        self.browseButton.setFixedSize(160, 90)  # 16:9 ratio
        self.browseButton.clicked.connect(self.browse_file)
        formLayout.addRow(QtWidgets.QLabel('图片路径:'), self.imagePathInput)
        formLayout.addRow(self.browseButton)

        leftLayout.addLayout(formLayout)

        self.classifyButton = QtWidgets.QPushButton('分类', self)
        self.classifyButton.setFixedSize(160, 90)  # 16:9 ratio
        self.classifyButton.clicked.connect(self.classify_file)
        leftLayout.addWidget(self.classifyButton)

        self.viewImageButton = QtWidgets.QPushButton('查看图片', self)
        self.viewImageButton.setFixedSize(160, 90)  # 16:9 ratio
        self.viewImageButton.clicked.connect(self.view_image)
        leftLayout.addWidget(self.viewImageButton)

        self.historyButton = QtWidgets.QPushButton('查看历史记录', self)
        self.historyButton.setFixedSize(160, 90)  # 16:9 ratio
        self.historyButton.clicked.connect(self.show_history)
        leftLayout.addWidget(self.historyButton)

        self.logoutButton = QtWidgets.QPushButton('退出登录', self)
        self.logoutButton.setFixedSize(160, 90)  # 16:9 ratio
        self.logoutButton.clicked.connect(self.logout)
        leftLayout.addWidget(self.logoutButton)

        # 右侧布局
        rightLayout = QtWidgets.QVBoxLayout()
        self.resultsText = QtWidgets.QTextBrowser(self)
        rightLayout.addWidget(self.resultsText)

        # 将左侧和右侧布局添加到主布局
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)

        # 设置主窗口布局
        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def browse_file(self):
        try:
            file_path = QtWidgets.QFileDialog.getOpenFileName(self, '选择图片', '', 'Images (*.png *.xpm *.jpg *.jpeg *.bmp)')[0]
            self.imagePathInput.setText(file_path)
            if self.history_displayed:
                self.resultsText.clear()  # 仅在历史记录已显示时清空结果显示框
                self.history_displayed = False
        except Exception as e:
            self.resultsText.setText(f"出现错误：{str(e)}")

    def view_image(self):
        try:
            image_path = self.imagePathInput.text()
            if os.path.exists(image_path):
                image_viewer = ImageWindow(image_path)
                image_viewer.exec_()
            else:
                self.resultsText.setText('找不到图片: ' + image_path)
        except Exception as e:
            self.resultsText.setText(f"查看图片时出现错误：{str(e)}")

    def classify_file(self):
        try:
            image_path = self.imagePathInput.text()
            if image_path:
                classifier = AirplaneClassifier('airplane_classifier_vgg16.pth', 3, torch.device("cpu"))  # 强制使用 CPU
                prediction, probabilities = classifier.predict_image(image_path)
                predicted_class = classifier.class_names[prediction]

                result_text = f'{image_path}: {predicted_class}'
                self.resultsText.setText(result_text)
                self.store_operation(image_path, predicted_class)

                self.history_displayed = False  # 进行新检测后清除历史记录显示标记
        except Exception as e:
            self.resultsText.setText(f"分类图片时出现错误：{str(e)}")

    def store_operation(self, image_path, result_text):
        try:
            conn = sqlite3.connect('db/database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO operations (username, image_path, result) VALUES (?, ?, ?)",
                           (self.username, image_path, result_text))
            conn.commit()
            conn.close()
        except Exception as e:
            self.resultsText.setText(f"存储操作时出现错误：{str(e)}")

    def show_history(self):
        try:
            conn = sqlite3.connect('db/database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT image_path, result FROM operations WHERE username=?", (self.username,))
            result = cursor.fetchall()
            conn.close()

            self.resultsText.clear()
            if result:
                for row in result:
                    image_path, result_text = row
                    self.resultsText.append(f"{image_path}: {result_text}<br><a href='{image_path}'>查看图片</a>")
                self.resultsText.setOpenExternalLinks(False)  # 确保链接在应用内处理

                if not self.anchorClickedConnected:
                    self.resultsText.anchorClicked.connect(self.handle_url_click)
                    self.anchorClickedConnected = True  # 标记已连接

                self.history_displayed = True  # 标记历史记录已显示
            else:
                self.resultsText.setText('暂无历史记录')
                self.history_displayed = True  # 标记历史记录已显示
        except Exception as e:
            self.resultsText.setText(f"显示历史记录时出现错误：{str(e)}")

    def handle_url_click(self, url):
        self.view_image_by_url(url.toString())

    def view_image_by_url(self, image_path):
        try:
            if os.path.exists(image_path):
                image_viewer = ImageWindow(image_path)
                image_viewer.exec_()
            else:
                self.resultsText.setText('找不到图片: ' + image_path)
        except Exception as e:
            self.resultsText.setText(f"查看图片时出现错误：{str(e)}")

    def logout(self):
        self.close()
        from ui.login_window import LoginWindow  # 在方法内部导入避免循环依赖
        self.login_window = LoginWindow()
        self.login_window.show()
