# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore
import sqlite3
import hashlib
import re
import time


class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.failed_attempts = 0
        self.locked_until = None
        self.initUI()

    def initUI(self):
        self.setFixedSize(1280, 720)  # 设置窗口大小
        self.setWindowTitle('登录')
        self.center()

        layout = QtWidgets.QVBoxLayout()

        formLayout = QtWidgets.QFormLayout()

        self.usernameInput = QtWidgets.QLineEdit(self)
        self.usernameInput.setFixedSize(320, 60)  # 16:3 ratio
        self.usernameInput.editingFinished.connect(self.check_username)
        self.usernameError = QtWidgets.QLabel('', self)
        self.usernameError.setStyleSheet('color: red')

        self.passwordInput = QtWidgets.QLineEdit(self)
        self.passwordInput.setFixedSize(320, 60)  # 16:3 ratio
        self.passwordInput.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordInput.editingFinished.connect(self.check_password)
        self.passwordError = QtWidgets.QLabel('', self)
        self.passwordError.setStyleSheet('color: red')

        formLayout.addRow(QtWidgets.QLabel('用户名:'), self.usernameInput)
        formLayout.addRow(self.usernameError)
        formLayout.addRow(QtWidgets.QLabel('密码:'), self.passwordInput)
        formLayout.addRow(self.passwordError)

        layout.addLayout(formLayout)

        buttonLayout = QtWidgets.QHBoxLayout()
        self.loginButton = QtWidgets.QPushButton('登录', self)
        self.loginButton.setFixedSize(160, 90)  # 16:9 ratio
        self.loginButton.clicked.connect(self.login)
        self.registerButton = QtWidgets.QPushButton('注册', self)
        self.registerButton.setFixedSize(160, 90)  # 16:9 ratio
        self.registerButton.clicked.connect(self.show_register)
        self.forgotPasswordButton = QtWidgets.QPushButton('忘记密码', self)
        self.forgotPasswordButton.setFixedSize(160, 90)  # 16:9 ratio
        self.forgotPasswordButton.clicked.connect(self.show_reset_password)

        buttonLayout.addWidget(self.loginButton)
        buttonLayout.addWidget(self.registerButton)
        buttonLayout.addWidget(self.forgotPasswordButton)

        layout.addLayout(buttonLayout)

        layout.setAlignment(QtCore.Qt.AlignCenter)  # 居中布局
        self.setLayout(layout)

    def center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def login(self):
        if self.locked_until and time.time() < self.locked_until:
            QtWidgets.QMessageBox.warning(self, '错误', '账户被锁定，请稍后再试')
            return

        username = self.usernameInput.text()
        password = self.passwordInput.text()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('db/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result is None:
            self.usernameError.setText('账号不存在')
        elif result[0] != hashed_password:
            self.failed_attempts += 1
            self.passwordError.setText('密码错误')
            if self.failed_attempts >= 5:
                self.locked_until = time.time() + 60  # 锁定1分钟
                self.failed_attempts = 0
                QtWidgets.QMessageBox.warning(self, '错误', '密码错误次数过多，账户被锁定1分钟')
        else:
            self.failed_attempts = 0
            self.usernameError.setText('')
            self.passwordError.setText('')
            from ui.main_window import MainWindow  # 在方法内部导入避免循环依赖
            self.mainWindow = MainWindow(username)
            self.mainWindow.show()
            self.close()

    def show_register(self):
        from ui.register_window import RegisterWindow  # 在方法内部导入避免循环依赖
        self.registerWindow = RegisterWindow(self)
        self.registerWindow.show()
        self.close()

    def show_reset_password(self):
        from ui.reset_password_window import ResetPasswordWindow  # 在方法内部导入避免循环依赖
        self.resetPasswordWindow = ResetPasswordWindow(self)
        self.resetPasswordWindow.show()
        self.close()

    def check_username(self):
        username = self.usernameInput.text()
        conn = sqlite3.connect('db/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            self.usernameError.setText('账号不存在')
        else:
            self.usernameError.setText('')

    def check_password(self):
        self.passwordError.setText('')
