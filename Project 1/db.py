import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="chatUsers"
)

mycursor = mydb.cursor()


def create_db():
  mycursor.execute("CREATE DATABASE chatUsers")


def create_table():
  mycursor.execute("CREATE TABLE users (name VARCHAR(255) PRIMARY KEY UNIQUE, ip VARCHAR(255), port INT(255))")


def insert_user(name, ip, port):
  if not check_exists(name):
    sql = "INSERT INTO users (name, ip, port) VALUES (%s, %s, %s)"
    val = (name.strip('\n'), ip, port)
    mycursor.execute(sql, val)
    mydb.commit()


def select():
  mycursor.execute("SELECT * FROM users")
  myresult = mycursor.fetchall()
  for x in myresult:
    print(x)


def check_exists(name):
  sql = "SELECT * FROM users WHERE name = %s"
  adr = (name,)
  mycursor.execute(sql, adr)
  myresult = mycursor.fetchall()
  if myresult:
    return True
  else:
    return False


def delete_user(name):
  if check_exists(name):
    sql = "DELETE FROM users WHERE name = %s"
    adr = (name, )
    mycursor.execute(sql, adr)
    mydb.commit()


def get_online_users():
  mycursor.execute("SELECT name FROM users")
  myresult = mycursor.fetchall()
  row = [item[0] for item in myresult]
  l = []
  for i in range(len(row)):
    print(row[i])
    row[i] = row[i].strip('\n')
    row[i] = row[i].strip('')
    l.append(row[i])
  return l


def change_name(oldName, newName):
  sql = "UPDATE users SET name = %s WHERE name = %s"
  val = (newName, oldName)
  mycursor.execute(sql, val)
  print(mycursor.rowcount)
  mydb.commit()


# create_db()
# create_table()
# insert_user("tara", "127.0.0.1", "5000")
# delete_user("mohammad")
# select()
# get_online_users()
# print(check_exists("moein"))
# change_name("ziba", "zahra")