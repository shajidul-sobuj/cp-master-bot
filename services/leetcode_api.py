"""
LeetCode API Service
Handles interactions with LeetCode (GraphQL API)
"""

import logging
import aiohttp
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

BASE_URL = "https://leetcode.com"
GRAPHQL_URL = f"{BASE_URL}/graphql"


async def make_graphql_request(query: str, variables: dict = None) -> Optional[dict]:
    """Make async GraphQL request to LeetCode."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GRAPHQL_URL,
                json={'query': query, 'variables': variables or {}},
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data')
                else:
                    logger.error(f"HTTP error {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None


async def get_user_info(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user profile information.
    Returns user stats, rating, and problem counts.
    """
    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            username
            profile {
                ranking
                reputation
            }
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
                totalSubmissionNum {
                    difficulty
                    count
                }
            }
        }
    }
    """
    
    result = await make_graphql_request(query, {'username': username})
    
    if result and 'matchedUser' in result:
        return result['matchedUser']
    return None


async def get_user_submissions(username: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
    """
    Get recent submissions by user.
    """
    query = """
    query getRecentSubmissions($username: String!, $limit: Int!) {
        recentSubmissionList(username: $username, limit: $limit) {
            title
            titleSlug
            timestamp
            statusDisplay
            lang
        }
    }
    """
    
    result = await make_graphql_request(query, {
        'username': username,
        'limit': limit
    })
    
    if result and 'recentSubmissionList' in result:
        return result['recentSubmissionList']
    return None


async def get_daily_problem() -> Optional[Dict[str, Any]]:
    """
    Get today's daily challenge problem.
    """
    query = """
    query questionOfToday {
        activeDailyCodingChallengeQuestion {
            date
            link
            question {
                questionId
                title
                titleSlug
                difficulty
                topicTags {
                    name
                }
            }
        }
    }
    """
    
    result = await make_graphql_request(query)
    
    if result and 'activeDailyCodingChallengeQuestion' in result:
        return result['activeDailyCodingChallengeQuestion']
    return None


async def get_random_problem(difficulty: str = None) -> Optional[Dict[str, Any]]:
    """
    Get a random problem, optionally filtered by difficulty.
    Difficulty: Easy, Medium, Hard
    """
    query = """
    query randomQuestion($categorySlug: String!, $filters: QuestionListFilterInput) {
        randomQuestion(categorySlug: $categorySlug, filters: $filters) {
            questionId
            title
            titleSlug
            difficulty
            topicTags {
                name
            }
        }
    }
    """
    
    variables = {
        'categorySlug': 'all-code-essentials',
        'filters': {}
    }
    
    if difficulty:
        variables['filters']['difficulty'] = difficulty.upper()
    
    result = await make_graphql_request(query, variables)
    
    if result and 'randomQuestion' in result:
        return result['randomQuestion']
    return None


async def get_problems_by_topic(topic: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
    """
    Get problems by topic tag.
    """
    query = """
    query problemsetQuestionList($categorySlug: String!, $limit: Int!, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            filters: $filters
        ) {
            questions: data {
                questionId
                title
                titleSlug
                difficulty
                topicTags {
                    name
                }
            }
        }
    }
    """
    
    variables = {
        'categorySlug': 'all-code-essentials',
        'limit': limit,
        'filters': {
            'tags': [topic]
        }
    }
    
    result = await make_graphql_request(query, variables)
    
    if result and 'problemsetQuestionList' in result:
        return result['problemsetQuestionList']['questions']
    return None


def format_problem_url(title_slug: str) -> str:
    """Format problem URL."""
    return f"{BASE_URL}/problems/{title_slug}/"


def get_difficulty_emoji(difficulty: str) -> str:
    """Get emoji for difficulty level."""
    difficulty_map = {
        'Easy': '🟢',
        'Medium': '🟡',
        'Hard': '🔴'
    }
    return difficulty_map.get(difficulty, '⚪')
