import os
import json
import base64
import logging
from django.conf import settings
from django.utils import timezone
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from cryptography.fernet import Fernet
from accounting.models import UserGmailToken, EmailCommunicationLog

logger = logging.getLogger(__name__)

# Scopes required for the application
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email'
]

class EncryptionService:
    @staticmethod
    def get_cipher_suite():
        key = os.getenv('FERNET_KEY')
        if not key:
            # Fallback for development (NOT SECURE FOR PROD without env var)
            # Ensure key is 32 url-safe base64-encoded bytes
            logger.warning("FERNET_KEY not found in env, using fallback based on SECRET_KEY")
            key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].zfill(32).encode())
        return Fernet(key)

    @staticmethod
    def encrypt(data):
        if not data: return None
        return EncryptionService.get_cipher_suite().encrypt(data.encode())

    @staticmethod
    def decrypt(data):
        if not data: return None
        return EncryptionService.get_cipher_suite().decrypt(data).decode()


class GmailAuthService:
    """
    Handles OAuth2 flow for Gmail.
    """
    EMAIL_SCOPE = ['https://www.googleapis.com/auth/userinfo.email']
    
    # Path relative to backend root: accounting/services/gmail_service.py -> .../backend/client_secret.json
    CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'client_secret.json')

    @staticmethod
    def get_flow(redirect_uri):
        if not os.path.exists(GmailAuthService.CLIENT_SECRETS_FILE):
             raise FileNotFoundError(f"Client secrets file not found at {GmailAuthService.CLIENT_SECRETS_FILE}")
             
        return Flow.from_client_secrets_file(
            GmailAuthService.CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

    @staticmethod
    def get_authorization_url(redirect_uri):
        flow = GmailAuthService.get_flow(redirect_uri)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url, state

    @staticmethod
    def exchange_code(code, redirect_uri, user):
        flow = GmailAuthService.get_flow(redirect_uri)
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Determine email address
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        email = user_info.get('email')

        # Encrypt and Store
        refresh_token_enc = EncryptionService.encrypt(credentials.refresh_token)
        
        token, created = UserGmailToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token': credentials.token,
                'refresh_token_encrypted': refresh_token_enc,
                'token_expiry': specs_to_expiry(credentials),
                'email': email
            }
        )
        return token

    @staticmethod
    def get_credentials(user):
        try:
            token = UserGmailToken.objects.get(user=user)
        except UserGmailToken.DoesNotExist:
            return None
            
        refresh_token = EncryptionService.decrypt(token.refresh_token_encrypted)
        
        credentials = Credentials(
            token=token.access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=get_client_id(), # Helper needed
            client_secret=get_client_secret(), # Helper needed
            scopes=SCOPES
        )
        
        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # Update DB with new access token
            token.access_token = credentials.token
            token.token_expiry = specs_to_expiry(credentials)
            token.save()
            
        return credentials

def specs_to_expiry(credentials):
    # expiry is usually a datetime object in credentials
    return credentials.expiry if hasattr(credentials, 'expiry') else timezone.now()

def get_client_id():
    with open(GmailAuthService.CLIENT_SECRETS_FILE) as f:
        data = json.load(f)
        return data['web']['client_id']

def get_client_secret():
    with open(GmailAuthService.CLIENT_SECRETS_FILE) as f:
        data = json.load(f)
        return data['web']['client_secret']


class GmailSenderService:
    """
    Sends emails and logs to PostgreSQL.
    """
    @staticmethod
    def send_email(user, subject, recipients, body, voucher=None, approval_action=None):
        credentials = GmailAuthService.get_credentials(user)
        if not credentials:
            raise ValueError("User has not linked Gmail account")

        service = build('gmail', 'v1', credentials=credentials)
        
        message = MIMEText(body)
        message['to'] = ", ".join(recipients) if isinstance(recipients, list) else recipients
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        try:
            sent_message = service.users().messages().send(userId="me", body={'raw': raw}).execute()
            
            # Log to DB
            EmailCommunicationLog.objects.create(
                message_id=sent_message['id'],
                subject=subject,
                sender=user.gmail_token.email,
                recipient=message['to'],
                voucher=voucher,
                approval_action=approval_action,
                status='sent',
                metadata_json=convert_metadata(sent_message)
            )
            return sent_message
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            # Log failure
            EmailCommunicationLog.objects.create(
                message_id=f"FAILED-{timezone.now().timestamp()}",
                subject=subject,
                sender=user.gmail_token.email if hasattr(user, 'gmail_token') else 'unknown',
                recipient=message['to'],
                voucher=voucher,
                approval_action=approval_action,
                status=f"failed: {str(e)}",
            )
            raise e

def convert_metadata(msg):
    return {
        'threadId': msg.get('threadId'),
        'labelIds': msg.get('labelIds')
    }
