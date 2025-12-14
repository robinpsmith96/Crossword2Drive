# NYT Crossword → Google Drive (Automated PDF)

This project automatically downloads the **New York Times daily crossword printable PDF** and uploads it to a **Google Drive folder**.

It is designed to run **fully unattended** using **GitHub Actions**, so once set up it will run every day without any manual steps.

---

## ⚠️ Important Notes

* The New York Times **does not provide an official Crossword API**.
* This project relies on **your own NYT account cookies** to download the printable crossword PDF.
* You **must have an active NYT Crossword subscription**.
* Google Drive uploads use **OAuth (not a service account)** and run inside GitHub Actions.

---

## What This Repo Does

1. Downloads today’s NYT crossword **printable PDF**
2. Names it like:

   ```
   NYT-Crossword-YYYY-MM-DD.pdf
   ```
3. Uploads it to a Google Drive folder you choose
4. Runs automatically **every day** via GitHub Actions

---

## Requirements

You will need:

* A GitHub account
* A New York Times account with Crossword access
* A Google account with Google Drive

No local Python setup is required once GitHub Actions is configured.

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/nyt-crossword-pdf.git
cd nyt-crossword-pdf
```

---

## Step 2: Get Your NYT Cookies

The script authenticates to NYT using cookies exported from your browser.

### How to export cookies

1. Log in to [https://www.nytimes.com](https://www.nytimes.com)
2. Install a browser extension like:

   * **EditThisCookie** (Chrome)
   * **cookies.txt** (Firefox)
3. Export cookies **for `.nytimes.com`** in **Netscape cookies.txt format**
4. Save the file as:

   ```
   nyt_cookies.txt
   ```

⚠️ **Do not commit this file to a public repo** — it grants account access.

---

## Step 3: Create a Google OAuth App

### 1. Create a Google Cloud Project

* Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
* Create a new project

### 2. Enable Google Drive API

* APIs & Services → Library
* Enable **Google Drive API**

### 3. Create OAuth Credentials

* APIs & Services → Credentials
* Create credentials → **OAuth client ID**
* Application type: **Desktop app**

Download the credentials file and rename it:

```
credentials.json
```

---

## Step 4: Create a Google Drive Folder

1. Go to Google Drive
2. Create a folder where PDFs will be uploaded
3. Open the folder and copy the ID from the URL:

```
https://drive.google.com/drive/folders/FOLDER_ID_HERE
```

Save this value — you’ll need it shortly.

---

## Step 5: Set GitHub Secrets

In your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

Add the following secrets:

### `DRIVE_FOLDER_ID`

```
FOLDER_ID_HERE
```

### `NYT_COOKIES`

Paste the **entire contents** of `nyt_cookies.txt`

### `GOOGLE_CREDENTIALS_JSON`

Paste the **entire contents** of `credentials.json`

---

## Step 6: GitHub Actions Workflow

This repo includes a workflow at:

```
.github/workflows/nyt-crossword.yml
```

It:

* Runs once per day
* Sets up Python
* Injects secrets
* Downloads the crossword
* Uploads it to Drive

You do **not** need Docker or local cron jobs.

---

## Step 7: Run It Manually (First Time)

1. Go to the **Actions** tab in GitHub
2. Select **NYT Crossword PDF**
3. Click **Run workflow**

The first run will prompt Google OAuth authorization in the logs.
Once authorized, future runs are automatic.

---

## Schedule

The workflow is scheduled using cron:

```yaml
schedule:
  - cron: "0 11 * * *"
```

This runs at:

* **11:00 UTC**
* **7:00 AM US Eastern (during DST)**

You can change this in the workflow file.

---

## Troubleshooting

### 403 / NYT download errors

* Your NYT cookies may be expired
* Re-export cookies and update the secret

### Google OAuth errors

* Ensure the Drive API is enabled
* Ensure credentials.json is for a **Desktop app**

### No PDF found

* The NYT sometimes delays the printable PDF early in the morning
* The script retries today and yesterday automatically

---

## Security Notes

* Never commit cookies or credentials
* Rotate cookies periodically
* Keep this repo private if possible

---

## Disclaimer

This project is for **personal use only**.
You are responsible for complying with:

* New York Times Terms of Service
* Google API Terms of Service

---

## Enjoy 🧩

If you want enhancements (email notifications, Slack alerts, filename changes, archiving), feel free to fork and extend!
