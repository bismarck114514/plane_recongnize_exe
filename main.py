# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets, QtGui
from ui.login_window import LoginWindow
import sqlite3
import hashlib
import os


def init_db():
    if not os.path.exists('db'):
        os.makedirs('db')
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            image_path TEXT NOT NULL,
            result TEXT NOT NULL,
            operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO users (username, password, phone, email) VALUES ('admin', ?, '', '')",
                       (hashlib.sha256('admin'.encode()).hexdigest(),))
    conn.commit()
    conn.close()



if __name__ == "__main__":
    init_db()  # 初始化数据库
    app = QtWidgets.QApplication(sys.argv)

    # 设置全局字体
    font = QtGui.QFont('SimSun', 12)  # 使用SimSun字体以确保支持中文显示
    app.setFont(font)

    loginWindow = LoginWindow()
    loginWindow.show()
    sys.exit(app.exec_())
