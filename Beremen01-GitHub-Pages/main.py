from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__, static_folder="static")

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/choose")
def choose():
    return render_template("choose.html")

@app.route("/main")
def main():
    return render_template("index.html")

@app.route("/weight")
def weight():
    return render_template("weight.html")

@app.route("/register_user", methods=["POST"])
def register_user():
    data = request.json
    user_id = data.get("user_id")
    username = data.get("username", "")

    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            username TEXT
        )
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username)
        VALUES (?, ?)
    """, (user_id, username))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# After: main.py (load_user_data computing weeks from start_date)
@app.route("/load_user_data", methods=["GET"])
def load_user_data():
    user_id = request.args.get("user_id")
    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    # (Ensure weight_summary table exists, etc., omitted for brevity)
    # Fetch all weight entries for the user
    cursor.execute("SELECT weight, date FROM weights WHERE user_id = ? ORDER BY date ASC", (user_id,))
    weight_rows = cursor.fetchall()
    start_weight = weight_rows[0][0] if weight_rows else None

    # NEW: Get stored pregnancy start date
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pregnancy_start (
            user_id TEXT UNIQUE,
            start_date TEXT
        )
    """)
    cursor.execute("SELECT start_date FROM pregnancy_start WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    start_date = row[0] if row else None

    # Compute current weeks based on start_date
    weeks = None
    if start_date:
        try:
            from datetime import date
            start_date_obj = date.fromisoformat(start_date)  # parse YYYY-MM-DD
        except Exception as e:
            start_date_obj = None
        if start_date_obj:
            diff_days = (date.today() - start_date_obj).days
            weeks = diff_days // 7

    # Get user height if exists
    cursor.execute("SELECT height FROM user_height WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    height = row[0] if row else None

    # Calculate recommended weight gain range if possible
    norm_info = None
    if start_weight and height and weeks is not None:
        norm_info = calculate_weight_norm(weeks, height, start_weight)
        cursor.execute("""
            INSERT OR REPLACE INTO weight_summary (user_id, bmi, bmi_category, min_kg, max_kg)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            norm_info["bmi"],
            norm_info["category"],
            norm_info["min_kg"],
            norm_info["max_kg"]
        ))
    conn.commit()
    conn.close()
    return jsonify({
        "start_weight": start_weight,
        "weights": weight_rows,
        "weeks": weeks,
        "start_date": start_date,
        "height": height,
        "norm_info": norm_info
    })


# 🔽 ДОБАВЛЕНО: получение всех записей веса
@app.route("/get_weights", methods=["GET"])
def get_weights():
    user_id = request.args.get("user_id", "default")
    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, weight FROM weights
        WHERE user_id = ?
        ORDER BY date ASC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return jsonify(rows)

@app.route("/debug_all")
def debug_all():
    import datetime
    import traceback

    def convert(row):
        return [str(cell) if isinstance(cell, (datetime.date, datetime.datetime, bytes)) else cell for cell in row]

    result = {}

    try:
        conn = sqlite3.connect("pregnancy.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print("Найдены таблицы:", tables)

        if "users" in tables:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            print("Пользователи:", rows)
            result["users"] = [convert(row) for row in rows]
        else:
            result["users"] = "Таблица users не найдена"

        if "weights" in tables:
            cursor.execute("SELECT * FROM weights")
            rows = cursor.fetchall()
            print("Вес:", rows)
            result["weights"] = [convert(row) for row in rows]
        else:
            result["weights"] = "Таблица weights не найдена"

        if "pregnancy_weeks" in tables:
            cursor.execute("SELECT * FROM pregnancy_weeks")
            rows = cursor.fetchall()
            print("Сроки:", rows)
            result["pregnancy_weeks"] = [convert(row) for row in rows]
        else:
            result["pregnancy_weeks"] = "Таблица pregnancy_weeks не найдена"

        if "weight_summary" in tables:
            cursor.execute("SELECT * FROM weight_summary")
            rows = cursor.fetchall()
            print("Индекс и норма:", rows)
            result["weight_summary"] = [convert(row) for row in rows]
        else:
            result["weight_summary"] = "Таблица weight_summary не найдена"

        if "normal_pressure" in tables:
            cursor.execute("SELECT * FROM normal_pressure")
            rows = cursor.fetchall()
            print("Нормальное давление:", rows)
            result["normal_pressure"] = [convert(row) for row in rows]
        else:
            result["normal_pressure"] = "Таблица normal_pressure не найдена"

        if "pressure_entries" in tables:
            cursor.execute("SELECT * FROM pressure_entries")
            rows = cursor.fetchall()
            print("Записи давления:", rows)
            result["pressure_entries"] = [convert(row) for row in rows]
        else:
            result["pressure_entries"] = "Таблица pressure_entries не найдена"

        conn.close()
        return jsonify(result)

    except Exception as e:
        print("ОШИБКА В /debug_all:")
        traceback.print_exc()
        return f"<pre>Ошибка: {str(e)}</pre>", 500

# After: main.py (save_weeks storing start_date and weeks)
@app.route("/save_weeks", methods=["POST"])
def save_weeks():
        data = request.json
        user_id = data.get("user_id")
        weeks = data.get("weeks")
        start_date = data.get("start_date")  # New field for pregnancy start date
        if not user_id or start_date is None or weeks is None:
            return jsonify({"error": "Недостаточно данных"}), 400
        conn = sqlite3.connect("pregnancy.db")
        cursor = conn.cursor()
        # Ensure tables exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pregnancy_start (
                user_id TEXT PRIMARY KEY,
                start_date TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pregnancy_weeks (
                user_id TEXT PRIMARY KEY,
                weeks INTEGER
            )
        """)
        # Save/Update pregnancy start date and weeks in the database
        cursor.execute("""
            INSERT OR REPLACE INTO pregnancy_start (user_id, start_date)
            VALUES (?, ?)
        """, (user_id, start_date))
        cursor.execute("""
            INSERT OR REPLACE INTO pregnancy_weeks (user_id, weeks)
            VALUES (?, ?)
        """, (user_id, weeks))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})

@app.route("/save_normal_pressure", methods=["POST"])
def save_normal_pressure():
    data = request.json
    user_id = data.get("user_id")
    systolic = data.get("systolic")
    diastolic = data.get("diastolic")

    if not user_id or not systolic or not diastolic:
        return jsonify({"error": "Недостаточно данных"}), 400

    conn = sqlite3.connect("pregnancy.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS normal_pressure (
            user_id TEXT PRIMARY KEY,
            systolic INTEGER,
            diastolic INTEGER
        )
    """)
    cur.execute("""
        INSERT OR REPLACE INTO normal_pressure (user_id, systolic, diastolic)
        VALUES (?, ?, ?)
    """, (user_id, systolic, diastolic))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/tests")
def tests():
    return render_template("tests.html")

@app.route("/save_pressure", methods=["POST"])
def save_pressure():
    data = request.json
    user_id = data.get("user_id")
    systolic = data.get("systolic")
    diastolic = data.get("diastolic")
    date = data.get("date")  # в формате YYYY-MM-DD

    if not user_id or not systolic or not diastolic or not date:
        return jsonify({"error": "Недостаточно данных"}), 400

    conn = sqlite3.connect("pregnancy.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pressure_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            date TEXT,
            systolic INTEGER,
            diastolic INTEGER,
            UNIQUE(user_id, date)
        )
    """)
    cur.execute("""
        INSERT OR REPLACE INTO pressure_entries (user_id, date, systolic, diastolic)
        VALUES (?, ?, ?, ?)
    """, (user_id, date, systolic, diastolic))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/load_pressure_data", methods=["GET"])
def load_pressure_data():
    user_id = request.args.get("user_id")

    conn = sqlite3.connect("pregnancy.db")
    cur = conn.cursor()

    cur.execute("SELECT systolic, diastolic FROM normal_pressure WHERE user_id = ?", (user_id,))
    norm_row = cur.fetchone()
    norm_pressure = {"systolic": norm_row[0], "diastolic": norm_row[1]} if norm_row else None

    cur.execute("""
        SELECT date, systolic, diastolic
        FROM pressure_entries
        WHERE user_id = ?
        ORDER BY date ASC
    """, (user_id,))
    entries = cur.fetchall()

    conn.close()

    return jsonify({
        "normal_pressure": norm_pressure,
        "entries": entries
    })

@app.route("/pressure")
def pressure():
    return render_template("pressure.html")

@app.route("/mood")
def mood():
    return render_template("mood.html")

@app.route("/save_mood", methods=["POST"])
def save_mood():
    data = request.get_json()
    user_id = data["user_id"]
    date = data["date"]
    mood = data.get("mood")
    wellbeing = data.get("wellbeing")

    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO mood_entries (user_id, date, mood, wellbeing)
        VALUES (?, ?, ?, ?)
    """, (user_id, date, mood, wellbeing))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/load_mood_data")
def load_mood_data():
    user_id = request.args.get("user_id")
    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, mood, wellbeing
        FROM mood_entries
        WHERE user_id = ?
        ORDER BY date
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify({"entries": rows})

@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")

@app.route("/sugar")
def sugar_page():
    return render_template("sugar.html")

@app.route("/save_sugar", methods=["POST"])
def save_sugar():
    data = request.get_json()
    user_id = data.get("user_id")
    date = data.get("date")
    sugar = data.get("sugar")

    if not user_id or not date or sugar is None:
        return jsonify({"error": "Missing data"}), 400

    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sugar_entries (
            user_id TEXT,
            date TEXT,
            sugar REAL,
            PRIMARY KEY (user_id, date)
        )
    """)
    cursor.execute("""
        INSERT OR REPLACE INTO sugar_entries (user_id, date, sugar)
        VALUES (?, ?, ?)
    """, (user_id, date, sugar))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/load_sugar_data", methods=["GET"])
def load_sugar_data():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sugar_entries (
            user_id TEXT,
            date TEXT,
            sugar REAL,
            PRIMARY KEY (user_id, date)
        )
    """)
    cursor.execute("""
        SELECT date, sugar FROM sugar_entries
        WHERE user_id = ?
        ORDER BY date
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return jsonify({"entries": rows})

@app.route("/save_weight", methods=["POST"])
def save_weight():
    data = request.json
    weight = data.get("weight")
    date_str = data.get("date")
    user_id = data.get("user_id", "default")  # можно позже заменить на Telegram ID

    if not weight or not date_str:
        return jsonify({"error": "Недостаточно данных"}), 400

    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()

    # Создание таблицы с ограничением уникальности по user_id и date
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            date TEXT,
            weight REAL,
            UNIQUE(user_id, date)
        )
    """)

    # Вставка или обновление записи
    cursor.execute("""
        INSERT INTO weights (user_id, date, weight)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, date) DO UPDATE SET weight = excluded.weight
    """, (user_id, date_str, weight))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

def calculate_weight_norm(week, height_cm, start_weight):
    if not week or not height_cm or not start_weight:
        return None

    height_m = height_cm / 100
    bmi = start_weight / (height_m ** 2)

    if bmi < 18.5:
        category = "underweight"
        base_gain = 1.2
    elif 18.5 <= bmi < 25:
        category = "normal"
        base_gain = 1.0
    elif 25 <= bmi < 30:
        category = "overweight"
        base_gain = 0.7
    else:
        category = "obese"
        base_gain = 0.5

    # Первая прибавка появляется после 8-й недели
    if week < 9:
        return {
            "bmi": round(bmi, 1),
            "category": category,
            "min_kg": 0,
            "max_kg": 0
        }

    # Мосгорздрав: прирост массы тела после 8-й недели
    weeks_with_gain = week - 8
    min_kg = weeks_with_gain * (base_gain - 0.2)
    max_kg = weeks_with_gain * (base_gain + 0.2)

    return {
        "bmi": round(bmi, 1),
        "category": category,
        "min_kg": round(min_kg, 1),
        "max_kg": round(max_kg, 1)
    }

# ▶️ Создание таблиц давления при старте, если не существуют
def init_tables():
        conn = sqlite3.connect("pregnancy.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pregnancy_weeks (
                user_id TEXT PRIMARY KEY,
                weeks   INTEGER
            )
        """)

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS normal_pressure (
            user_id TEXT PRIMARY KEY,
            systolic INTEGER,
            diastolic INTEGER
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pressure_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            date TEXT,
            systolic INTEGER,
            diastolic INTEGER,
            UNIQUE(user_id, date)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_entries (
            user_id TEXT,
            date TEXT,
            mood INTEGER,
            wellbeing INTEGER,
            UNIQUE(user_id, date)
        )
        ''')

        conn.commit()
        conn.close()
        print("✅ Все таблицы инициализированы.")

# Вызов при запуске
init_tables()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)