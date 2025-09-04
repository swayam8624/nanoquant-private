"""
Cloud integration for NanoQuant Enterprise
Handles user data storage, authentication, and cloud services
"""
import os
import json
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
import logging
import urllib.parse
import requests

logger = logging.getLogger(__name__)

class CloudStorage:
    def __init__(self):
        """Initialize cloud storage integration"""
        self.s3_client = None
        self.db_client = None
        self._initialize_aws()
    
    def _initialize_aws(self):
        """Initialize AWS services"""
        try:
            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # Initialize DynamoDB client
            self.db_client = boto3.resource(
                'dynamodb',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            logger.info("AWS services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS services: {e}")
    
    def upload_user_model(self, user_id: str, model_path: str, model_name: str) -> bool:
        """Upload compressed model to cloud storage"""
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            bucket_name = os.getenv('S3_BUCKET_NAME', 'nanoquant-models')
            key = f"{user_id}/{model_name}"
            
            self.s3_client.upload_file(model_path, bucket_name, key)
            logger.info(f"Model uploaded successfully: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload model: {e}")
            return False
    
    def download_user_model(self, user_id: str, model_name: str, local_path: str) -> bool:
        """Download compressed model from cloud storage"""
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            bucket_name = os.getenv('S3_BUCKET_NAME', 'nanoquant-models')
            key = f"{user_id}/{model_name}"
            
            self.s3_client.download_file(bucket_name, key, local_path)
            logger.info(f"Model downloaded successfully: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to download model: {e}")
            return False
    
    def save_user_data(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Save user data to database"""
        if not self.db_client:
            logger.error("DynamoDB client not initialized")
            return False
        
        try:
            table = self.db_client.Table(os.getenv('DYNAMODB_TABLE', 'nanoquant-users'))
            user_data['user_id'] = user_id
            
            table.put_item(Item=user_data)
            logger.info(f"User data saved successfully: {user_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to save user data: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user data from database"""
        if not self.db_client:
            logger.error("DynamoDB client not initialized")
            return None
        
        try:
            table = self.db_client.Table(os.getenv('DYNAMODB_TABLE', 'nanoquant-users'))
            
            response = table.get_item(Key={'user_id': user_id})
            user_data = response.get('Item')
            
            if user_data:
                logger.info(f"User data retrieved successfully: {user_id}")
                return user_data
            else:
                logger.info(f"No user data found: {user_id}")
                return None
        except ClientError as e:
            logger.error(f"Failed to retrieve user data: {e}")
            return None

class SocialAuth:
    def __init__(self):
        """Initialize social authentication"""
        self.google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.github_client_id = os.getenv('GITHUB_CLIENT_ID')
        self.github_client_secret = os.getenv('GITHUB_CLIENT_SECRET')
    
    def google_auth_url(self, redirect_uri: str) -> str:
        """Generate Google authentication URL"""
        import urllib.parse
        
        params = {
            'client_id': self.google_client_id,
            'redirect_uri': redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'offline'
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"https://accounts.google.com/o/oauth2/auth?{query_string}"
    
    def github_auth_url(self, redirect_uri: str) -> str:
        """Generate GitHub authentication URL"""
        import urllib.parse
        
        params = {
            'client_id': self.github_client_id,
            'redirect_uri': redirect_uri,
            'scope': 'user:email'
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"https://github.com/login/oauth/authorize?{query_string}"
    
    def verify_google_token(self, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange Google authorization code for access token and user info"""
        try:
            # Exchange code for access token
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    'client_id': self.google_client_id,
                    'client_secret': self.google_client_secret,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri
                },
                headers={'Accept': 'application/json'}
            )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                access_token = token_data.get('access_token')
                
                if access_token:
                    # Get user info
                    user_response = requests.get(
                        "https://www.googleapis.com/oauth2/v2/userinfo",
                        headers={'Authorization': f'Bearer {access_token}'}
                    )
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        return {
                            'id': user_data.get('id'),
                            'email': user_data.get('email'),
                            'name': user_data.get('name'),
                            'picture': user_data.get('picture')
                        }
            
            return None
        except Exception as e:
            logger.error(f"Failed to verify Google token: {e}")
            return None
    
    def verify_github_token(self, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange GitHub code for access token and user info"""
        try:
            # Exchange code for access token
            token_response = requests.post(
                "https://github.com/login/oauth/access_token",
                data={
                    'client_id': self.github_client_id,
                    'client_secret': self.github_client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri
                },
                headers={'Accept': 'application/json'}
            )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                access_token = token_data.get('access_token')
                
                if access_token:
                    # Get user info
                    user_response = requests.get(
                        "https://api.github.com/user",
                        headers={'Authorization': f'token {access_token}'}
                    )
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        return {
                            'id': user_data.get('id'),
                            'email': user_data.get('email'),
                            'name': user_data.get('name', user_data.get('login')),
                            'avatar_url': user_data.get('avatar_url')
                        }
            
            return None
        except Exception as e:
            logger.error(f"Failed to verify GitHub token: {e}")
            return None

# Global cloud storage instance
cloud_storage = CloudStorage()