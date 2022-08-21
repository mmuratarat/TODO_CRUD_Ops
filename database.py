import sqlite3

db_file = "myDatabase_TODO.db"
connection = sqlite3.connect(db_file)
cursor = connection.cursor()

def drop_create_table():
    cursor.execute('DROP TABLE IF EXISTS TODO_TABLE;')
    cursor.execute('CREATE TABLE IF NOT EXISTS TODO_TABLE(task_ TEXT NOT NULL UNIQUE, status_ NOT NULL, date_ DATE NOT NULL, PRIMARY KEY (task_))')

def create_table():
    # cursor.execute('DROP TABLE IF EXISTS TODO_TABLE;')
    cursor.execute('CREATE TABLE IF NOT EXISTS TODO_TABLE(task_ TEXT NOT NULL UNIQUE, status_ NOT NULL, date_ DATE NOT NULL, PRIMARY KEY (task_))')
    
def insert_data(task_, status_, date_):
    cursor.execute("INSERT INTO TODO_TABLE(task_, status_, date_) VALUES (?, ?, ?)", (task_, status_, date_)) # Always use the format YYYY-MM-DD to insert the date into database.
    connection.commit()
    
def show_data():
    cursor.execute('SELECT * FROM TODO_TABLE')
    records = cursor.fetchall()
    return records

def retrieve_task(task_):
    cursor.execute('SELECT * FROM TODO_TABLE WHERE task_ = "{}"'.format(task_))
    records = cursor.fetchall()
    return records

def delete_data(task_):
    cursor.execute('DELETE FROM TODO_TABLE WHERE task_ = "{}"'.format(task_))
    connection.commit()
    
def view_tasks():
    cursor.execute('SELECT DISTINCT task_ FROM TODO_TABLE')
    records = cursor.fetchall()
    return records

def update_task(new_task_, new_status_, new_date_, task_, status_, date_):
    cursor.execute('UPDATE TODO_TABLE SET task_ = ?, status_ = ?, date_ = ?  WHERE task_ = ? and status_ = ? and date_ = ?', (new_task_, new_status_, new_date_, task_, status_, date_))
    connection.commit()
    records = cursor.fetchall()
    return records