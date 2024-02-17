import mysql.connector
from typing import Final
import os 
from dotenv import load_dotenv

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd = os.getenv('SQL_ROOT_PASSWORD'),
    database = "testdatabase"
)

mycursor = db.cursor()

mycursor.execute("CREATE DATABASE testdatabase")