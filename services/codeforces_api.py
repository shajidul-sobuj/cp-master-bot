"""
Codeforces API Service
Handles all interactions with Codeforces API
"""

import logging
import aiohttp
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

BASE_URL = "https://codeforces.com/api"


async def make_request(endpoint: str, params: dict = None) -> Optional[dict]:
    """Make async request to Codeforces API."""
    url = f"{BASE_URL}/{endpoint}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['status'] == 'OK':
                        return data['result']
                    else:
                        logger.error(f"CF API error: {data.get('comment', 'Unknown')}")
                        return None
                else:
                    logger.error(f"HTTP error {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None


async def get_user_info(handle: str) -> Optional[Dict[str, Any]]:
    """
    Get user information by handle.
    Returns user rating, rank, and other details.
    """
    result = await make_request("user.info", {"handles": handle})
    
    if result and len(result) > 0:
        return result[0]
    return None


async def get_user_rating(handle: str) -> Optional[List[Dict[str, Any]]]:
    """
    Get user rating history.
    Returns list of rating changes.
    """
    return await make_request("user.rating", {"handle": handle})


async def get_user_submissions(handle: str, count: int = 100) -> Optional[List[Dict[str, Any]]]:
    """
    Get user's recent submissions.
    Returns list of submissions with verdict, problem info, etc.
    """
    return await make_request("user.status", {
        "handle": handle,
        "from": 1,
        "count": count
    })


async def get_contests() -> Optional[List[Dict[str, Any]]]:
    """
    Get list of all contests.
    Returns contest information including upcoming contests.
    """
    return await make_request("contest.list")


async def get_problemset(tags: List[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get problemset with optional tag filter.
    Returns problems and problem statistics.
    """
    params = {}
    if tags:
        params['tags'] = ';'.join(tags)
    
    return await make_request("problemset.problems", params)


async def get_problems_by_rating(min_rating: int, max_rating: int, 
                                tags: List[str] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Get problems filtered by rating range.
    """
    problemset = await get_problemset(tags)
    
    if not problemset or 'problems' not in problemset:
        return None
    
    problems = problemset['problems']
    
    # Filter by rating
    filtered = [
        p for p in problems
        if 'rating' in p and min_rating <= p['rating'] <= max_rating
    ]
    
    return filtered


async def get_problem_by_id(contest_id: int, index: str) -> Optional[Dict[str, Any]]:
    """
    Get specific problem by contest ID and index.
    """
    problemset = await get_problemset()
    
    if not problemset or 'problems' not in problemset:
        return None
    
    for problem in problemset['problems']:
        if (problem.get('contestId') == contest_id and 
            problem.get('index') == index):
            return problem
    
    return None


async def get_contest_standings(contest_id: int, handle: str = None) -> Optional[Dict[str, Any]]:
    """
    Get contest standings.
    If handle provided, returns specific user's standing.
    """
    params = {"contestId": contest_id, "from": 1, "count": 100}
    if handle:
        params['handles'] = handle
    
    return await make_request("contest.standings", params)


async def search_problems_by_tags(tags: List[str], limit: int = 50) -> Optional[List[Dict[str, Any]]]:
    """
    Search problems by tags.
    Returns list of problems matching all provided tags.
    """
    problemset = await get_problemset(tags)
    
    if not problemset or 'problems' not in problemset:
        return None
    
    problems = problemset['problems']
    
    # Filter to ensure all tags are present
    filtered = []
    for problem in problems:
        problem_tags = [t.lower() for t in problem.get('tags', [])]
        if all(tag.lower() in problem_tags for tag in tags):
            filtered.append(problem)
            if len(filtered) >= limit:
                break
    
    return filtered


def format_problem_url(contest_id: int, index: str) -> str:
    """Format problem URL."""
    return f"https://codeforces.com/problemset/problem/{contest_id}/{index}"


def format_contest_url(contest_id: int) -> str:
    """Format contest URL."""
    return f"https://codeforces.com/contest/{contest_id}"


def get_rank_color(rank: str) -> str:
    """Get emoji/color representation of rank."""
    rank_colors = {
        'newbie': '⚪',
        'pupil': '🟢',
        'specialist': '🔵',
        'expert': '💙',
        'candidate master': '💜',
        'master': '🟠',
        'international master': '🟠',
        'grandmaster': '🔴',
        'international grandmaster': '🔴',
        'legendary grandmaster': '🔴'
    }
    return rank_colors.get(rank.lower(), '⚪')
