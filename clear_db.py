import sqlite3

def clean_db():
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS operations")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    clean_db()
    print("数据库清理完成")
