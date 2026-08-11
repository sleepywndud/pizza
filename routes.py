from imports import *

# remembers the last search so it survives the redirect after adding an item to order
last_query = None
last_sort_by = "price-ascending"


# route setting to pizzas.html
@app.route("/pizzas", methods=["GET", "POST"])
def main():
    global orders
    sort_by = request.form.get("sort", "price-ascending")
    data = menu_connect("pizza", sort_by)
    orders = order_connect()

    # use voucher code from the voucher_code form in HTML

    # triple condition for error message:
    # 1. must be a post request
    # 2. must be a voucher_code post request
    # 3. entered (by user) code must NOT be in the voucher db
    errormessage = None  # (init) no errors at initialization
    if (
        request.method == "POST"  # post req
        and "voucher_code" in request.form  # if request is voucher code
        and not apply_voucher(
            request.form.get("voucher_code")
        )  # if it ISN'T in the voucher table
    ):
        errormessage = "Invalid voucher code entered."

    # calculations involving total price and discounted price
    total_cost = totalcost_calc(orders)
    voucher = voucher_connect()
    discounted_total = apply_discount(total_cost, voucher)

    return render_template(
        "pizzas.html",
        data=data,
        orders=orders,
        total_cost=total_cost,
        voucher=voucher,
        discounted_total=discounted_total,
        sort_by=sort_by,
        errormessage=errormessage,
    )


# route to remove the applied voucher
@app.route("/remove_voucher")
def remove_voucher_route():
    remove_voucher()
    return redirect(request.referrer or url_for("main"))


# route to change the quantity of the item
@app.route("/update_quantity/<int:item_id>", methods=["POST"])
def update_quantity(item_id):
    # fetch quantity from the form in index.html
    try:
        new_quantity = int(request.form.get("quantity"))
    except ValueError:
        # redirect back if input is invalid (for valueerror)

        # right now it basically returns to the state before the invalid input
        return redirect(request.referrer or url_for("main"))

    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()

    if (
        0 < new_quantity <= 100
    ):  # quantity must be between 1 and 100 -- zero will delete the item
        # update quantity in the database to the corresponding itemid
        cr.execute("UPDATE cart SET quantity = ? WHERE id = ?", (new_quantity, item_id))
    elif new_quantity == 0:
        # remove item if quantity is zero
        # if this was a custom pizza, its ingredients in custom_pizza_draft
        # are linked via cart_id -- delete those first so none are left
        # pointing at a cart row that's about to be deleted
        cr.execute("DELETE FROM custom_pizza_draft WHERE cart_id = ?", (item_id,))
        cr.execute("DELETE FROM cart WHERE id = ?", (item_id,))
    else:
        print(
            "Invalid Quantity Entered."
        )  # triggered when integer quantity that doesn't fit inside 1~100 is entered
    # if quantity is negative or too high, we just don't update anything -- send straight back to request.referrer

    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("main"))


# route to remove an item from the cart
@app.route("/remove_from_cart/<int:item_id>")
def remove_from_cart(item_id):
    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()
    # if this was a custom pizza, its ingredients in custom_pizza_draft are
    # linked via cart_id -- delete those first so none are left pointing at
    # a cart row that's about to be deleted
    cr.execute("DELETE FROM custom_pizza_draft WHERE cart_id = ?", (item_id,))
    # deletes the item specified
    cr.execute("DELETE FROM cart WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    return redirect(request.referrer or url_for("main"))


# route to add an item to the cart
@app.route("/add_to_order/<name>")
def add_to_order(name):
    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()

    # pizza/snack/drinks are now one table (menu_item), so one lookup covers
    # all three instead of checking pizza, then snack, then drinks
    cr.execute("SELECT id, price FROM menu_item WHERE name = ?", (name,))
    item_data = cr.fetchone()

    # updates quantity in cart table if item is in menu
    if item_data is not None:
        item_id = item_data[0]  # id -- needed for the new cart.item_id foreign key
        price = item_data[1]  # price

        # checks if item is already in cart
        cr.execute("SELECT quantity FROM cart WHERE name = ?", (name,))
        item = cr.fetchone()

        if item is not None:
            # if item exists, increase the quantity by one
            new_quantity = item[0] + 1

            if (
                0 < new_quantity <= 100
            ):  # quantity must be between 1 and 100 -- zero will delete the item
                # update quantity in the database to the corresponding itemid
                cr.execute(
                    "UPDATE cart SET quantity = ? WHERE name = ?", (new_quantity, name)
                )
            else:
                print(
                    "Invalid Quantity Entered."
                )  # triggered when integer quantity that doesn't fit inside 1~100 is entered
            # if quantity is too high, we just don't update anything
        else:
            # if item doesn't exist, then add the row to the db with quantity 1
            # item_id links this row to its menu_item row (the new foreign key)
            cr.execute(
                "INSERT INTO cart (item_id, name, price, quantity) VALUES (?, ?, ?, 1)",
                (item_id, name, price),
            )
        #  [] =
        conn.commit()
        conn.close()

    return redirect(request.referrer or url_for("main"))


# route setting to snacks.html
@app.route("/snacks", methods=["GET", "POST"])
def snacks():
    global orders
    sort_by = request.form.get("sort", "price-ascending")
    data = menu_connect("snack", sort_by)

    orders = order_connect()

    # use voucher code from the voucher_code form in HTML
    errormessage = None
    if (
        request.method == "POST"
        and "voucher_code" in request.form
        and not apply_voucher(request.form.get("voucher_code"))
    ):
        errormessage = "Invalid voucher code entered."

    # cost calculation
    total_cost = totalcost_calc(orders)
    voucher = voucher_connect()
    discounted_total = apply_discount(total_cost, voucher)

    return render_template(
        "snacks.html",
        data=data,
        orders=orders,
        total_cost=total_cost,
        voucher=voucher,
        discounted_total=discounted_total,
        sort_by=sort_by,
        errormessage=errormessage,
    )


# route setting to drinks.html
@app.route("/drinks", methods=["GET", "POST"])
def drinks():
    global orders
    sort_by = request.form.get("sort", "price-ascending")
    data = menu_connect("drinks", sort_by)

    orders = order_connect()

    # use voucher code from the voucher_code form in HTML
    errormessage = None
    if (
        request.method == "POST"
        and "voucher_code" in request.form
        and not apply_voucher(request.form.get("voucher_code"))
    ):
        errormessage = "Invalid voucher code entered."

    # cost calculation
    total_cost = totalcost_calc(orders)
    voucher = voucher_connect()
    discounted_total = apply_discount(total_cost, voucher)

    return render_template(
        "drinks.html",
        data=data,
        orders=orders,
        total_cost=total_cost,
        voucher=voucher,
        discounted_total=discounted_total,
        sort_by=sort_by,
        errormessage=errormessage,
    )


# route setting to customize.html
@app.route("/customize", methods=["GET", "POST"])
def customize():
    global orders
    data = menu_connect("ingredient")
    orders = order_connect()

    # use voucher code from the voucher_code form in HTML
    errormessage = None
    if (
        request.method == "POST"
        and "voucher_code" in request.form
        and not apply_voucher(request.form.get("voucher_code"))
    ):
        errormessage = "Invalid voucher code entered."

    # total cost by summing (price * quantity) using for loop
    total_cost = 0.0
    for order in orders:
        total_cost += float(order[2]) * int(order[3])
    # rounding to 2dp in case decimal place goes over 2
    total_cost = round(total_cost, 2)

    # cost calculation
    voucher = voucher_connect()
    discounted_total = apply_discount(total_cost, voucher)

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
        voucher=voucher,
        discounted_total=discounted_total,
        draft=draft,
        draft_total=draft_total,
        errormessage=errormessage,
    )


# route that adds the ingredient to the custom_pizza_draft db
@app.route("/ingredient/<name>")
def ingredient(name):
    # below lines could be refactored into a function..
    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()
    cr.execute("SELECT id, price FROM ingredient WHERE name = ?", (name,))
    item_data = cr.fetchone()

    if item_data is not None:
        ingredient_id = item_data[
            0
        ]  # id -- needed for the new ingredient_id foreign key
        price = item_data[1]

        # ingredient_id links this row to its ingredient row (the new foreign key)
        cr.execute(
            "INSERT INTO custom_pizza_draft (ingredient_id, name, price) VALUES (?, ?, ?)",
            (ingredient_id, name, price),
        )
        conn.commit()

    conn.close()
    return redirect(url_for("customize"))


# route thta removes the ingredient from the custom_pizza_draft db
@app.route("/remove_ingredient/<item_id>")
def remove_ingredient(item_id):
    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()
    cr.execute(
        "DELETE FROM custom_pizza_draft WHERE id = ?", (item_id,)
    )  # removes ingredient id from db
    conn.commit()
    conn.close()

    return redirect(url_for("customize"))


# route to index html -- AKA the introduction (or help) page
@app.route("/")
def user_manual():
    return render_template("index.html")


# route to add a custom pizza (with ingredients) to the cart
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

    conn = sqlite3.connect("pizza.db")
    cr = conn.cursor()
    cr.execute(
        "INSERT INTO cart (name, price, quantity) VALUES ('Custom Pizza', ?, 1)",
        (str(total),),
    )  # add custom pizza to cart -- item_id stays NULL since it's not one single menu_item
    cart_id = cr.lastrowid  # id of the cart row we just inserted

    # link the staged ingredient rows to this cart row instead of deleting
    # them, so the FK from custom_pizza_draft.cart_id -> cart.id stays valid
    # and the preview clears (customize.html only shows rows where cart_id IS NULL)
    cr.execute(
        "UPDATE custom_pizza_draft SET cart_id = ? WHERE cart_id IS NULL", (cart_id,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("customize"))


# route setting to search.html
@app.route("/search", methods=["GET", "POST"])
def search():
    global orders, last_query, last_sort_by
    orders = order_connect()

    errormessage = None
    # triple condition for error message again..
    if (
        request.method == "POST"
        and "voucher_code" in request.form
        and not apply_voucher(request.form.get("voucher_code"))
    ):
        errormessage = "Invalid voucher code entered."

    # last search function
    if (
        request.method == "POST" and "search_bar" in request.form
    ):  # triggers if search bar post req
        last_query = (
            request.form.get("search_bar", "").strip().lower()
        )  # makes the user-input value the last_query so it is saved (no search history loss)
        last_sort_by = request.form.get(
            "sort", "price-ascending"
        )  # default sorting (price ASC)

    results = []
    # triggers every time user makes a request (except fetching the page the first time)
    if last_query is not None:
        results = search_menu(last_query, last_sort_by)

    total_cost = totalcost_calc(orders)
    voucher = voucher_connect()
    discounted_total = apply_discount(total_cost, voucher)

    return render_template(
        "search.html",
        results=results,
        query=last_query,
        sort_by=last_sort_by,
        orders=orders,
        total_cost=total_cost,
        voucher=voucher,
        discounted_total=discounted_total,
        errormessage=errormessage,
    )


# route to the checkout page
@app.route("/checkout")
def checkout():
    orders = order_connect()

    total_cost = totalcost_calc(orders)
    voucher = voucher_connect()
    discounted_total = apply_discount(total_cost, voucher)

    return render_template(
        "checkout.html",
        orders=orders,
        total_cost=total_cost,
        voucher=voucher,
        discounted_total=discounted_total,
    )
