"""
Duel Handler - Manages competitive duels between users
Commands: /duel, /accept, /decline, /duelstatus
"""

import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from database import (
    create_duel, get_pending_duel, update_duel_status, 
    get_user, create_or_update_user
)
from services.problem_selector import get_random_problem

logger = logging.getLogger(__name__)

# Duel duration in minutes
DUEL_DURATION = 60


async def challenge_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Challenge another user to a duel.
    Usage: /duel @username <rating>
    """
    chat = update.effective_chat
    user = update.effective_user
    
    # Check if in group
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text(
            "❌ Duels can only be initiated in groups!"
        )
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Invalid format!\n"
            "Usage: /duel @username <rating>\n"
            "Example: /duel @john 1400"
        )
        return
    
    # Parse arguments
    mentioned_user = context.args[0]
    
    try:
        problem_rating = int(context.args[1])
        if problem_rating < 800 or problem_rating > 3500:
            await update.message.reply_text(
                "❌ Rating must be between 800 and 3500!"
            )
            return
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid rating! Please provide a number."
        )
        return
    
    # Get mentioned user (this is simplified - in production use entities)
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "⚠️ Please reply to the user's message when challenging them!"
        )
        return
    
    challenged_user = update.message.reply_to_message.from_user
    
    if challenged_user.id == user.id:
        await update.message.reply_text(
            "😅 You can't challenge yourself!"
        )
        return
    
    # Check if challenged user has pending duel
    pending = get_pending_duel(challenged_user.id)
    if pending:
        await update.message.reply_text(
            f"❌ {challenged_user.first_name} already has a pending duel!"
        )
        return
    
    # Create users in DB if not exists
    create_or_update_user(user.id, user.username, user.first_name)
    create_or_update_user(challenged_user.id, challenged_user.username, 
                         challenged_user.first_name)
    
    # Create duel
    duel_id = create_duel(chat.id, user.id, challenged_user.id, problem_rating)
    
    if not duel_id:
        await update.message.reply_text(
            "❌ Failed to create duel. Please try again!"
        )
        return
    
    # Send challenge message
    challenge_text = f"""
⚔️ **DUEL CHALLENGE!** ⚔️

{user.first_name} has challenged {challenged_user.first_name}!

**Problem Rating:** {problem_rating}
**Duration:** {DUEL_DURATION} minutes

{challenged_user.first_name}, use /accept to accept or /decline to decline!
    """
    
    await update.message.reply_text(challenge_text, parse_mode='Markdown')


async def accept_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Accept a pending duel.
    Usage: /accept
    """
    user = update.effective_user
    
    # Get pending duel
    duel = get_pending_duel(user.id)
    
    if not duel:
        await update.message.reply_text(
            "❌ You don't have any pending duel challenges!"
        )
        return
    
    # Get problem
    problem_rating = duel['problem_rating']
    problem = await get_random_problem(problem_rating)
    
    if not problem:
        await update.message.reply_text(
            "❌ Failed to fetch problem. Please try again!"
        )
        return
    
    # Update duel status
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=DUEL_DURATION)
    
    update_duel_status(
        duel['duel_id'],
        'active',
        start_time=start_time,
        end_time=end_time,
        problem_name=problem['name'],
        problem_url=problem['url']
    )
    
    # Send duel start message
    duel_text = f"""
🔥 **DUEL STARTED!** 🔥

⏰ Duration: {DUEL_DURATION} minutes
📝 **Problem:** {problem['name']}
⭐ **Rating:** {problem_rating}

🔗 **Problem Link:** {problem['url']}

First to solve wins! Good luck! 🚀

Use /duelstatus to check time remaining.
    """
    
    await update.message.reply_text(duel_text, parse_mode='Markdown')


async def decline_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Decline a pending duel.
    Usage: /decline
    """
    user = update.effective_user
    
    # Get pending duel
    duel = get_pending_duel(user.id)
    
    if not duel:
        await update.message.reply_text(
            "❌ You don't have any pending duel challenges!"
        )
        return
    
    # Update status
    update_duel_status(duel['duel_id'], 'declined')
    
    await update.message.reply_text(
        "❌ Duel declined. Maybe next time!"
    )


async def duel_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check status of ongoing duel.
    Usage: /duelstatus
    """
    user = update.effective_user
    
    # Get active duel for user
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM duels 
        WHERE (challenger_id = ? OR challenged_id = ?) 
        AND status = 'active'
        ORDER BY created_at DESC LIMIT 1
    ''', (user.id, user.id))
    
    duel = cursor.fetchone()
    conn.close()
    
    if not duel:
        await update.message.reply_text(
            "❌ You don't have any active duels!"
        )
        return
    
    duel = dict(duel)
    
    # Calculate remaining time
    end_time = datetime.fromisoformat(duel['end_time'])
    remaining = end_time - datetime.now()
    
    if remaining.total_seconds() <= 0:
        await update.message.reply_text(
            "⏰ **Time's up!**\n\n"
            "The duel has ended. Check submissions to determine winner!",
            parse_mode='Markdown'
        )
        update_duel_status(duel['duel_id'], 'completed')
        return
    
    minutes = int(remaining.total_seconds() // 60)
    seconds = int(remaining.total_seconds() % 60)
    
    status_text = f"""
⚔️ **Active Duel Status**

📝 **Problem:** {duel['problem_name']}
⏰ **Time Remaining:** {minutes}m {seconds}s

🔗 {duel['problem_url']}

Keep coding! 💪
    """
    
    await update.message.reply_text(status_text, parse_mode='Markdown')
