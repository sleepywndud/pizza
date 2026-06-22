from imports import *


# route setting to index.html
@app.route("/", methods=["GET", "POST"])
def main():
    global voucher_code
    data = menu_connect()

    orders = order_connect()

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


@app.route("/update_quantity/<int:item_id>", methods=["POST"])
def update_quantity(item_id):
    # fetch quantity from the form in index.html
    try:
        new_quantity = int(request.form.get("quantity"))
    except ValueError:
        # redirect back if input is invalid (for valueerror and typeerror)
        # maybe alert user somehow if invalid input ???

        # right now it basically returns to the state before the invalid input
        return redirect(request.referrer or url_for("main"))

    conn = sqlite3.connect("order.db")
    cr = conn.cursor()

    if 0 < new_quantity <= 100:
        # update quantity in the database to the corresponding itemid
        cr.execute("UPDATE cart SET quantity = ? WHERE id = ?", (new_quantity, item_id))
    elif new_quantity == 0:
        # remove item if quantity is zero
        cr.execute("DELETE FROM cart WHERE id = ?", (item_id,))
    # if quantity is negative or too high, we just don't update anything

    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("main"))


@app.route("/add_to_order/<name>")
def add_to_order(name):
    conn = sqlite3.connect("database.db")
    cr = conn.cursor()

    # check pizza table
    cr.execute("SELECT price FROM pizza WHERE name = ?", (name,))
    item_data = cr.fetchone()

    # if not in pizza, check snack table
    if item_data is None:  # (if not in pizza table)
        cr.execute("SELECT price FROM snack WHERE name = ?", (name,))
        item_data = cr.fetchone()  # set item_data as the price of the item

    # if not in snack, check drinks table
    if item_data is None:
        cr.execute("SELECT price FROM drinks WHERE name = ?", (name,))
        item_data = cr.fetchone()

    conn.close()

    # updates quantity in cart table if item is in menu
    if item_data is not None:
        price = item_data[0]  # price

        conn = sqlite3.connect("order.db")
        cr = conn.cursor()
        # checks if item is already in order.db
        cr.execute("SELECT quantity FROM cart WHERE name = ?", (name,))
        item = cr.fetchone()

        if item is not None:
            # if item exists, increase the quantity by one
            new_quantity = item[0] + 1
            cr.execute(
                "UPDATE cart SET quantity = ? WHERE name = ?", (new_quantity, name)
            )
        else:
            # if item doesn't exist, then add the row to the db with quantity 1
            cr.execute(
                "INSERT INTO cart (name, price, quantity) VALUES (?, ?, 1)",
                (name, price),
            )

        conn.commit()
        conn.close()

    return redirect(request.referrer or url_for("main"))


# route setting to snacks.html
@app.route("/snacks")
def snacks():
    data = menu_connect("snack")

    orders = order_connect()

    # total cost by summing (price * quantity) using for loop
    total_cost = 0.0
    for order in orders:
        total_cost += float(order[2]) * int(order[3])
    # rounding to 2dp in case decimal place goes over 2
    total_cost = round(total_cost, 2)

    return render_template(
        "snacks.html", data=data, orders=orders, total_cost=total_cost
    )


# route setting to drinks.html
@app.route("/drinks")
def drinks():
    data = menu_connect("drinks")

    orders = order_connect()

    # total cost by summing (price * quantity) using for loop
    total_cost = 0.0
    for order in orders:
        total_cost += float(order[2]) * int(order[3])
    # rounding to 2dp in case decimal place goes over 2
    total_cost = round(total_cost, 2)

    return render_template(
        "drinks.html", data=data, orders=orders, total_cost=total_cost
    )


# route setting to custmoize.html
@app.route("/customize")
def customize():
    data = menu_connect("ingredient")

    orders = order_connect()

    # total cost by summing (price * quantity) using for loop
    total_cost = 0.0
    for order in orders:
        total_cost += float(order[2]) * int(order[3])
    # rounding to 2dp in case decimal place goes over 2
    total_cost = round(total_cost, 2)

    return render_template(
        "customize.html", data=data, orders=orders, total_cost=total_cost
    )
