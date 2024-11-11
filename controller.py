import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from backend.validate_db import validate_database

# Initialize the Flask app
app = Flask(__name__, template_folder="frontend")

# Construct an absolute path to the database file
project_root = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(project_root, 'backend', 'Hotelek.db')

# Validate the database structure to ensure `Szalloda` table exists
validate_database(db_path)

# Configure the database URI for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}?timeout=30&check_same_thread=False"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with SQLAlchemy
db = SQLAlchemy(app)

# Query functions
def query_szalloda(search_query=None):
    """Query all hotels or filter by search term."""
    if search_query:
        query = text("SELECT * FROM Szalloda WHERE szalloda LIKE :search")
        results = db.session.execute(query, {"search": f"%{search_query}%"}).fetchall()
    else:
        query = text("SELECT * FROM Szalloda")
        results = db.session.execute(query).fetchall()
    
    headers = [column[1] for column in db.session.execute(text("PRAGMA table_info(Szalloda);")).fetchall()]
    return headers, results

def query_room_count_per_hotel():
    """Query the number of rooms per hotel."""
    query = text("SELECT Szalloda.szalloda AS Hotel, COUNT(Szoba.id) AS RoomCount FROM Szoba JOIN Szalloda ON Szoba.szallodaID = Szalloda.ID GROUP BY Szalloda.szalloda")
    headers = ["Hotel", "Room Count"]
    results = db.session.execute(query).fetchall()
    return headers, results

def query_average_beds_per_room():
    """Query the average number of beds per room for each hotel."""
    query = text("SELECT szalloda, avg(szoba.agy) as atlag FROM szalloda INNER JOIN szoba ON szalloda.ID = szoba.szallodaID GROUP BY szalloda.ID ORDER BY atlag")
    headers = ["Hotel", "Average Beds"]
    results = db.session.execute(query).fetchall()
    return headers, results

def query_reservations_per_hotel():
    """Query all reservations for each hotel."""
    query = text("SELECT Szalloda.szalloda AS SzallodaNev, Foglalas.ID AS FoglalasID, Foglalas.DatumKezd, Foglalas.DatumVeg FROM Szalloda INNER JOIN szoba ON Szalloda.ID = szoba.szallodaID INNER JOIN szoba_foglalas ON szoba.ID = szoba_foglalas.szobaID INNER JOIN Foglalas ON szoba_foglalas.foglalasID = Foglalas.ID ORDER BY Szalloda.szalloda, Foglalas.DatumKezd;")
    headers = ["Hotel Name", "Reservation ID", "Start Date", "End Date"]
    results = db.session.execute(query).fetchall()
    return headers, results

def query_restaurant_types_per_hotel():
    """Query the types of restaurants available in each hotel."""
    query = text("SELECT szalloda, etterem.tipus FROM Szalloda, etterem, szalloda_etterem WHERE szalloda.ID = szalloda_etterem.szallodaID AND etterem.id = szalloda_etterem.etteremID GROUP BY szalloda.ID")
    headers = ["Hotel", "Restaurant Type"]
    results = db.session.execute(query).fetchall()
    return headers, results

def query_reservation_counts_per_hotel():
    """Query the total number of reservations per hotel."""
    query = text("SELECT Szalloda.szalloda AS SzallodaNev, COUNT(Foglalas.ID) AS FoglalasokSzama FROM Foglalas JOIN szoba_foglalas ON Foglalas.ID = szoba_foglalas.foglalasID JOIN szoba ON szoba_foglalas.szobaID = szoba.ID JOIN Szalloda ON szoba.szallodaID = Szalloda.ID GROUP BY Szalloda.szalloda ORDER BY FoglalasokSzama DESC")
    headers = ["Hotel Name", "Reservation Count"]
    results = db.session.execute(query).fetchall()
    return headers, results

# Routes
@app.route("/", methods=["GET"])
def show_szalloda():
    """Show all hotels or search results in Szalloda table."""
    search_query = request.args.get('query')
    headers, results = query_szalloda(search_query)
    data = [dict(zip(headers, row)) for row in results]
    return render_template("index.html", headers=headers, data=data, title="Hotels")

@app.route("/room_count")
def room_count_per_hotel():
    """Show the number of rooms per hotel."""
    headers, results = query_room_count_per_hotel()
    data = [dict(zip(headers, row)) for row in results]
    return render_template("index.html", headers=headers, data=data, title="Room Count per Hotel")

@app.route("/average_beds")
def average_beds_per_room():
    """Show the average number of beds per room for each hotel."""
    headers, results = query_average_beds_per_room()
    data = [dict(zip(headers, row)) for row in results]
    return render_template("index.html", headers=headers, data=data, title="Average Beds per Room")

@app.route("/reservations")
def reservations_per_hotel():
    """Show all reservations for each hotel."""
    headers, results = query_reservations_per_hotel()
    data = [dict(zip(headers, row)) for row in results]
    return render_template("index.html", headers=headers, data=data, title="Reservations per Hotel")

@app.route("/restaurant_types")
def restaurant_types_per_hotel():
    """Show the types of restaurants available in each hotel."""
    headers, results = query_restaurant_types_per_hotel()
    data = [dict(zip(headers, row)) for row in results]
    return render_template("index.html", headers=headers, data=data, title="Restaurant Types per Hotel")

@app.route("/reservation_counts")
def reservation_counts_per_hotel():
    """Show the total number of reservations per hotel."""
    headers, results = query_reservation_counts_per_hotel()
    data = [dict(zip(headers, row)) for row in results]
    return render_template("index.html", headers=headers, data=data, title="Reservation Counts per Hotel")

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
