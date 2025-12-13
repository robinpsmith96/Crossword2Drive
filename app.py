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

def fetch_pdf_for_date(session, date):
    print_url = (
        "https://www.nytimes.com/svc/crosswords/v2/puzzle/print/"
        f"{months[str(date.month)]}{date.day:02d}{str(date.year)[2:]}.pdf"
    )
    # print(print_url)

    r = session.get(print_url)
    if r.status_code != 200:
        return None

    filename = f"NYT Crossword {date.isoformat()}.pdf"
    with open(filename, "wb") as f:
        f.write(r.content)
        return filename

    # Find embedded PDF URL
    #print(r.text)
    match = PDF_RE.search(r.text)
    if not match:
        return None

    print("UhOh!")
    pdf_url = match.group(0)
    r2 = session.get(pdf_url)

    if r2.status_code == 200 and r2.content.startswith(b"%PDF"):
        filename = f"NYT Crossword {date.isoformat()}.pdf"
        with open(filename, "wb") as f:
            f.write(r2.content)
        return filename

    return None

def download_crossword_pdf():
    session = requests.Session()

    cj = http.cookiejar.MozillaCookieJar()
    cj.load("nyt_cookies.txt", ignore_discard=True, ignore_expires=True)
    session.cookies = cj
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    today = datetime.date.today()

    pdf = fetch_pdf_for_date(session, today)
    if pdf:
        return pdf

    pdf = fetch_pdf_for_date(session, today - timedelta(days=1))
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
