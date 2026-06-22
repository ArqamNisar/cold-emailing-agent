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

def check_thread_replies(thread_id: str, lead_email: str) -> int:
    """
    Check the Gmail thread for replies from the lead.
    Returns the number of reply messages from the lead.
    """
    if not is_authenticated():
        log.warning("check_thread_replies called but not authenticated")
        return 0
    try:
        creds = get_credentials()
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/threads/{thread_id}"
        headers = {
            "Authorization": f"Bearer {creds.token}"
        }
        log.info("Fetching thread %s details from Gmail API via requests", thread_id)
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            log.error("Failed to fetch thread %s. Code: %d, Response: %s", thread_id, response.status_code, response.text)
            return 0
            
        thread_data = response.json()
        messages = thread_data.get('messages', [])
        
        reply_count = 0
        my_email = get_profile_email().lower()
        lead_email_clean = lead_email.strip().lower()
        
        for msg in messages:
            headers_list = msg.get('payload', {}).get('headers', [])
            from_header = ""
            for h in headers_list:
                if h.get('name', '').lower() == 'from':
                    from_header = h.get('value', '').lower()
                    break
            
            # If the email is from the lead, and NOT from me
            if lead_email_clean in from_header and my_email not in from_header:
                reply_count += 1
                
        log.info("Counted %d replies from lead %s in thread %s", reply_count, lead_email, thread_id)
        return reply_count
    except Exception as e:
        log.error("Error checking replies in thread %s: %s", thread_id, e)
        return 0

def extract_body(payload) -> str:
    """Recursively search and extract text/plain or text/html from message payload."""
    if 'parts' in payload:
        # 1. Search for text/plain
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    try:
                        return base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8', errors='replace')
                    except Exception as dec_err:
                        log.error("Failed to decode text/plain body: %s", dec_err)
        # 2. Search for text/html if text/plain not found
        for part in payload['parts']:
            if part.get('mimeType') == 'text/html':
                data = part.get('body', {}).get('data', '')
                if data:
                    try:
                        return base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8', errors='replace')
                    except Exception as dec_err:
                        log.error("Failed to decode text/html body: %s", dec_err)
        # 3. Recursively search nested parts
        for part in payload['parts']:
            if 'parts' in part:
                body = extract_body(part)
                if body:
                    return body
    else:
        # Simple body payload
        data = payload.get('body', {}).get('data', '')
        if data:
            try:
                return base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8', errors='replace')
            except Exception as dec_err:
                log.error("Failed to decode simple body: %s", dec_err)
    return ""

def get_thread_replies(thread_id: str, lead_email: str) -> list:
    """
    Check the Gmail thread for replies from the lead.
    Returns a list of reply message dicts, each with sender, date, snippet, and body.
    """
    if not is_authenticated():
        log.warning("get_thread_replies called but not authenticated")
        return []
    try:
        creds = get_credentials()
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/threads/{thread_id}"
        headers = {
            "Authorization": f"Bearer {creds.token}"
        }
        log.info("Fetching thread %s details from Gmail API for replies", thread_id)
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            log.error("Failed to fetch thread %s. Code: %d, Response: %s", thread_id, response.status_code, response.text)
            return []
            
        thread_data = response.json()
        messages = thread_data.get('messages', [])
        
        replies = []
        my_email = get_profile_email().lower()
        lead_email_clean = lead_email.strip().lower()
        
        for msg in messages:
            payload = msg.get('payload', {})
            headers_list = payload.get('headers', [])
            
            from_header = ""
            date_header = ""
            for h in headers_list:
                name_lower = h.get('name', '').lower()
                if name_lower == 'from':
                    from_header = h.get('value', '')
                elif name_lower == 'date':
                    date_header = h.get('value', '')
                    
            from_header_lower = from_header.lower()
            
            # If the email is from the lead, and NOT from me
            if lead_email_clean in from_header_lower and my_email not in from_header_lower:
                body = extract_body(payload)
                replies.append({
                    "from": from_header,
                    "date": date_header,
                    "snippet": msg.get('snippet', ''),
                    "body": body if body.strip() else msg.get('snippet', '')
                })
                
        log.info("Retrieved %d reply/replies content from lead %s in thread %s", len(replies), lead_email, thread_id)
        return replies
    except Exception as e:
        log.error("Error retrieving replies in thread %s: %s", thread_id, e)
        return []

