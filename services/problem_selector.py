"""
Problem Selector Service
Intelligently selects problems based on user preferences
"""

import logging
import random
from typing import Optional, Dict, Any, List

from services import codeforces_api, atcoder_api, leetcode_api

logger = logging.getLogger(__name__)


async def get_random_problem(rating: int = None, platform: str = 'codeforces') -> Optional[Dict[str, Any]]:
    """
    Get a random problem from specified platform.
    
    Args:
        rating: Problem difficulty rating (Codeforces: 800-3500)
        platform: 'codeforces', 'atcoder', or 'leetcode'
    
    Returns:
        Problem dictionary with name, rating, tags, url
    """
    if platform.lower() == 'codeforces':
        return await get_codeforces_problem(rating)
    elif platform.lower() == 'atcoder':
        return await get_atcoder_problem()
    elif platform.lower() == 'leetcode':
        return await get_leetcode_problem()
    else:
        # Default to Codeforces
        return await get_codeforces_problem(rating)


async def get_codeforces_problem(rating: int = None) -> Optional[Dict[str, Any]]:
    """
    Get a random Codeforces problem.
    """
    try:
        if rating:
            # Get problems within ±100 of target rating
            problems = await codeforces_api.get_problems_by_rating(
                rating - 100, rating + 100
            )
        else:
            # Get all problems
            problemset = await codeforces_api.get_problemset()
            problems = problemset.get('problems', []) if problemset else None
        
        if not problems or len(problems) == 0:
            logger.error("No problems found")
            return None
        
        # Select random problem
        problem = random.choice(problems)
        
        # Format response
        contest_id = problem.get('contestId')
        index = problem.get('index')
        
        if not contest_id or not index:
            return None
        
        return {
            'name': problem.get('name', 'Unknown'),
            'rating': problem.get('rating', 'N/A'),
            'tags': problem.get('tags', []),
            'url': codeforces_api.format_problem_url(contest_id, index),
            'platform': 'Codeforces',
            'contest_id': contest_id,
            'index': index
        }
    
    except Exception as e:
        logger.error(f"Error getting CF problem: {e}")
        return None


async def get_atcoder_problem() -> Optional[Dict[str, Any]]:
    """
    Get a random AtCoder problem.
    """
    try:
        problems = await atcoder_api.get_problems()
        
        if not problems or len(problems) == 0:
            logger.error("No AtCoder problems found")
            return None
        
        # Select random problem
        problem = random.choice(problems)
        
        return {
            'name': problem.get('title', problem.get('name', 'Unknown')),
            'rating': 'N/A',
            'tags': [],
            'url': atcoder_api.format_problem_url(
                problem.get('contest_id', ''),
                problem.get('id', '')
            ),
            'platform': 'AtCoder'
        }
    
    except Exception as e:
        logger.error(f"Error getting AtCoder problem: {e}")
        return None


async def get_leetcode_problem(difficulty: str = None) -> Optional[Dict[str, Any]]:
    """
    Get a random LeetCode problem.
    
    Args:
        difficulty: 'Easy', 'Medium', or 'Hard'
    """
    try:
        problem = await leetcode_api.get_random_problem(difficulty)
        
        if not problem:
            logger.error("No LeetCode problem found")
            return None
        
        return {
            'name': problem.get('title', 'Unknown'),
            'rating': problem.get('difficulty', 'N/A'),
            'tags': [tag['name'] for tag in problem.get('topicTags', [])],
            'url': leetcode_api.format_problem_url(problem.get('titleSlug', '')),
            'platform': 'LeetCode'
        }
    
    except Exception as e:
        logger.error(f"Error getting LeetCode problem: {e}")
        return None


async def get_problem_by_topic(topic: str, rating: int = None, 
                               platform: str = 'codeforces') -> Optional[Dict[str, Any]]:
    """
    Get a problem filtered by topic/tag.
    
    Args:
        topic: Problem topic (e.g., 'dp', 'graphs', 'greedy')
        rating: Optional difficulty rating
        platform: Platform to search on
    
    Returns:
        Problem dictionary
    """
    if platform.lower() == 'codeforces':
        return await get_codeforces_problem_by_topic(topic, rating)
    elif platform.lower() == 'leetcode':
        return await get_leetcode_problem_by_topic(topic)
    else:
        return await get_codeforces_problem_by_topic(topic, rating)


async def get_codeforces_problem_by_topic(topic: str, rating: int = None) -> Optional[Dict[str, Any]]:
    """
    Get Codeforces problem by topic.
    """
    try:
        # Search problems by tag
        problems = await codeforces_api.search_problems_by_tags([topic])
        
        if not problems or len(problems) == 0:
            logger.error(f"No problems found for topic: {topic}")
            return None
        
        # Filter by rating if specified
        if rating:
            problems = [
                p for p in problems
                if 'rating' in p and abs(p['rating'] - rating) <= 200
            ]
        
        if not problems:
            return None
        
        # Select random problem
        problem = random.choice(problems)
        
        contest_id = problem.get('contestId')
        index = problem.get('index')
        
        if not contest_id or not index:
            return None
        
        return {
            'name': problem.get('name', 'Unknown'),
            'rating': problem.get('rating', 'N/A'),
            'tags': problem.get('tags', []),
            'url': codeforces_api.format_problem_url(contest_id, index),
            'platform': 'Codeforces'
        }
    
    except Exception as e:
        logger.error(f"Error getting CF problem by topic: {e}")
        return None


async def get_leetcode_problem_by_topic(topic: str) -> Optional[Dict[str, Any]]:
    """
    Get LeetCode problem by topic.
    """
    try:
        problems = await leetcode_api.get_problems_by_topic(topic)
        
        if not problems or len(problems) == 0:
            logger.error(f"No LeetCode problems found for topic: {topic}")
            return None
        
        # Select random problem
        problem = random.choice(problems)
        
        return {
            'name': problem.get('title', 'Unknown'),
            'rating': problem.get('difficulty', 'N/A'),
            'tags': [tag['name'] for tag in problem.get('topicTags', [])],
            'url': leetcode_api.format_problem_url(problem.get('titleSlug', '')),
            'platform': 'LeetCode'
        }
    
    except Exception as e:
        logger.error(f"Error getting LeetCode problem by topic: {e}")
        return None


def normalize_topic(topic: str) -> str:
    """
    Normalize topic name to match API expectations.
    """
    # Common aliases
    topic_map = {
        'dp': 'dp',
        'dynamic programming': 'dp',
        'graph': 'graphs',
        'tree': 'trees',
        'bfs': 'graphs',
        'dfs': 'graphs',
        'binary search': 'binary search',
        'bs': 'binary search',
        'greedy': 'greedy',
        'math': 'math',
        'implementation': 'implementation',
        'brute force': 'brute force',
        'constructive': 'constructive algorithms',
        'strings': 'strings',
        'sortings': 'sortings',
        'number theory': 'number theory',
        'combinatorics': 'combinatorics',
        'geometry': 'geometry'
    }
    
    return topic_map.get(topic.lower(), topic)


async def get_problems_for_practice(user_rating: int, count: int = 5) -> List[Dict[str, Any]]:
    """
    Get a list of problems suitable for practice based on user rating.
    Returns mix of problems slightly below, at, and above user rating.
    """
    problems = []
    
    # Get problems at different difficulty levels
    ratings = [
        user_rating - 200,  # Easier
        user_rating,        # Current level
        user_rating + 200   # Challenging
    ]
    
    for rating in ratings:
        try:
            problem = await get_codeforces_problem(rating)
            if problem:
                problems.append(problem)
                if len(problems) >= count:
                    break
        except Exception as e:
            logger.error(f"Error getting practice problem: {e}")
            continue
    
    return problems
