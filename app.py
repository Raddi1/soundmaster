from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


# Function to initialize the database and create the 'favorites' table if it doesn't exist
def init_db():
    conn = sqlite3.connect("database.db")  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to interact with the database
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL
        )
        """
    )  # SQL command to create the 'favorites' table
    conn.commit()  # Commit the changes
    conn.close()  # Close the connection


# Route for the main page
@app.route("/")
def index():
    # Render the main page template
    return render_template("index.html")


# Route to add a track to the favorites
@app.route("/add_to_favorites", methods=["POST"])
def add_to_favorites():
    title = request.form.get("track_title")  # Get the track title from the form
    artist = request.form.get("artist_name")  # Get the artist name from the form

    # Check if title and artist are provided
    if not title or not artist:
        return "Both track title and artist name are required!", 400

    conn = sqlite3.connect("database.db")  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to interact with the database
    cursor.execute(
        "INSERT INTO favorites (title, artist) VALUES (?, ?)", (title, artist)
    )  # SQL command to insert the new track into the 'favorites' table
    conn.commit()  # Commit the changes
    conn.close()  # Close the connection
    return redirect(url_for("index"))  # Redirect to the main page


# Route to display the favorites page
@app.route("/favorites")
def favorites():
    conn = sqlite3.connect("database.db")  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to interact with the database
    cursor.execute(
        "SELECT title, artist, id FROM favorites"
    )  # SQL command to get all tracks from the 'favorites' table
    tracks = cursor.fetchall()  # Fetch all results from the executed query
    conn.close()  # Close the connection
    return render_template(
        "favorites.html", tracks=tracks
    )  # Render the favorites page template with the tracks


@app.route("/remove_from_favorites", methods=["POST"])
def remove_from_favorites():
    track_id = request.form.get("track_id")  # Get the track ID from the form
    if not track_id:
        return "Track ID is required!", 400
    conn = sqlite3.connect("database.db")  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to interact with the database
    cursor.execute(
        "DELETE FROM favorites WHERE id = ?", (track_id,)
    )  # SQL command to delete the track from the 'favorites' table
    conn.commit()  # Commit the changes
    conn.close()  # Close the connection
    return "", 204  # Return a No Content response


# Main entry point of the application
if __name__ == "__main__":
    init_db()  # Initialize the database
    app.run(debug=True)  # Run the Flask application in debug mode
