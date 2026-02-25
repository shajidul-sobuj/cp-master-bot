"""
Practice Tracker Handler - Tracks user solving progress
Commands: /sethandle, /streak, /report
"""

import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from database import (
    get_user, create_or_update_user, set_user_handle,
    get_streak, get_connection
)
from services.codeforces_api import get_user_submissions

logger = logging.getLogger(__name__)


async def set_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set Codeforces handle for tracking.
    Usage: /sethandle <handle>
    """
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide your Codeforces handle!\n"
            "Usage: /sethandle <handle>\n"
            "Example: /sethandle tourist"
        )
        return
    
    handle = context.args[0]
    
    # Create/update user
    create_or_update_user(user.id, user.username, user.first_name)
    
    # Set handle
    success = set_user_handle(user.id, 'cf', handle)
    
    if success:
        await update.message.reply_text(
            f"✅ Handle set to: **{handle}**\n\n"
            f"Your solving progress will now be tracked!\n"
            f"Use /streak to check your solving streak.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Failed to set handle. Please try again!"
        )


async def show_streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show user's solving streak.
    Usage: /streak
    """
    user = update.effective_user
    
    # Get user from database
    user_data = get_user(user.id)
    
    if not user_data or not user_data.get('cf_handle'):
        await update.message.reply_text(
            "❌ You haven't set your Codeforces handle yet!\n"
            "Use /sethandle <handle> to start tracking."
        )
        return
    
    handle = user_data['cf_handle']
    
    msg = await update.message.reply_text("📊 Calculating your streak...")
    
    # Get submissions from Codeforces
    submissions = await get_user_submissions(handle, count=100)
    
    if not submissions:
        await msg.edit_text(
            "❌ Couldn't fetch your submissions. Please try again!"
        )
        return
    
    # Calculate streak from submissions
    streak_data = calculate_streak_from_submissions(submissions)
    
    # Update streak in database
    from database import update_streak
    update_streak(user.id)
    
    # Get updated streak data
    streak = get_streak(user.id) or {
        'current_streak': 0,
        'max_streak': 0,
        'total_solves': 0
    }
    
    # Format message
    current = streak_data['current_streak']
    max_streak = streak_data['max_streak']
    total = streak_data['total_solves']
    
    fire_emoji = "🔥" * min(current, 5)
    
    streak_text = f"""
{fire_emoji} **Your Solving Streak** {fire_emoji}

🎯 **Current Streak:** {current} days
🏆 **Max Streak:** {max_streak} days
📝 **Total Solves:** {total} problems

{get_motivation_message(current)}
    """
    
    await msg.edit_text(streak_text, parse_mode='Markdown')


async def weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show weekly solving report.
    Usage: /report
    """
    user = update.effective_user
    
    # Get user from database
    user_data = get_user(user.id)
    
    if not user_data or not user_data.get('cf_handle'):
        await update.message.reply_text(
            "❌ You haven't set your Codeforces handle yet!\n"
            "Use /sethandle <handle> to start tracking."
        )
        return
    
    handle = user_data['cf_handle']
    
    msg = await update.message.reply_text("📊 Generating your weekly report...")
    
    # Get recent submissions
    submissions = await get_user_submissions(handle, count=200)
    
    if not submissions:
        await msg.edit_text(
            "❌ Couldn't fetch your submissions. Please try again!"
        )
        return
    
    # Calculate weekly stats
    week_ago = datetime.now() - timedelta(days=7)
    week_submissions = [
        s for s in submissions 
        if datetime.fromtimestamp(s['creationTimeSeconds']) > week_ago
    ]
    
    # Count accepted solutions
    accepted = [s for s in week_submissions if s['verdict'] == 'OK']
    
    # Get unique problems solved
    unique_problems = set()
    for s in accepted:
        problem_id = f"{s['problem']['contestId']}-{s['problem']['index']}"
        unique_problems.add(problem_id)
    
    # Count by difficulty
    difficulty_count = {}
    for s in accepted:
        rating = s['problem'].get('rating', 'unrated')
        difficulty_count[rating] = difficulty_count.get(rating, 0) + 1
    
    # Format report
    report_text = f"""
📊 **Weekly Progress Report**

📅 **Last 7 Days**

✅ **Problems Solved:** {len(unique_problems)}
📝 **Total Submissions:** {len(week_submissions)}
🎯 **Acceptance Rate:** {len(accepted)/len(week_submissions)*100:.1f}%

**By Difficulty:**
"""
    
    for rating in sorted([r for r in difficulty_count.keys() if isinstance(r, int)]):
        report_text += f"• {rating}: {difficulty_count[rating]} problems\n"
    
    report_text += f"\n{get_progress_message(len(unique_problems))}"
    
    await msg.edit_text(report_text, parse_mode='Markdown')


def calculate_streak_from_submissions(submissions):
    """Calculate streak from submission history."""
    if not submissions:
        return {'current_streak': 0, 'max_streak': 0, 'total_solves': 0}
    
    # Get only accepted submissions
    accepted = [s for s in submissions if s['verdict'] == 'OK']
    
    # Get unique dates
    solve_dates = set()
    for s in accepted:
        date = datetime.fromtimestamp(s['creationTimeSeconds']).date()
        solve_dates.add(date)
    
    # Sort dates
    sorted_dates = sorted(solve_dates, reverse=True)
    
    if not sorted_dates:
        return {'current_streak': 0, 'max_streak': 0, 'total_solves': 0}
    
    # Calculate current streak
    current_streak = 0
    today = datetime.now().date()
    
    for date in sorted_dates:
        expected_date = today - timedelta(days=current_streak)
        if date == expected_date:
            current_streak += 1
        else:
            break
    
    # Calculate max streak
    max_streak = 1
    temp_streak = 1
    
    for i in range(1, len(sorted_dates)):
        diff = (sorted_dates[i-1] - sorted_dates[i]).days
        if diff == 1:
            temp_streak += 1
            max_streak = max(max_streak, temp_streak)
        else:
            temp_streak = 1
    
    return {
        'current_streak': current_streak,
        'max_streak': max_streak,
        'total_solves': len(solve_dates)
    }


def get_motivation_message(streak):
    """Get motivational message based on streak."""
    if streak == 0:
        return "Start your journey today! 💪"
    elif streak < 7:
        return "Keep it up! You're building momentum! 🚀"
    elif streak < 30:
        return "Amazing consistency! Keep pushing! 🔥"
    elif streak < 100:
        return "Legendary streak! You're unstoppable! ⚡"
    else:
        return "Ultimate dedication! You're a CP master! 👑"


def get_progress_message(solved):
    """Get progress message based on problems solved."""
    if solved == 0:
        return "Time to start solving! 💻"
    elif solved < 5:
        return "Good start! Keep the momentum going! 💪"
    elif solved < 10:
        return "Great progress! You're on fire! 🔥"
    elif solved < 20:
        return "Incredible week! Outstanding work! ⚡"
    else:
        return "Phenomenal! You're crushing it! 👑"
