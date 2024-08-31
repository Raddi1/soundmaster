from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/audio"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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


current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "tracks.json")


@app.route("/")
def index():
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tracks = json.load(f)
    except FileNotFoundError:
        tracks = []
        print("File not found")  # Debug message
    except json.JSONDecodeError:
        tracks = []
        print("JSON decode error")  # Debug message
    return render_template("music.html", tracks=tracks)


def count_files_in_directory(directory):
    # Get the list of all files and folders in the directory
    files_and_folders = os.listdir(directory)

    # Count the number of files
    file_count = sum(
        1 for item in files_and_folders if os.path.isfile(os.path.join(directory, item))
    )

    return file_count


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]

        if file.filename == "":
            return "No selected file"

        if file and (file.filename.endswith(".mp3") or file.filename.endswith(".wav")):
            count = count_files_in_directory(app.config["UPLOAD_FOLDER"])
            extension = ".mp3" if file.filename.endswith(".mp3") else ".wav"
            filename = f"track{count}{extension}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    tracks = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                tracks = []

            # Add new track info to the list
            track_info = {
                "title": request.form.get("title"),
                "artist": request.form.get("artist"),
                "path": f"audio/{filename}",  # relative path to the file in static
            }
            tracks.append(track_info)

            # Save updated tracks list back to the JSON file
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(tracks, f, ensure_ascii=False, indent=4)

            return redirect(url_for("index"))
        else:
            return "Invalid file type. Only MP3 and WAV files are allowed."

    return render_template("upload.html")


@app.route("/themes")
def change_theme():
    return render_template("themes.html")


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
