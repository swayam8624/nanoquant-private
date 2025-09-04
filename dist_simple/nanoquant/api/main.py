"""
FastAPI application for NanoQuant
Provides REST API endpoints for model compression
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import secrets
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory session storage (in production, use Redis or database)
user_sessions = {}

app = FastAPI(
    title="NanoQuant API",
    description="API for compressing LLMs into NanoQuants",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import user management
from nanoquant.core.user_management import UserManager
user_manager = UserManager()

# Try to import cloud integration and payment processor
try:
    from nanoquant.core.cloud_integration import SocialAuth, PaymentProcessor
    CLOUD_AVAILABLE = True
except ImportError:
    CLOUD_AVAILABLE = False
    SocialAuth = None
    PaymentProcessor = None

class CompressionRequest(BaseModel):
    model_id: str
    compression_level: str = "medium"
    push_to_ollama: bool = True
    preserve_super_weights: bool = False
    custom_config: Optional[Dict[str, Any]] = None

class CompressionResponse(BaseModel):
    model_id: str
    generated_models: List[Dict[str, Any]]
    output_directory: str
    ollama_tags: List[str]
    pull_commands: Dict[str, str]

class ModelInfoResponse(BaseModel):
    model_id: str
    architecture: str
    model_family: str
    hidden_size: Optional[int]
    num_layers: Optional[int]
    recommended_compression: Dict[str, Any]

class UserRegistrationRequest(BaseModel):
    email: str
    password: str
    social_id: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: str
    password: str

class SocialLoginRequest(BaseModel):
    provider: str  # 'google' or 'github'
    code: str

class UserProfileResponse(BaseModel):
    email: str
    credits: int
    tier: str
    created_at: str
    compression_history: List[Any]
    last_login: str

class CouponRedemptionRequest(BaseModel):
    coupon_code: str

class PaymentRequest(BaseModel):
    amount: int
    currency: str = "usd"
    payment_method: str  # 'stripe', 'razorpay', 'paypal'
    provider_data: Optional[Dict[str, Any]] = None

class PaymentResponse(BaseModel):
    payment_id: str
    client_secret: Optional[str]
    payment_url: Optional[str]
    status: str

class UserSession(BaseModel):
    user_id: str
    session_token: str

def get_current_user(authorization: str = Header(None)):
    """Dependency to get current user from authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Extract token from "Bearer <token>" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    # Look up user by session token
    for user_id, session_token in user_sessions.items():
        if session_token == token:
            return user_id
    
    raise HTTPException(status_code=401, detail="Invalid or expired session")

@app.get("/")
async def root():
    return {"message": "Welcome to NanoQuant API", "version": "1.0.0"}

@app.post("/auth/register")
async def register_user(request: UserRegistrationRequest):
    """Register a new user"""
    try:
        user_id = user_manager.register_user(request.email, request.password, request.social_id)
        if user_id is None:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create session token
        session_token = secrets.token_urlsafe(32)
        user_sessions[user_id] = session_token
        
        return {
            "user_id": user_id,
            "session_token": session_token,
            "message": "User registered successfully"
        }
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login")
async def login_user(request: UserLoginRequest):
    """Authenticate a user"""
    try:
        user_id = user_manager.authenticate_user(request.email, request.password)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create session token
        session_token = secrets.token_urlsafe(32)
        user_sessions[user_id] = session_token
        
        return {
            "user_id": user_id,
            "session_token": session_token,
            "message": "Login successful"
        }
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/social")
async def social_login(request: SocialLoginRequest, req: Request):
    """Authenticate a user via social login"""
    if not CLOUD_AVAILABLE or not SocialAuth:
        raise HTTPException(status_code=501, detail="Social authentication not available")
    
    try:
        social_auth = SocialAuth()
        redirect_uri = f"{req.base_url}auth/social/callback"
        
        if request.provider == "google":
            user_info = social_auth.verify_google_token(request.code, redirect_uri)
        elif request.provider == "github":
            user_info = social_auth.verify_github_token(request.code, redirect_uri)
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Failed to authenticate with social provider")
        
        # Check if user exists, if not create new user
        user_id = user_manager.authenticate_social_user(user_info["id"], request.provider)
        if not user_id:
            # Create new user
            user_id = user_manager.register_user(user_info["email"], None, user_info["id"])
            if not user_id:
                raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create session token
        session_token = secrets.token_urlsafe(32)
        user_sessions[user_id] = session_token
        
        return {
            "user_id": user_id,
            "session_token": session_token,
            "message": "Social login successful"
        }
    except Exception as e:
        logger.error(f"Error during social login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/social/google")
async def google_auth_url(req: Request):
    """Get Google authentication URL"""
    if not CLOUD_AVAILABLE or not SocialAuth:
        raise HTTPException(status_code=501, detail="Social authentication not available")
    
    try:
        social_auth = SocialAuth()
        redirect_uri = f"{req.base_url}auth/social/callback"
        auth_url = social_auth.google_auth_url(redirect_uri)
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Error generating Google auth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/social/github")
async def github_auth_url(req: Request):
    """Get GitHub authentication URL"""
    if not CLOUD_AVAILABLE or not SocialAuth:
        raise HTTPException(status_code=501, detail="Social authentication not available")
    
    try:
        social_auth = SocialAuth()
        redirect_uri = f"{req.base_url}auth/social/callback"
        auth_url = social_auth.github_auth_url(redirect_uri)
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Error generating GitHub auth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: str = Depends(get_current_user)):
    """Get user profile information"""
    try:
        profile = user_manager.get_user_profile(user_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/coupons/redeem")
async def redeem_coupon(request: CouponRedemptionRequest, user_id: str = Depends(get_current_user)):
    """Redeem a coupon code for credits"""
    try:
        success = user_manager.redeem_coupon(user_id, request.coupon_code)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid or expired coupon code")
        
        # Get updated user profile
        profile = user_manager.get_user_profile(user_id)
        
        return {
            "message": "Coupon redeemed successfully",
            "credits_added": profile.get("credits", 0),
            "new_balance": profile.get("credits", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redeeming coupon: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/payments/create")
async def create_payment(request: PaymentRequest, user_id: str = Depends(get_current_user)):
    """Create a payment for credits"""
    if not CLOUD_AVAILABLE or not PaymentProcessor:
        raise HTTPException(status_code=501, detail="Payment processing not available")
    
    try:
        payment_processor = PaymentProcessor()
        
        if request.payment_method == "stripe":
            client_secret = payment_processor.create_stripe_payment_intent(request.amount, request.currency)
            if client_secret:
                return PaymentResponse(
                    payment_id="stripe_payment",
                    client_secret=client_secret,
                    status="created"
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to create Stripe payment")
        
        elif request.payment_method == "razorpay":
            order = payment_processor.create_razorpay_order(request.amount, request.currency)
            if order:
                return PaymentResponse(
                    payment_id=order["id"],
                    payment_url=f"https://rzp.io/i/{order['id']}",
                    status="created"
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to create Razorpay order")
        
        elif request.payment_method == "paypal":
            order = payment_processor.create_paypal_order(request.amount, request.currency)
            if order:
                return PaymentResponse(
                    payment_id=order["id"],
                    payment_url=order["links"][1]["href"] if len(order.get("links", [])) > 1 else None,
                    status="created"
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to create PayPal order")
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported payment method")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/payments/verify")
async def verify_payment(payment_id: str, provider: str = "stripe", user_id: str = Depends(get_current_user)):
    """Verify payment completion and add credits"""
    if not CLOUD_AVAILABLE or not PaymentProcessor:
        raise HTTPException(status_code=501, detail="Payment processing not available")
    
    try:
        payment_processor = PaymentProcessor()
        verified = payment_processor.verify_payment(payment_id, provider)
        
        if verified:
            # Add credits based on payment amount
            # This is a simplified calculation - in reality, you'd have a pricing table
            credits_to_add = 10 * (int(payment_id.split("_")[-1]) if "_" in payment_id else 10)
            
            if user_manager.add_credits(user_id, credits_to_add, f"payment_{payment_id}"):
                return {
                    "message": "Payment verified and credits added",
                    "credits_added": credits_to_add
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to add credits")
        else:
            raise HTTPException(status_code=400, detail="Payment verification failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compression/start", response_model=CompressionResponse)
async def compress_model(request: CompressionRequest, user_id: str = Depends(get_current_user)):
    """
    Compress a model into NanoQuants
    """
    try:
        logger.info(f"Compression request received for model: {request.model_id}")
        
        # Import here to avoid circular imports
        from nanoquant.core.compression_pipeline import CompressionPipeline
        
        # Validate compression level
        valid_levels = ["light", "medium", "heavy", "extreme", "ultra", "nano", "atomic"]
        if request.compression_level not in valid_levels:
            raise HTTPException(status_code=400, detail=f"Invalid compression level. Valid levels: {valid_levels}")
        
        # Check if user has access to this compression level
        if not user_manager.check_compression_access(user_id, request.compression_level):
            raise HTTPException(status_code=403, detail="Insufficient credits or access level for this compression level")
        
        # Create pipeline
        pipeline = CompressionPipeline()
        
        # Process model
        if request.custom_config:
            result = pipeline.process_custom_model(
                request.model_id,
                request.custom_config,
                push_to_ollama=request.push_to_ollama,
                user_id=user_id
            )
        else:
            # Add preserve_super_weights to config if requested
            if request.preserve_super_weights:
                # This would be handled in the compression engine
                pass
                
            result = pipeline.process_model(
                request.model_id,
                request.compression_level,
                push_to_ollama=request.push_to_ollama,
                user_id=user_id
            )
        
        logger.info(f"Compression completed successfully for model: {request.model_id}")
        return CompressionResponse(**result)
    except PermissionError as e:
        logger.warning(f"Permission error: {e}")
        raise HTTPException(status_code=403, detail="Access denied. Please check your credits and subscription level.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during compression: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/compression-levels")
async def get_compression_levels(user_id: str = Depends(get_current_user)):
    """Get available compression levels with user-specific restrictions"""
    try:
        # Get user profile to determine access level
        profile = user_manager.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Define compression levels with descriptions
        levels = {
            "light": {
                "name": "Light",
                "description": "50-70% size reduction, quality-critical applications",
                "cost": 0,
                "accessible": True
            },
            "medium": {
                "name": "Medium",
                "description": "70-85% size reduction, balanced compression/quality",
                "cost": 0,
                "accessible": True
            },
            "heavy": {
                "name": "Heavy",
                "description": "85-92% size reduction, significant size reduction",
                "cost": 10,
                "accessible": user_manager.check_compression_access(user_id, "heavy")
            },
            "extreme": {
                "name": "Extreme",
                "description": "92-96% size reduction, maximum compression",
                "cost": 25,
                "accessible": user_manager.check_compression_access(user_id, "extreme")
            },
            "ultra": {
                "name": "Ultra",
                "description": "96-98% size reduction, extreme compression with advanced techniques",
                "cost": 50,
                "accessible": user_manager.check_compression_access(user_id, "ultra")
            },
            "nano": {
                "name": "Nano",
                "description": "98-99% size reduction, sub-1-bit compression",
                "cost": 100,
                "accessible": user_manager.check_compression_access(user_id, "nano")
            },
            "atomic": {
                "name": "Atomic",
                "description": "99-99.5% size reduction, maximum compression with all ultra-advanced techniques",
                "cost": 200,
                "accessible": user_manager.check_compression_access(user_id, "atomic")
            }
        }
        
        return {
            "levels": levels,
            "user_credits": profile.get("credits", 0),
            "user_tier": profile.get("tier", "free")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compression levels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "NanoQuant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)