# Student Registration Web Application

A student registration web app built with **Flask**, containerized with **Docker**, and integrated with the **Google Sheets API** for storing registration records. This project is designed as a hands-on AWS deployment project using an **Ubuntu EC2 instance**.

> **Runtime:** Python 3.12 · Flask · Gunicorn · Docker  
> **Storage:** Google Sheets API  
> **Timestamp timezone:** Indian Standard Time (IST, `Asia/Kolkata`)  
> **Status:** Learning/demo project

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Google Sheets Setup](#google-sheets-setup)
- [Run Locally](#run-locally)
- [Run with Docker](#run-with-docker)
- [Deploy to AWS EC2](#deploy-to-aws-ec2)
- [Configuration](#configuration)
- [Google Sheet Columns](#google-sheet-columns)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
- [Future Improvements](#future-improvements)
- [License](#license)

## Overview

The application provides a web form for collecting student details and saving them directly to a Google Sheet. Flask handles requests and server-side validation. Google service-account credentials authenticate the application to Google Sheets, while Docker provides a consistent runtime.

This project demonstrates Python web development, external API integration, Docker containerization, AWS EC2 deployment, and secure runtime configuration.

## Architecture

```text
Student Browser
      |
      | HTTP :5000 (demo setup)
      v
AWS EC2 - Ubuntu
      |
      v
Docker container: student-registration
      |
      +--> Gunicorn
      |      |
      |      v
      |    Flask application
      |      |
      |      +--> Form rendering and validation
      |      +--> Google Sheets API client
      |
      v
Google Sheets API
      |
      v
Google Spreadsheet
(Student registration records)
```

**Note:** This example uses HTTP on port `5000` for learning purposes. Use HTTPS and additional security controls before collecting real student data.

## Features

- Student registration form: name, email, phone number, and course
- Server-side validation of required fields and selected course
- Saves registrations to Google Sheets
- Stores new registration timestamps in IST
- Docker image based on Python 3.12
- Gunicorn WSGI server with two workers
- Runs as a non-root user inside the container
- Service-account JSON mounted read-only at runtime
- Configuration supplied through environment variables
- Container restart policy using `unless-stopped`
- Success and error messages displayed to the user

### Available courses

- Python Programming
- AWS Cloud
- DevOps
- Full Stack Development
- Data Science
- Generative AI

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| Web framework | Flask |
| WSGI server | Gunicorn |
| Registration storage | Google Sheets API |
| Authentication | Google service account / `google-auth` |
| Sheets client | `gspread` |
| Containerization | Docker |
| Cloud platform | AWS EC2 |
| Operating system | Ubuntu 24.04 LTS |
| Timezone | `Asia/Kolkata` (IST) |

## Project Structure

```text
student-registration-app/
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── templates/
    └── index.html
```

Runtime configuration and credentials should be stored outside the repository:

```text
/root/.config/student-registration/
└── app.env

/opt/student-registration/secrets/
└── credentials.json
```

**Never commit** `app.env`, the service-account JSON key, private keys, or other secrets to GitHub.

## How It Works

1. A student opens the registration page.
2. The student submits the form.
3. Flask validates the required fields, email format, phone number, and course selection.
4. The app authenticates to Google Sheets using a service-account JSON key.
5. A new row is appended to the first worksheet.
6. The registration time is formatted in IST, for example `2026-10-09 14:11:00 IST`.
7. The app displays a success or failure message.

The timestamp is generated with Python's `zoneinfo.ZoneInfo("Asia/Kolkata")`. Existing spreadsheet rows are not automatically modified when the application is updated.

## Prerequisites

- AWS account with permission to launch and access an EC2 instance
- Ubuntu 24.04 EC2 instance
- SSH key pair for the instance
- Docker Engine (for Docker deployment)
- Google account and Google Cloud project
- Google Sheets API enabled
- Spreadsheet shared with the service account as **Editor**
- Git installed on your computer or EC2 instance

## Google Sheets Setup

### 1. Create a spreadsheet

Create a Google spreadsheet, for example `Student Registration`. Set the first row to these headers:

```text
Student Name | Email ID | Phone Number | Course | Registered At
```

The app appends records to the first worksheet (`spreadsheet.sheet1`).

### 2. Enable the Google Sheets API

1. Open <https://console.cloud.google.com/>.
2. Create or select a Google Cloud project.
3. Go to **APIs & Services → Library**.
4. Find **Google Sheets API** and enable it.

### 3. Create a service account

1. Open **IAM & Admin → Service Accounts**.
2. Create a service account for this application.
3. Create and download a JSON key.
4. Keep the key private. Do not commit it to source control.

### 4. Share the spreadsheet

Copy the service-account email address and share the spreadsheet with that address, granting **Editor** access.

### 5. Find the spreadsheet ID

For a URL like:

```text
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
```

The spreadsheet ID is the value between `/d/` and `/edit`.

## Run Locally

### 1. Create and activate a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Set the following variables in your shell or a protected local environment file. Use an absolute path to the service-account JSON key.

```bash
export GOOGLE_SHEETS_ID="YOUR_SPREADSHEET_ID"
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/credentials.json"
```

Do not commit the actual values or credentials.

### 4. Run the application

```bash
python app.py
```

Open <http://127.0.0.1:5000> in your browser.

## Run with Docker

### 1. Build the image

Run this from the directory containing the `Dockerfile`:

```bash
docker build -t student-registration:1.0 .
```

### 2. Create runtime configuration

For the existing EC2 layout:

```bash
sudo mkdir -p /root/.config/student-registration
sudo chmod 700 /root/.config/student-registration
sudo nano /root/.config/student-registration/app.env
```

Add these lines, replacing the placeholder:

```dotenv
GOOGLE_SHEETS_ID=YOUR_SPREADSHEET_ID
GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/google-credentials.json
```

Save the file, then restrict access:

```bash
sudo chmod 600 /root/.config/student-registration/app.env
```

### 3. Place the service-account key on the host

For this deployment, the key is expected at:

```text
/opt/student-registration/secrets/credentials.json
```

The following commands assume the key already exists at that path and the container runs with UID/GID `1000`:

```bash
sudo mkdir -p /opt/student-registration/secrets
sudo chown root:1000 /opt/student-registration/secrets/credentials.json
sudo chmod 640 /opt/student-registration/secrets/credentials.json
sudo chmod 755 /opt
sudo chmod 755 /opt/student-registration
sudo chmod 750 /opt/student-registration/secrets
```

If the key has not yet been copied to that path, transfer it securely first. Adjust ownership if you changed the container user in your Dockerfile.

### 4. Start the container

```bash
docker run -d \
  --name student-registration \
  --restart unless-stopped \
  -p 5000:5000 \
  --env-file /root/.config/student-registration/app.env \
  --mount type=bind,src=/opt/student-registration/secrets/credentials.json,dst=/run/secrets/google-credentials.json,readonly \
  student-registration:1.0
```

### 5. Verify the container

```bash
docker ps
docker logs --tail 50 student-registration
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5000/
```

The GET request should return HTTP `200` if the app is responding. Submit a test registration to verify the Google Sheets integration end to end.

### 6. Update the application

After editing the source code, build a new image tag and recreate the container:

```bash
docker build -t student-registration:1.1 .

docker rm -f student-registration

docker run -d \
  --name student-registration \
  --restart unless-stopped \
  -p 5000:5000 \
  --env-file /root/.config/student-registration/app.env \
  --mount type=bind,src=/opt/student-registration/secrets/credentials.json,dst=/run/secrets/google-credentials.json,readonly \
  student-registration:1.1
```

Changing source files does not automatically update a running container. Rebuild the image and recreate the container after code changes.

## Deploy to AWS EC2

### 1. Configure the security group

For a temporary demo, use these inbound rules:

| Rule | Port | Recommended source |
|---|---:|---|
| SSH | 22 | Your public IP only |
| Custom TCP | 5000 | Your public IP only |

Do not expose SSH to everyone. Avoid collecting personal student data over public HTTP.

### 2. Connect to EC2

```bash
ssh -i /path/to/key.pem ubuntu@EC2_PUBLIC_IP
```

Use the correct SSH username for the AMI. The example Docker commands use the existing root-based directory paths; use consistent paths and privileges if your project lives under `/home/ubuntu`.

### 3. Install Docker

Follow the official instructions: <https://docs.docker.com/engine/install/ubuntu/>

Verify the installation:

```bash
docker --version
sudo docker run --rm hello-world
```

### 4. Clone the repository

After pushing this project to GitHub:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Replace the placeholders with your GitHub username and repository name. Ensure no secrets are present in the repository.

### 5. Build, configure, and run

Complete the Docker steps above: build the image, create `app.env`, securely place the service-account key, start the container, and verify it using logs and `curl`.

### 6. Open the application

Visit:

```text
http://EC2_PUBLIC_IP:5000
```

Replace `EC2_PUBLIC_IP` with your instance's public IPv4 address. The address can change after stopping and starting an instance unless you use an Elastic IP.

## Configuration

| Variable | Required | Purpose |
|---|---|---|
| `GOOGLE_SHEETS_ID` | Yes | ID of the target spreadsheet |
| `GOOGLE_APPLICATION_CREDENTIALS` | Yes | Path to the service-account JSON key inside the runtime environment |

Example runtime configuration:

```dotenv
GOOGLE_SHEETS_ID=YOUR_SPREADSHEET_ID
GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/google-credentials.json
```

Keep real values in a protected local file, not in this README or the Git repository.

## Google Sheet Columns

| Column | Description | Example |
|---|---|---|
| Student Name | Student's name | Alex Kumar |
| Email ID | Student's email | alex@example.com |
| Phone Number | 10–15 digits | 9876543210 |
| Course | Selected course | AWS Cloud |
| Registered At | Date and time in IST | `2026-10-09 14:11:00 IST` |

Examples are illustrative; use test data when validating the application.

## Troubleshooting

### Application does not load

```bash
docker ps -a
docker logs --tail 100 student-registration
curl -v http://localhost:5000/
```

Check container status, port mapping, EC2 public IP, and security-group rules.

### Google Sheets write fails

```bash
docker logs --tail 100 student-registration
```

Check that:
- Google Sheets API is enabled in the correct Cloud project.
- The spreadsheet ID is correct.
- The spreadsheet is shared with the service-account email as Editor.
- The JSON key exists on the host and is mounted at `/run/secrets/google-credentials.json`.
- The container user can read the mounted credential file.
- Both environment variables are configured correctly.

### Timestamp appears in UTC

The app should generate timestamps using:

```python
from datetime import datetime
from zoneinfo import ZoneInfo

registered_at = datetime.now(
    ZoneInfo("Asia/Kolkata")
).strftime("%Y-%m-%d %H:%M:%S IST")
```

Rebuild the image and recreate the container after changing source code. Existing rows are not automatically converted.

### Container name already exists

```bash
docker rm -f student-registration
```

Only remove the container if you intend to replace that deployment.

## Security Best Practices

- **Never commit secrets:** keep service-account JSON keys, `.env` files, private keys, and passwords out of Git.
- Use `.gitignore` as well as `.dockerignore`.
- Keep the service-account key outside the Docker image and mount it read-only.
- Restrict SSH and demo port access to trusted IP addresses.
- Use HTTPS for any deployment handling real personal information.
- Add CSRF protection, rate limiting, robust validation, monitoring, and privacy/retention policies before production use.
- Grant the service account only the access it needs.
- Rotate credentials immediately if a key is exposed.
- Never publish logs or screenshots containing secrets or real student data.

### Recommended `.gitignore`

```gitignore
.venv/
venv/
__pycache__/
*.py[cod]
.env
.env.*
!.env.example
credentials.json
*service-account*.json
*.pem
*.key
```

Review `git status` before pushing. If a secret was committed, deleting it in a later commit is not enough: revoke/rotate the exposed key and clean repository history where appropriate.

## Future Improvements

- HTTPS using a domain and TLS certificate
- Reverse proxy or load balancer
- PostgreSQL or Amazon RDS
- Automated tests and CI/CD using GitHub Actions
- Container image scanning and dependency updates
- Authentication and an admin dashboard
- Duplicate registration checks
- Structured logging, monitoring, and backups
- Infrastructure as Code using Terraform

## License

Choose a license before publishing this repository. If you want others to reuse the project, consider adding an appropriate open-source license such as MIT. Do not claim a license until a `LICENSE` file has been added.
