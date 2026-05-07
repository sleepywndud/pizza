from imports import *


# route setting to index.html
@app.route("/", methods=["GET", "POST"])
def main():
    global voucher_code
    conn = sqlite3.connect("database.db")
    cr = conn.cursor()

    cr.execute("SELECT * FROM pizza")
    data = cr.fetchall()
    conn.close()

    conn = sqlite3.connect("order.db")
    cr = conn.cursor()
    cr.execute("SELECT * FROM orders")
    orders = cr.fetchall()
    conn.close()

    if request.method == "POST":
        voucher_code = request.form.get("voucher_code")
        print(f"\n\nVoucher Code Received: {voucher_code}\n\n")

    return render_template("index.html", data=data, orders=orders)


@app.route("/add_to_order/<name>/<price>")
def add_to_order(name, price):
    conn = sqlite3.connect("order.db")
    cr = conn.cursor()
    cr.execute("INSERT INTO orders (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()
    # redirects to main function
    return redirect(url_for("main"))


# route setting to snacks.html
@app.route("/snacks")
def snacks():
    return render_template("snacks.html")


# route setting to drinks.html
@app.route("/drinks")
def drinks():
    return render_template("drinks.html")


# route setting to custmoize.html
@app.route("/customize")
def customize():
    return render_template("customize.html")
