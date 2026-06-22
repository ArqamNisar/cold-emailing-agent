import os
import json
import base64
import requests
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from logger import get_logger

log = get_logger(__name__)

# Scopes required to send emails and view metadata (like user email address)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

TOKEN_FILE = '.token.json'
CREDENTIALS_FILE = '.credentials.json'

def get_credentials():
    """Retrieve credentials from token.json or refresh them if expired."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            log.debug("Loaded existing credentials from %s", TOKEN_FILE)
        except Exception as e:
            log.error("Failed to load token file: %s", e)
    
    if creds and creds.expired and creds.refresh_token:
        try:
            log.info("Credentials expired. Attempting refresh.")
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            log.info("Credentials refreshed successfully.")
        except Exception as e:
            log.error("Failed to refresh token: %s", e)
            creds = None
            
    return creds

def is_authenticated() -> bool:
    """Return whether valid credentials are currently active."""
    creds = get_credentials()
    return creds is not None and creds.valid

def get_profile_email() -> str:
    """Retrieve the email address of the authenticated Gmail account via REST API."""
    if not is_authenticated():
        log.warning("get_profile_email called but not authenticated")
        return ""
    try:
        creds = get_credentials()
        url = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
        headers = {
            "Authorization": f"Bearer {creds.token}"
        }
        log.info("Fetching Gmail profile email via requests REST API")
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            profile = response.json()
            email = profile.get('emailAddress', '')
            log.info("Fetched Gmail profile email: %s", email)
            return email
        else:
            log.error("Failed to fetch Gmail profile. Code: %d, Response: %s", response.status_code, response.text)
            return ""
    except Exception as e:
        log.error("Failed to fetch Gmail profile: %s", e)
        return ""

def authenticate():
    """Run local OAuth desktop application flow and save token.json."""
    if not os.path.exists(CREDENTIALS_FILE):
        log.error("Authentication failed: %s does not exist", CREDENTIALS_FILE)
        raise FileNotFoundError(f"Google OAuth client secrets file '{CREDENTIALS_FILE}' is missing.")
        
    log.info("Starting Gmail API OAuth local flow")
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    # run_local_server will open the local web browser to authenticate
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    log.info("Gmail API OAuth successfully completed and token saved to %s", TOKEN_FILE)
    return creds

def disconnect():
    """Remove the authenticated token file."""
    if os.path.exists(TOKEN_FILE):
        try:
            os.remove(TOKEN_FILE)
            log.info("Disconnected Gmail account by removing %s", TOKEN_FILE)
        except Exception as e:
            log.error("Failed to remove token file: %s", e)
            raise e
    else:
        log.info("Disconnect called but token.json does not exist")

def send_email(to_email: str, subject: str, body_text: str):
    """Send an email using Gmail API's messages/send REST endpoint via requests."""
    if not is_authenticated():
        raise ValueError("Not authenticated with Gmail API. Please connect your account first.")
        
    creds = get_credentials()
    
    # Construct the MIME message
    message = MIMEText(body_text)
    message['to'] = to_email
    message['subject'] = subject
    
    # Gmail API expects a base64url encoded string
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    payload = {'raw': raw}
    
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json"
    }
    
    try:
        log.info("Sending email to %s via Gmail API REST endpoint (requests)", to_email)
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        
        if response.status_code == 200:
            sent_message = response.json()
            msg_id = sent_message.get('id', 'Unknown')
            log.info("Email sent successfully. Message ID: %s", msg_id)
            return sent_message
        else:
            log.error("Failed to send email via Gmail REST API. Code: %d, Response: %s", response.status_code, response.text)
            raise Exception(f"Gmail API REST error {response.status_code}: {response.text}")
    except Exception as e:
        log.error("Failed to send email to %s: %s", to_email, e)
        raise e
