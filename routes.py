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

    # total cost by summing (price * quantity) using for loop
    total_cost = 0.0
    for order in orders:
        total_cost += float(order[2]) * int(order[3])
    # rounding to 2dp in case decimal place goes over 2
    total_cost = round(total_cost, 2)

    if request.method == "POST":
        voucher_code = request.form.get("voucher_code")
        print(f"\n\nVoucher Code Received: {voucher_code}\n\n")

    return render_template(
        "index.html", data=data, orders=orders, total_cost=total_cost
    )


@app.route("/update_quantity/<item_id>", methods=["POST"])
def update_quantity(item_id):
    # fetch quantity from the form in index.html
    # NOTE: ADD VALUE-TYPE CHECKING
    new_quantity = int(request.form.get("quantity"))

    conn = sqlite3.connect("order.db")
    cr = conn.cursor()

    if new_quantity > 0:
        # update quantity in the database to the corresponding itemid
        cr.execute(
            "UPDATE orders SET quantity = ? WHERE id = ?", (new_quantity, item_id)
        )
    else:
        # remove item if quantity is zero
        cr.execute("DELETE FROM orders WHERE id = ?", (item_id,))

    conn.commit()
    conn.close()
    return redirect(url_for("main"))


@app.route("/add_to_order/<name>/<price>")
def add_to_order(name, price):
    conn = sqlite3.connect("order.db")
    cr = conn.cursor()
    # checks if item is in order.db
    cr.execute(
        "SELECT quantity FROM orders WHERE name = ?", (name,)
    )  # need to pass a tuple so that it works
    item = cr.fetchone()

    if item:
        # if item exists, increase the quantity by one
        new_quantity = item[0] + 1
        cr.execute(
            "UPDATE orders SET quantity = ? WHERE name = ?", (new_quantity, name)
        )
    else:
        # if item doesn't exist, then add the row to the db, with quantity 1
        cr.execute(
            "INSERT INTO orders (name, price, quantity) VALUES (?, ?, 1)", (name, price)
        )

    conn.commit()
    conn.close()
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
