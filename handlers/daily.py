"""
Daily Problem Handler - Provides daily problems
Commands: /daily, /topic
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.problem_selector import get_random_problem, get_problem_by_topic

logger = logging.getLogger(__name__)


async def get_daily_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Get a random problem or problem by rating.
    Usage: /daily or /daily <rating>
    """
    rating = None
    
    if context.args:
        try:
            rating = int(context.args[0])
            if rating < 800 or rating > 3500:
                await update.message.reply_text(
                    "❌ Rating must be between 800 and 3500!\n"
                    "Common ratings: 800, 1000, 1200, 1400, 1600, 1800, 2000"
                )
                return
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid rating! Please provide a number.\n"
                "Example: /daily 1400"
            )
            return
    
    msg = await update.message.reply_text("🎲 Finding a problem for you...")
    
    # Get problem from service
    problem = await get_random_problem(rating)
    
    if not problem:
        await msg.edit_text(
            "❌ Couldn't fetch a problem right now. Please try again!"
        )
        return
    
    # Format problem message
    problem_text = f"""
📝 **Daily Problem Challenge**

**Problem:** {problem['name']}
**Rating:** {problem.get('rating', 'N/A')}
**Tags:** {', '.join(problem.get('tags', [])[:3])}

🔗 **Solve it here:** {problem['url']}

Good luck! 🚀
    """
    
    await msg.edit_text(problem_text, parse_mode='Markdown')


async def get_problem_by_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Get a problem by specific topic/tag.
    Usage: /topic <topic_name>
    """
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a topic!\n"
            "Usage: /topic <topic>\n"
            "Examples: /topic dp, /topic graphs, /topic greedy\n\n"
            "Common topics: dp, greedy, math, implementation, graphs, "
            "binary search, data structures"
        )
        return
    
    topic = ' '.join(context.args)
    
    msg = await update.message.reply_text(f"🔍 Finding a {topic} problem...")
    
    # Get problem by topic
    problem = await get_problem_by_topic(topic)
    
    if not problem:
        await msg.edit_text(
            f"❌ No problems found for topic: {topic}\n"
            "Try different topic or use /daily for random problem."
        )
        return
    
    # Format problem message
    problem_text = f"""
📝 **{topic.title()} Problem**

**Problem:** {problem['name']}
**Rating:** {problem.get('rating', 'N/A')}
**Tags:** {', '.join(problem.get('tags', []))}

🔗 **Solve it here:** {problem['url']}

Master this topic! 💪
    """
    
    await msg.edit_text(problem_text, parse_mode='Markdown')
