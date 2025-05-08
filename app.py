from flask import Flask, render_template, request
import os
from parse_employees import parse_schedule
from generate_schedule import generate_schedule

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    schedule = None

    if request.method == "POST":
        file = request.files.get("file")
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            employees = parse_schedule(filepath)
            schedule = generate_schedule(employees)

    return render_template("index.html", schedule=schedule)


if __name__ == "__main__":
    app.run(debug=True)
