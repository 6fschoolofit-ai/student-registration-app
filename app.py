import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, render_template, request
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Available courses
COURSES = [
    "Python Programming",
    "AWS Cloud",
    "DevOps",
    "Full Stack Development",
    "Data Science",
    "Generative AI",
]

# Google Sheets configuration
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

CREDENTIALS_FILE = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/run/secrets/google-credentials.json"
)

SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_ID")


def get_worksheet():
    """Connect to Google Sheets and return the first worksheet."""
    if not SPREADSHEET_ID:
        raise ValueError("GOOGLE_SHEETS_ID environment variable is missing.")

    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    return spreadsheet.sheet1


def save_to_google_sheets(name, email, phone, course):
    """Save student registration details with an IST timestamp."""
    worksheet = get_worksheet()

    # Generate the current date and time in Indian Standard Time
    registered_at = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%Y-%m-%d %H:%M:%S IST")

    worksheet.append_row(
        [
            name,
            email,
            phone,
            course,
            registered_at,
        ],
        value_input_option="RAW",
    )

    logger.info("Student registration saved successfully.")


@app.route("/", methods=["GET", "POST"])
def index():
    """Display the registration form and process submissions."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        course = request.form.get("course", "").strip()

        # Validate required fields
        if not all([name, email, phone, course]):
            return render_template(
                "index.html",
                courses=COURSES,
                error="All fields are required.",
            ), 400

        # Validate email format
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            return render_template(
                "index.html",
                courses=COURSES,
                error="Please enter a valid email address.",
            ), 400

        # Validate phone number
        if not phone.isdigit() or not 10 <= len(phone) <= 15:
            return render_template(
                "index.html",
                courses=COURSES,
                error="Please enter a valid phone number (10–15 digits).",
            ), 400

        # Validate selected course
        if course not in COURSES:
            return render_template(
                "index.html",
                courses=COURSES,
                error="Please select a valid course.",
            ), 400

        try:
            save_to_google_sheets(name, email, phone, course)

            return render_template(
                "index.html",
                courses=COURSES,
                success="Student registered successfully!",
            )

        except Exception:
            logger.exception("Failed to save registration to Google Sheets")

            return render_template(
                "index.html",
                courses=COURSES,
                error=(
                    "Registration could not be saved. "
                    "Please try again later."
                ),
            ), 500

    return render_template("index.html", courses=COURSES)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

