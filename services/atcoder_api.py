"""
AtCoder API Service
Handles interactions with AtCoder (unofficial API/scraping)
"""

import logging
import aiohttp
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = "https://atcoder.jp"
KENKOOOO_API = "https://kenkoooo.com/atcoder/resources"


async def make_request(url: str, params: dict = None) -> Optional[Any]:
    """Make async request."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"HTTP error {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None


async def get_user_info(handle: str) -> Optional[Dict[str, Any]]:
    """
    Get user information using Kenkoooo API.
    Returns user rating and statistics.
    """
    # Get user submissions count
    url = f"{KENKOOOO_API}/ac.json"
    submissions = await make_request(url)
    
    if not submissions:
        return None
    
    # Filter user submissions
    user_submissions = [s for s in submissions if s.get('user_id') == handle]
    
    if not user_submissions:
        return None
    
    return {
        'handle': handle,
        'solved_count': len(user_submissions),
        'platform': 'atcoder'
    }


async def get_contests() -> Optional[List[Dict[str, Any]]]:
    """
    Get list of AtCoder contests.
    """
    url = f"{KENKOOOO_API}/contests.json"
    contests = await make_request(url)
    
    if not contests:
        return None
    
    # Filter upcoming contests
    now = datetime.now().timestamp()
    upcoming = []
    
    for contest in contests:
        start_epoch = contest.get('start_epoch_second', 0)
        if start_epoch > now:
            upcoming.append({
                'id': contest['id'],
                'title': contest['title'],
                'start_time': start_epoch,
                'duration': contest.get('duration_second', 0),
                'url': f"{BASE_URL}/contests/{contest['id']}"
            })
    
    return upcoming


async def get_problems() -> Optional[List[Dict[str, Any]]]:
    """
    Get all problems from AtCoder.
    """
    url = f"{KENKOOOO_API}/problems.json"
    return await make_request(url)


async def get_user_submissions(handle: str) -> Optional[List[Dict[str, Any]]]:
    """
    Get user submissions.
    """
    url = f"{KENKOOOO_API}/ac.json"
    all_submissions = await make_request(url)
    
    if not all_submissions:
        return None
    
    # Filter by user
    user_submissions = [s for s in all_submissions if s.get('user_id') == handle]
    return user_submissions


def format_problem_url(contest_id: str, problem_id: str) -> str:
    """Format problem URL."""
    return f"{BASE_URL}/contests/{contest_id}/tasks/{problem_id}"


def format_contest_url(contest_id: str) -> str:
    """Format contest URL."""
    return f"{BASE_URL}/contests/{contest_id}"
