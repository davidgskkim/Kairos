📅 Employee Shift Scheduler

This is a Flask web app that automatically generates optimized employee shift schedules based on uploaded Excel files containing weekly availability and preferences.

<!-- optional if you have one -->
🚀 Features

    📤 Upload .xlsx Excel files with weekly availability

    🤖 Automatically assigns shifts based on:

        Availability

        Ideal shift count

        Overlap constraints

        Preference rankings

    📊 Outputs schedule in a clean HTML table

    📥 Download final schedule as Excel

    🌐 Deployed and styled with Bootstrap 5

📁 Project Structure

shift_scheduler/
├── app.py                  # Flask app
├── templates/index.html    # HTML frontend
├── static/                 # CSS/JS/assets + Excel downloads
├── uploads/                # Uploaded Excel files
├── parse_employees.py      # Parses availability Excel input
├── generate_schedule.py    # Core scheduling logic
├── requirements.txt
├── render.yaml             # Render deploy config

📦 Requirements

    Python 3.8+

    pip

Install dependencies:

pip install -r requirements.txt

🧪 Running Locally

python app.py

Then go to http://localhost:5000

🔧 Excel Format Example

The uploaded file must include:
(no header)	MON	TUE	...	SUN	Ideal	Preference
Alice	ON	OFF	...	ON	4	3

Values:

    ON = Available for open & close

    OPEN = Only morning

    CLOSE = Only evening

    OFF or blank = Unavailable

☁️ Deployment

The app is deployed via Render.com using render.yaml.

To redeploy:

    Push to GitHub

    Render rebuilds automatically

📄 License

MIT License.
Feel free to fork and adapt to your own scheduling needs.
