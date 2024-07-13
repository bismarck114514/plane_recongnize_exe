# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore
import sqlite3
import hashlib
import re

class ResetPasswordWindow(QtWidgets.QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.initUI()

    def initUI(self):
        self.setFixedSize(1280, 720)  # 设置窗口大小
        self.setWindowTitle('重置密码')
        self.center()

        layout = QtWidgets.QVBoxLayout()

        formLayout = QtWidgets.QFormLayout()

        self.usernameInput = QtWidgets.QLineEdit(self)
        self.usernameInput.setFixedSize(320, 60)  # 16:3 ratio
        self.usernameInput.editingFinished.connect(self.check_username)
        self.usernameError = QtWidgets.QLabel('', self)
        self.usernameError.setStyleSheet('color: red')

        self.phoneInput = QtWidgets.QLineEdit(self)
        self.phoneInput.setFixedSize(320, 60)  # 16:3 ratio
        self.phoneInput.editingFinished.connect(self.check_phone)
        self.phoneError = QtWidgets.QLabel('', self)
        self.phoneError.setStyleSheet('color: red')

        self.emailInput = QtWidgets.QLineEdit(self)
        self.emailInput.setFixedSize(320, 60)  # 16:3 ratio
        self.emailInput.editingFinished.connect(self.check_email)
        self.emailError = QtWidgets.QLabel('', self)
        self.emailError.setStyleSheet('color: red')

        self.newPasswordInput = QtWidgets.QLineEdit(self)
        self.newPasswordInput.setFixedSize(320, 60)  # 16:3 ratio
        self.newPasswordInput.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmPasswordInput = QtWidgets.QLineEdit(self)
        self.confirmPasswordInput.setFixedSize(320, 60)  # 16:3 ratio
        self.confirmPasswordInput.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmPasswordInput.editingFinished.connect(self.check_password_match)
        self.passwordError = QtWidgets.QLabel('', self)
        self.passwordError.setStyleSheet('color: red')

        formLayout.addRow(QtWidgets.QLabel('用户名:'), self.usernameInput)
        formLayout.addRow(self.usernameError)
        formLayout.addRow(QtWidgets.QLabel('手机号:'), self.phoneInput)
        formLayout.addRow(self.phoneError)
        formLayout.addRow(QtWidgets.QLabel('邮箱:'), self.emailInput)
        formLayout.addRow(self.emailError)
        formLayout.addRow(QtWidgets.QLabel('新密码:'), self.newPasswordInput)
        formLayout.addRow(QtWidgets.QLabel('确认新密码:'), self.confirmPasswordInput)
        formLayout.addRow(self.passwordError)

        layout.addLayout(formLayout)

        buttonLayout = QtWidgets.QHBoxLayout()
        self.resetButton = QtWidgets.QPushButton('重置密码', self)
        self.resetButton.setFixedSize(160, 90)  # 16:9 ratio
        self.resetButton.clicked.connect(self.reset_password)
        self.backButton = QtWidgets.QPushButton('返回', self)
        self.backButton.setFixedSize(160, 90)  # 16:9 ratio
        self.backButton.clicked.connect(self.go_back)

        buttonLayout.addWidget(self.resetButton)
        buttonLayout.addWidget(self.backButton)

        layout.addLayout(buttonLayout)

        layout.setAlignment(QtCore.Qt.AlignCenter)  # 居中布局
        self.setLayout(layout)

    def center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

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

    def check_password_match(self):
        password = self.newPasswordInput.text()
        confirm_password = self.confirmPasswordInput.text()

        if password != confirm_password:
            self.passwordError.setText('两次输入密码不一致')
        else:
            self.passwordError.setText('')

    def check_phone(self):
        phone = self.phoneInput.text()
        if not re.match(r"^1\d{10}$", phone):
            self.phoneError.setText('手机号格式错误')
            return

    def check_email(self):
        email = self.emailInput.text()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email) or not email.endswith('.com'):
            self.emailError.setText('邮箱格式错误')
            return

    def reset_password(self):
        username = self.usernameInput.text()
        phone = self.phoneInput.text()
        email = self.emailInput.text()
        new_password = self.newPasswordInput.text()
        confirm_password = self.confirmPasswordInput.text()

        if new_password != confirm_password:
            self.passwordError.setText('两次输入密码不一致')
            return

        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

        conn = sqlite3.connect('db/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        result = cursor.fetchone()

        if result:
            cursor.execute("SELECT * FROM users WHERE phone=? AND email=?", (phone, email))
            result = cursor.fetchone()

            if result:
                cursor.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, username))
                conn.commit()
                QtWidgets.QMessageBox.information(self, '成功', '密码重置成功')
                self.go_back()
            else:
                self.phoneError.setText('手机号或邮箱不匹配')
        else:
            self.usernameError.setText('账号不存在')

        conn.close()

    def go_back(self):
        self.login_window.show()
        self.close()
