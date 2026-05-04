from imports import *


# route setting to index.html
@app.route("/", methods=["POST"])
def main():
    global voucher_code
    conn = sqlite3.connect("database.db")
    cr = conn.cursor()

    cr.execute("SELECT * FROM pizza")
    data = cr.fetchall()

    if request.method == "POST":
        voucher_code = request.form.get("voucher_code")
        print(f"Voucher Code Received: {voucher_code}")

    return render_template("index.html", data=data)


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
