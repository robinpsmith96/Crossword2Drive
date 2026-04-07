import os
import datetime
import requests
import pickle

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

months = {
    "1":"Jan",
    "2":"Feb",
    "3":"Mar",
    "4":"Apr",
    "5":"May",
    "6":"Jun",
    "7":"Jul",
    "8":"Aug",
    "9":"Sep",
    "10":"Oct",
    "11":"Nov",
    "12":"Dec"
}

# ---------------------------
# Download NYT print PDF
# ---------------------------

import http.cookiejar
import re
from datetime import timedelta

PDF_RE = re.compile(r'https://[^"]+\.pdf')

def get_puzzle_id_from_page(session):
    url = "https://www.nytimes.com/crosswords/game/daily"
    r = session.get(url)
    if r.status_code != 200:
        return None

    # Look for embedded JSON with puzzle_id
    match = re.search(r'"puzzle_id":\s*(\d+)', r.text)
    if match:
        return match.group(1)

    return None

def fetch_latest_pdf(session):
    url = "https://www.nytimes.com/crosswords/game/daily"
    r = session.get(url)
    print("Page length:", len(r.text))

    if r.status_code != 200:
        print("Failed to load crossword page:", r.status_code)
        return None

    # Extract puzzle_id from embedded page data
    match = re.search(r'"puzzle_id":\s*(\d+)', r.text)
    if not match:
        print("Could not find puzzle_id in page")
        return None

    puzzle_id = match.group(1)
    print("Found puzzle_id:", puzzle_id)

    pdf_url = f"https://www.nytimes.com/svc/crosswords/v2/puzzle/{puzzle_id}.pdf"
    r2 = session.get(pdf_url)

    if r2.status_code == 200 and r2.content.startswith(b"%PDF"):
        filename = f"NYT Crossword {datetime.date.today().isoformat()}.pdf"
        with open(filename, "wb") as f:
            f.write(r2.content)
        return filename

    print("Failed to download PDF:", r2.status_code)
    return None

def download_crossword_pdf():
    session = requests.Session()

    cj = http.cookiejar.MozillaCookieJar()
    cj.load("nyt_cookies.txt", ignore_discard=True, ignore_expires=True)
    session.cookies = cj
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    today = datetime.date.today()

    pdf = fetch_latest_pdf(session)

    if not pdf:
        raise RuntimeError("Printable NYT crossword PDF not found.")
    if pdf:
        return pdf

    raise RuntimeError("Printable NYT crossword PDF not found (today or yesterday).")

# ---------------------------
# Google Drive
# ---------------------------

def drive_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("drive", "v3", credentials=creds)


def upload_pdf(service, path):
    service.files().create(
        body={
            "name": os.path.basename(path),
            "parents": [DRIVE_FOLDER_ID],
        },
        media_body=MediaFileUpload(path, mimetype="application/pdf"),
    ).execute()

# ---------------------------
# Main
# ---------------------------

def main():
    pdf = download_crossword_pdf()
    upload_pdf(drive_service(), pdf)

if __name__ == "__main__":
    main()
