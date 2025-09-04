"""
User management system for NanoQuant
Handles user authentication, credit management, and subscription tiers
"""

import hashlib
import secrets
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os

# Try to import cloud integration (optional)
try:
    from nanoquant.core.cloud_integration import CloudStorage
    CLOUD_AVAILABLE = True
except ImportError:
    CLOUD_AVAILABLE = False
    CloudStorage = None

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, db_path: str = "./nanoquant_users.json"):
        self.db_path = db_path
        self.users = self._load_users()
        self.coupons = self._load_coupons()
        self.cloud_storage = CloudStorage() if CLOUD_AVAILABLE else None
        
    def _load_users(self) -> Dict[str, Any]:
        """Load users from file or create empty database"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading users: {e}")
                return {}
        return {
            "users": {},
            "coupons": {}
        }
    
    def _load_coupons(self) -> Dict[str, Any]:
        """Load coupons from the users database"""
        return self.users.get("coupons", {})
    
    def _save_users(self):
        """Save users to file"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def register_user(self, email: str, password: str, social_id: str = None) -> Optional[str]:
        """
        Register a new user
        Returns user ID if successful, None if email already exists
        """
        # Check if email already exists
        for user_id, user_data in self.users.get("users", {}).items():
            if user_data.get("email") == email:
                return None
        
        # Create new user
        user_id = secrets.token_hex(16)
        password_hash = self._hash_password(password) if password else None
        
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "social_id": social_id,
            "credits": 100,  # Free tier credits
            "tier": "free",
            "created_at": datetime.now().isoformat(),
            "compression_history": [],
            "last_login": datetime.now().isoformat()
        }
        
        if "users" not in self.users:
            self.users["users"] = {}
            
        self.users["users"][user_id] = user_data
        self._save_users()
        
        # Save to cloud if available
        if self.cloud_storage:
            self.cloud_storage.save_user_data(user_id, user_data)
        
        logger.info(f"New user registered: {email}")
        return user_id
    
    def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """
        Authenticate a user with email and password
        Returns user ID if successful, None if authentication fails
        """
        for user_id, user_data in self.users.get("users", {}).items():
            if user_data.get("email") == email:
                if user_data.get("password_hash") and self._verify_password(password, user_data.get("password_hash", "")):
                    # Update last login
                    self.users["users"][user_id]["last_login"] = datetime.now().isoformat()
                    self._save_users()
                    return user_id
        return None
    
    def authenticate_social_user(self, social_id: str, provider: str) -> Optional[str]:
        """
        Authenticate a user with social login
        Returns user ID if successful, None if authentication fails
        """
        for user_id, user_data in self.users.get("users", {}).items():
            if user_data.get("social_id") == social_id:
                # Update last login
                self.users["users"][user_id]["last_login"] = datetime.now().isoformat()
                self._save_users()
                return user_id
        
        # If user doesn't exist, create new user
        # In a real implementation, we would get user details from the social provider
        return None
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information
        """
        # Try to get from cloud first
        if self.cloud_storage:
            cloud_data = self.cloud_storage.get_user_data(user_id)
            if cloud_data:
                return cloud_data
        
        user_data = self.users.get("users", {}).get(user_id)
        if not user_data:
            return None
            
        # Return a copy without sensitive information
        profile = user_data.copy()
        profile.pop("password_hash", None)
        return profile
    
    def get_user_credits(self, user_id: str) -> Optional[int]:
        """
        Get user's current credit balance
        """
        user_data = self.users.get("users", {}).get(user_id)
        if not user_data:
            return None
        return user_data.get("credits", 0)
    
    def add_credits(self, user_id: str, credits: int, reason: str = "purchase") -> bool:
        """
        Add credits to user's account
        """
        if user_id not in self.users.get("users", {}):
            return False
            
        current_credits = self.users["users"][user_id].get("credits", 0)
        self.users["users"][user_id]["credits"] = current_credits + credits
        
        # Log the credit addition
        if "credit_log" not in self.users["users"][user_id]:
            self.users["users"][user_id]["credit_log"] = []
            
        self.users["users"][user_id]["credit_log"].append({
            "amount": credits,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_users()
        
        # Update cloud storage if available
        if self.cloud_storage:
            self.cloud_storage.save_user_data(user_id, self.users["users"][user_id])
        
        return True
    
    def deduct_credits(self, user_id: str, credits: int, reason: str = "compression") -> bool:
        """
        Deduct credits from user's account
        """
        if user_id not in self.users.get("users", {}):
            return False
            
        current_credits = self.users["users"][user_id].get("credits", 0)
        if current_credits < credits:
            return False
            
        self.users["users"][user_id]["credits"] = current_credits - credits
        
        # Log the credit deduction
        if "credit_log" not in self.users["users"][user_id]:
            self.users["users"][user_id]["credit_log"] = []
            
        self.users["users"][user_id]["credit_log"].append({
            "amount": -credits,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_users()
        
        # Update cloud storage if available
        if self.cloud_storage:
            self.cloud_storage.save_user_data(user_id, self.users["users"][user_id])
        
        return True
    
    def check_compression_access(self, user_id: str, compression_level: str) -> bool:
        """
        Check if user has access to a specific compression level
        """
        user_data = self.users.get("users", {}).get(user_id)
        if not user_data:
            return False
            
        tier = user_data.get("tier", "free")
        credits = user_data.get("credits", 0)
        
        # Define credit costs for different levels
        level_costs = {
            "light": 0,
            "medium": 0,
            "heavy": 10,
            "extreme": 25,
            "ultra": 50,
            "nano": 100,
            "atomic": 200,
            "custom": 75
        }
        
        cost = level_costs.get(compression_level, 0)
        
        # Free tier restrictions
        if tier == "free":
            free_levels = ["light", "medium"]
            if compression_level not in free_levels:
                # Check if user has any free trials left for paid levels
                trials_used = self._get_trials_count(user_id, compression_level)
                if trials_used >= 2:  # Limit to 2 trials
                    return credits >= cost
                # Allow trial usage
                return True
        
        # Premium tier - check credits
        return credits >= cost
    
    def _get_trials_count(self, user_id: str, compression_level: str) -> int:
        """
        Get the number of trials a free user has used for a compression level
        """
        user_data = self.users.get("users", {}).get(user_id)
        if not user_data:
            return 0
            
        trials = user_data.get("trial_usage", {})
        return trials.get(compression_level, 0)
    
    def increment_trial_usage(self, user_id: str, compression_level: str):
        """
        Increment trial usage counter for a free user
        """
        if user_id not in self.users.get("users", {}):
            return
            
        if "trial_usage" not in self.users["users"][user_id]:
            self.users["users"][user_id]["trial_usage"] = {}
            
        current = self.users["users"][user_id]["trial_usage"].get(compression_level, 0)
        self.users["users"][user_id]["trial_usage"][compression_level] = current + 1
        self._save_users()
    
    def create_coupon(self, credits: int, admin_key: str) -> Optional[str]:
        """
        Create a new coupon code (admin function)
        Returns coupon code if successful, None if unauthorized
        """
        # Simple admin check - in production, use proper authentication
        if admin_key != "nanoquant_admin_secret":
            return None
            
        coupon_code = secrets.token_urlsafe(16)
        expiration = datetime.now() + timedelta(days=30)
        
        coupon_data = {
            "credits": credits,
            "expires_at": expiration.isoformat(),
            "used_by": None,
            "used_at": None
        }
        
        if "coupons" not in self.users:
            self.users["coupons"] = {}
            
        self.users["coupons"][coupon_code] = coupon_data
        self._save_users()
        
        logger.info(f"New coupon created: {coupon_code} for {credits} credits")
        return coupon_code
    
    def redeem_coupon(self, user_id: str, coupon_code: str) -> bool:
        """
        Redeem a coupon code for credits
        """
        if user_id not in self.users.get("users", {}):
            return False
            
        if coupon_code not in self.users.get("coupons", {}):
            return False
            
        coupon = self.users["coupons"][coupon_code]
        
        # Check if coupon is expired
        expiration = datetime.fromisoformat(coupon.get("expires_at", ""))
        if datetime.now() > expiration:
            return False
            
        # Check if coupon has already been used
        if coupon.get("used_by") is not None:
            return False
            
        # Add credits to user
        credits = coupon.get("credits", 0)
        if self.add_credits(user_id, credits, f"coupon_{coupon_code}"):
            # Mark coupon as used
            self.users["coupons"][coupon_code]["used_by"] = user_id
            self.users["coupons"][coupon_code]["used_at"] = datetime.now().isoformat()
            self._save_users()
            return True
            
        return False
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return self._hash_password(password) == password_hash