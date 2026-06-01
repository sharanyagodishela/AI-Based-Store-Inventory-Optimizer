from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, inspect, text
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle

app = Flask(__name__)
app.secret_key = "secret123"

# -----------------------
# DATABASE CONFIG
# -----------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------
# LOAD TRAINED MODEL
# -----------------------
model = None
features = None

if os.path.exists("model.pkl"):
    with open("model.pkl", "rb") as f:
        model_data = pickle.load(f)
        model = model_data["model"]
        features = model_data["features"]
    print("✅ ML Model Loaded Successfully")
else:
    print("⚠️ model.pkl not found. Run train_model.py first!")

# -----------------------
# USER TABLE
# -----------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200), nullable=False)

# -----------------------
# PRODUCT TABLE
# -----------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    stock = db.Column(db.Integer)
    price = db.Column(db.Float)
    sales = db.Column(db.Integer)

# -----------------------
# FIX DATABASE
# -----------------------
def fix_database():
    inspector = inspect(db.engine)

    if 'user' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('user')]

        if 'email' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE user ADD COLUMN email VARCHAR(120)"))
                print("✅ Email column added")

# -----------------------
# LOGIN PAGE
# -----------------------
@app.route("/")
@app.route("/login")
def login_page():
    return render_template("login.html")

# -----------------------
# REGISTER
# -----------------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password")

        existing_user = User.query.filter(
            or_(User.username == username, User.email == email)
        ).first()

        if existing_user:
            flash("Username or Email already exists")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful! Please Login")
        return redirect(url_for("login_page"))

    return render_template("register.html")

# -----------------------
# LOGIN PROCESS
# -----------------------
@app.route("/login", methods=["POST"])
def login():
    user_input = request.form.get("username").strip()
    password = request.form.get("password")

    user = User.query.filter(
        or_(User.username == user_input, User.email == user_input)
    ).first()

    if user and check_password_hash(user.password, password):
        session['username'] = user.username
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid Username or Password")
        return redirect(url_for("login_page"))

# -----------------------
# LOGOUT
# -----------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect(url_for("login_page"))

# -----------------------
# DASHBOARD
# -----------------------
@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        flash("Please login first")
        return redirect(url_for("login_page"))

    products = Product.query.all()

    low_stock = []
    restock = []

    for p in products:
        if p.stock < 10:
            low_stock.append(p)
        if p.sales > 50 and p.stock < 20:
            restock.append(p)

    top_products = Product.query.order_by(Product.sales.desc()).limit(3).all()

    total_products = len(products)
    total_stock = sum(p.stock for p in products)
    total_sales = sum(p.sales for p in products)

    # -----------------------
    # ML PREDICTION
    # -----------------------
    predicted_sales = {}

    if model:
        for p in products:
            try:
                # Mapping to match training features
                input_data = np.array([[p.stock, p.sales, p.price]])
                prediction = model.predict(input_data)
                predicted_sales[p.id] = int(prediction[0])
            except:
                predicted_sales[p.id] = p.sales
    else:
        for p in products:
            predicted_sales[p.id] = p.sales

    return render_template(
        "dashboard.html",
        products=products,
        low_stock=low_stock,
        restock=restock,
        top_products=top_products,
        predicted_sales=predicted_sales,
        total_products=total_products,
        total_stock=total_stock,
        total_sales=total_sales
    )

# -----------------------
# ADD PRODUCT
# -----------------------
@app.route("/add", methods=["GET","POST"])
def add_product():
    if 'username' not in session:
        return redirect(url_for("login_page"))

    if request.method == "POST":
        name = request.form["name"]
        stock = int(request.form["stock"])
        price = float(request.form["price"])
        sales = int(request.form["sales"])

        product = Product.query.filter_by(name=name).first()

        if product:
            product.stock += stock
            product.sales += sales
            product.price = price
        else:
            new_product = Product(name=name, stock=stock, price=price, sales=sales)
            db.session.add(new_product)

        db.session.commit()
        flash("Product Added / Updated")
        return redirect(url_for("dashboard"))

    return render_template("add_product.html")

# -----------------------
# EDIT PRODUCT
# -----------------------
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit_product(id):
    if 'username' not in session:
        return redirect(url_for("login_page"))

    product = Product.query.get_or_404(id)

    if request.method == "POST":
        product.name = request.form["name"]
        product.stock = int(request.form["stock"])
        product.price = float(request.form["price"])
        product.sales = int(request.form["sales"])  # ✅ FIXED

        db.session.commit()
        flash("Product Updated Successfully")
        return redirect(url_for("dashboard"))

    return render_template("edit_product.html", product=product)

# -----------------------
# SEARCH PRODUCT
# -----------------------
@app.route("/search", methods=["GET","POST"])
def search():
    products = []

    if request.method == "POST":
        keyword = request.form["keyword"]
        products = Product.query.filter(Product.name.like(f"%{keyword}%")).all()

    return render_template("search.html", products=products)

# -----------------------
# DELETE PRODUCT
# -----------------------
@app.route("/delete/<int:id>", methods=["POST"])
def delete_product(id):
    if 'username' not in session:
        return redirect(url_for("login_page"))

    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()

    flash("Product Deleted")
    return redirect(url_for("dashboard"))

# -----------------------
# GRAPH
# -----------------------
@app.route("/graph")
def graph():
    products = Product.query.all()

    names = [p.name for p in products]
    sales = [p.sales for p in products]
    stock = [p.stock for p in products]

    predicted_sales = []
    predicted = 0

    if model and len(products) > 0:
        for p in products:
            try:
                input_data = np.array([[p.stock, p.sales, p.price]])
                pred = model.predict(input_data)
                predicted_sales.append(pred[0])
            except:
                predicted_sales.append(p.sales)

        predicted = int(predicted_sales[-1])

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.figure()
    plt.bar(names, sales)
    plt.title("Product Sales")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("static/graph1.png")
    plt.close()

    plt.figure()
    plt.bar(names, stock)
    plt.title("Product Stock")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("static/graph2.png")
    plt.close()

    if len(predicted_sales) > 0:
        plt.figure()
        plt.plot(sales, label="Actual Sales")
        plt.plot(predicted_sales, label="Predicted Sales")
        plt.legend()
        plt.title("Actual vs Predicted Sales")
        plt.tight_layout()
        plt.savefig("static/graph3.png")
        plt.close()

    return render_template("graph.html", predicted=predicted)

# ----------------------
# RUN APP
# ----------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        fix_database()

    app.run(debug=True)