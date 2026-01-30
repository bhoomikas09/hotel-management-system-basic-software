from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
                    room_no INTEGER PRIMARY KEY,
                    room_type TEXT,
                    price REAL,
                    status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    room_no INTEGER,
                    check_in TEXT,
                    check_out TEXT,
                    total_cost REAL)''')
    conn.commit()
    conn.close()

init_db()


# ---------- ROUTES ----------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_no = request.form['room_no']
        room_type = request.form['room_type']
        price = request.form['price']
        status = 'Available'
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO rooms VALUES (?, ?, ?, ?)", (room_no, room_type, price, status))
        conn.commit()
        conn.close()
        return redirect('/view_rooms')
    return render_template('add_room.html')


@app.route('/view_rooms')
def view_rooms():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rooms")
    data = c.fetchall()
    conn.close()
    return render_template('view_rooms.html', rooms=data)


@app.route('/check_in', methods=['GET', 'POST'])
def check_in():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT room_no FROM rooms WHERE status='Available'")
    available_rooms = c.fetchall()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        room_no = request.form['room_no']
        check_in_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO customers (name, phone, room_no, check_in) VALUES (?, ?, ?, ?)",
                  (name, phone, room_no, check_in_date))
        c.execute("UPDATE rooms SET status='Occupied' WHERE room_no=?", (room_no,))
        conn.commit()
        conn.close()
        return redirect('/view_customers')
    return render_template('check_in.html', rooms=available_rooms)


@app.route('/check_out', methods=['GET', 'POST'])
def check_out():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT room_no, check_in FROM customers WHERE id=?", (customer_id,))
        customer = c.fetchone()

        if customer:
            room_no, check_in_time = customer
            check_in_dt = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
            check_out_dt = datetime.now()
            days = max(1, (check_out_dt - check_in_dt).days + 1)

            c.execute("SELECT price FROM rooms WHERE room_no=?", (room_no,))
            price = c.fetchone()[0]
            total_cost = price * days

            c.execute("UPDATE customers SET check_out=?, total_cost=? WHERE id=?",
                      (check_out_dt.strftime("%Y-%m-%d %H:%M:%S"), total_cost, customer_id))
            c.execute("UPDATE rooms SET status='Available' WHERE room_no=?", (room_no,))
            conn.commit()
        conn.close()
        return redirect('/view_customers')
    return render_template('check_out.html')


@app.route('/view_customers')
def view_customers():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    customers = c.fetchall()
    conn.close()
    return render_template('view_customers.html', customers=customers)


if __name__ == '__main__':
    app.run(debug=True)
