#!/usr/bin/env python3
"""
Debug credit system enforcement issues
"""

import os
import sys
import logging

# Add the nanoquant package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_credit_enforcement():
    """Debug credit system enforcement"""
    try:
        from nanoquant.core.user_management import UserManager
        
        user_manager = UserManager()
        
        # Create test user with 5 credits
        test_user_id = user_manager.register_user("debug@test.com", "password123")
        user_manager.users["users"][test_user_id]["credits"] = 5
        user_manager.users["users"][test_user_id]["tier"] = "free"
        user_manager._save_users()
        
        logger.info(f"Created user {test_user_id} with 5 credits, free tier")
        
        # Test expensive levels
        expensive_levels = ["ultra", "nano", "atomic"]
        level_costs = {"ultra": 50, "nano": 100, "atomic": 200}
        
        for level in expensive_levels:
            cost = level_costs[level]
            has_access = user_manager.check_compression_access(test_user_id, level)
            trials_used = user_manager._get_trials_count(test_user_id, level)
            
            logger.info(f"Level: {level}, Cost: {cost}, Credits: 5, Trials used: {trials_used}, Access: {has_access}")
            
            # Should be False for users with insufficient credits
            if has_access and cost > 5:
                logger.error(f"BUG: User with 5 credits has access to {level} (cost: {cost})")
            else:
                logger.info(f"✓ Correctly blocked access to {level}")
        
        return True
        
    except Exception as e:
        logger.error(f"Credit debug failed: {e}")
        return False

def test_trials_system():
    """Test the trials system specifically"""
    try:
        from nanoquant.core.user_management import UserManager
        
        user_manager = UserManager()
        
        # Create fresh user
        test_user_id = user_manager.register_user("trials@test.com", "password123")
        user_manager.users["users"][test_user_id]["credits"] = 0  # No credits
        user_manager.users["users"][test_user_id]["tier"] = "free"
        user_manager._save_users()
        
        logger.info(f"Created user {test_user_id} with 0 credits, free tier")
        
        # Test trial access
        level = "ultra"
        trials_used = user_manager._get_trials_count(test_user_id, level)
        has_access = user_manager.check_compression_access(test_user_id, level)
        
        logger.info(f"Trials used for {level}: {trials_used}")
        logger.info(f"Access to {level} with 0 credits: {has_access}")
        
        # Should have access for first 2 trials
        if trials_used < 2 and has_access:
            logger.info("✓ Trial system working correctly")
            return True
        elif trials_used >= 2 and not has_access:
            logger.info("✓ Trial limit enforced correctly")
            return True
        else:
            logger.error("✗ Trial system has issues")
            return False
            
    except Exception as e:
        logger.error(f"Trials test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Debugging credit system...")
    debug_credit_enforcement()
    test_trials_system()
