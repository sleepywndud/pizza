from imports import *


# route setting to index.html
@app.route("/", methods=["GET", "POST"])
def main():
    # global voucher_code
    data = menu_connect()
    orders = order_connect()

    # total cost by summing (price * quantity) using for loop
    total_cost = 0.0
    for order in orders:
        total_cost += float(order[2]) * int(order[3])
    # rounding to 2dp in case decimal place goes over 2
    total_cost = round(total_cost, 2)

    # voucher code section is not finished
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
        # redirect back if input is invalid (for valueerror)
        # NOTE: maybe alert user somehow if invalid input ???

        # right now it basically returns to the state before the invalid input
        return redirect(request.referrer or url_for("main"))

    conn = sqlite3.connect("order.db")
    cr = conn.cursor()

    if 0 < new_quantity <= 100:  # upper boundary is 100
        # update quantity in the database to the corresponding itemid
        cr.execute("UPDATE cart SET quantity = ? WHERE id = ?", (new_quantity, item_id))
    elif new_quantity == 0:
        # remove item if quantity is zero
        cr.execute("DELETE FROM cart WHERE id = ?", (item_id,))
    else:
        print(
            "AAAHHHHHHHHHHH"
        )  # i don't even know -- this shouldn't be triggered at all?
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
        #  [] = asdf.execure(asdfasdfasdf)
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


# route setting to customize.html
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

    draft = draft_connect()

    # draft total starts at $5 base, then adds each staged ingredient
    draft_total = 5.0
    for item in draft:
        draft_total += float(item[2])
    draft_total = round(draft_total, 2)

    return render_template(
        "customize.html",
        data=data,
        orders=orders,
        total_cost=total_cost,
        draft=draft,
        draft_total=draft_total,
    )


@app.route("/ingredient/<name>")
def ingredient(name):
    # below 5 lines could be refactored into a function..
    conn = sqlite3.connect("database.db")
    cr = conn.cursor()
    cr.execute("SELECT price FROM ingredient WHERE name = ?", (name,))
    item_data = cr.fetchone()
    conn.close()

    if item_data is not None:
        price = item_data[0]

        conn = sqlite3.connect("order.db")
        cr = conn.cursor()
        cr.execute(
            "INSERT INTO custom_pizza_draft (ingredient, price) VALUES (?, ?)",
            (name, price),
        )
        conn.commit()
        conn.close()

    return redirect(url_for("customize"))


@app.route("/remove_ingredient/<item_id>")
def remove_ingredient(item_id):
    conn = sqlite3.connect("order.db")
    cr = conn.cursor()
    cr.execute(
        "DELETE FROM custom_pizza_draft WHERE id = ?", (item_id,)
    )  # removes ingredient id from db
    conn.commit()
    conn.close()

    return redirect(url_for("customize"))


@app.route("/add_custom_to_cart")
def add_custom_to_cart():
    draft = draft_connect()

    if not draft:
        return redirect(url_for("customize"))

    # calculate total: $5 base + each ingredient
    total = 5.0
    for item in draft:
        total += float(item[2])
    total = round(total, 2)

    conn = sqlite3.connect("order.db")
    cr = conn.cursor()
    cr.execute(
        "INSERT INTO cart (name, price, quantity) VALUES ('Custom Pizza', ?, 1)",
        (str(total),),
    )  # add custom pizza to cart
    # 'total' is the total cost of the custom pizza (ingredient + the base price)
    cr.execute(
        "DELETE FROM custom_pizza_draft"
    )  # so that pizza preview is cleared after adding to cart
    conn.commit()
    conn.close()

    return redirect(url_for("customize"))
