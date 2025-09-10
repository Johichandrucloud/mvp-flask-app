from flask import Flask
import pymysql
import boto3
import json

app = Flask(__name__)

def get_db_secret():
    try:
        client = boto3.client("secretsmanager", region_name="ap-south-1")
        secret = client.get_secret_value(SecretId="mvp-app/db-credentials")
        return json.loads(secret["SecretString"])
    except Exception as e:
        print(f"Error loading secret: {e}")
        return None

secret = get_db_secret()

if secret:
    DB_HOST = secret.get("host")
    DB_USER = secret.get("username")
    DB_PASS = secret.get("password")
    DB_NAME = secret.get("database")
else:
    DB_HOST = DB_USER = DB_PASS = DB_NAME = None

@app.get("/healthz")
def health():
    return ("ok", 200)

@app.get("/")
def home():
    return "Hello from EC2 + RDS + Secrets Manager!"

@app.get("/dbtest")
def dbtest():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return {"db_time": str(result[0])}
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/users")
def get_users():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, created_at FROM users")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {"users": rows}
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/secrettest")
def secrettest():
    return {
        "db_host": DB_HOST,
        "db_user": DB_USER,
        "db_name": DB_NAME
    }
