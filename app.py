from flask import Flask, render_template, request
import os
from parse_employees import parse_schedule
from generate_schedule import generate_schedule
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = "your-secret-key"  # replace with env var in production
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    schedule = None
    excel_filename = None

    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("❌ No file selected.", "danger")
            return redirect(url_for("index"))

        if not file.filename.endswith(".xlsx"):
            flash("❌ Only .xlsx files are supported.", "danger")
            return redirect(url_for("index"))

        try:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            employees = parse_schedule(filepath)
            schedule = generate_schedule(employees, filepath)
            excel_filename = "latest_schedule.xlsx"
            flash("✅ Schedule generated successfully!", "success")
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "danger")
            return redirect(url_for("index"))

    return render_template(
        "index.html", schedule=schedule, excel_filename=excel_filename
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
