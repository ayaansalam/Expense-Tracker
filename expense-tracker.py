from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    amount INTEGER,
                    priority TEXT
            )
''')
conn.commit()
conn.close()

@app.route("/")
def home():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchall()[0][0] or 0

    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    categories = cursor.fetchall()

    max_total = max([c[1] for c in categories]) if categories else 1

    sort = request.args.get("sort")

    if sort == "asc":
        order = "ORDER BY amount ASC"
    elif sort == "desc":
        order = "ORDER BY amount DESC"
    else:
        order = ""

    search = request.args.get("search")
    if search:
        cursor.execute("SELECT * FROM expenses WHERE category LIKE ? " + order, ("%" + search + "%",))
    else:
        cursor.execute("SELECT * FROM expenses " + order)
    expenses = cursor.fetchall()

    conn.close()
    return render_template("index.html", expenses = expenses, total = total, categories = categories, max_total = max_total, search = search)
 
@app.route("/add", methods = ["POST"])
def add():
    category = request.form["category"]
    amount = request.form["amount"]
    priority = request.form["priority"]
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (category, amount, priority) VALUES (?,?,?)", (category, amount, priority))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:id>", methods = ["POST"])
def delete(id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)