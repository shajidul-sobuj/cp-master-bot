"""
Rating Handler - Manages user ratings and comparisons
Commands: /cf, /compare, /leaderboard
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from database import get_user, create_or_update_user, set_user_handle, get_connection
from services.codeforces_api import get_user_info

logger = logging.getLogger(__name__)


async def set_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set Codeforces handle for the user.
    Usage: /cf <handle>
    """
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide your Codeforces handle!\n"
            "Usage: /cf <handle>\n"
            "Example: /cf tourist"
        )
        return
    
    handle = context.args[0]
    
    # Send "processing" message
    msg = await update.message.reply_text("🔍 Fetching your Codeforces data...")
    
    # Fetch user info from Codeforces API
    user_info = await get_user_info(handle)
    
    if not user_info:
        await msg.edit_text(
            f"❌ Handle '{handle}' not found on Codeforces!\n"
            "Please check your handle and try again."
        )
        return
    
    # Create/update user in database
    create_or_update_user(
        user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    # Set handle and rating info
    set_user_handle(user.id, 'cf', handle)
    
    # Update rating in database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET current_rating = ?, max_rating = ?, rank = ?
        WHERE user_id = ?
    ''', (
        user_info.get('rating', 0),
        user_info.get('maxRating', 0),
        user_info.get('rank', 'unrated'),
        user.id
    ))
    conn.commit()
    conn.close()
    
    # Format response
    rank = user_info.get('rank', 'unrated')
    rating = user_info.get('rating', 0)
    max_rating = user_info.get('maxRating', 0)
    
    await msg.edit_text(
        f"✅ **Handle set successfully!**\n\n"
        f"👤 **Handle:** {handle}\n"
        f"⭐ **Rank:** {rank.title()}\n"
        f"📊 **Rating:** {rating}\n"
        f"🏆 **Max Rating:** {max_rating}\n\n"
        f"You can now use /compare and /leaderboard commands!",
        parse_mode='Markdown'
    )


async def compare_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Compare two Codeforces users.
    Usage: /compare <user1> <user2>
    """
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Please provide two usernames to compare!\n"
            "Usage: /compare <user1> <user2>\n"
            "Example: /compare tourist jiangly"
        )
        return
    
    handle1, handle2 = context.args[0], context.args[1]
    
    msg = await update.message.reply_text("🔍 Comparing users...")
    
    # Fetch both users' info
    user1_info = await get_user_info(handle1)
    user2_info = await get_user_info(handle2)
    
    if not user1_info:
        await msg.edit_text(f"❌ Handle '{handle1}' not found!")
        return
    
    if not user2_info:
        await msg.edit_text(f"❌ Handle '{handle2}' not found!")
        return
    
    # Extract data
    u1_rating = user1_info.get('rating', 0)
    u1_max = user1_info.get('maxRating', 0)
    u1_rank = user1_info.get('rank', 'unrated')
    
    u2_rating = user2_info.get('rating', 0)
    u2_max = user2_info.get('maxRating', 0)
    u2_rank = user2_info.get('rank', 'unrated')
    
    # Determine winner
    if u1_rating > u2_rating:
        winner = f"🏆 {handle1} is ahead!"
        diff = u1_rating - u2_rating
    elif u2_rating > u1_rating:
        winner = f"🏆 {handle2} is ahead!"
        diff = u2_rating - u1_rating
    else:
        winner = "🤝 It's a tie!"
        diff = 0
    
    comparison_text = f"""
⚔️ **User Comparison**

**{handle1}**
⭐ Rank: {u1_rank.title()}
📊 Rating: {u1_rating}
🏆 Max: {u1_max}

**{handle2}**
⭐ Rank: {u2_rank.title()}
📊 Rating: {u2_rating}
🏆 Max: {u2_max}

{winner}
{f'📈 Rating Difference: {diff}' if diff > 0 else ''}
    """
    
    await msg.edit_text(comparison_text, parse_mode='Markdown')


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show leaderboard for the current chat.
    Usage: /leaderboard
    """
    chat = update.effective_chat
    
    # Get all users in database with CF handles
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, first_name, cf_handle, current_rating, rank
        FROM users
        WHERE cf_handle IS NOT NULL
        ORDER BY current_rating DESC
        LIMIT 10
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        await update.message.reply_text(
            "📊 No users have set their Codeforces handle yet!\n"
            "Use /cf <handle> to join the leaderboard."
        )
        return
    
    # Build leaderboard text
    leaderboard_text = "🏆 **Codeforces Leaderboard** 🏆\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for idx, user in enumerate(users, 1):
        username = user[0] or user[1] or "Unknown"
        handle = user[2]
        rating = user[3]
        rank = user[4] or "unrated"
        
        medal = medals[idx-1] if idx <= 3 else f"{idx}."
        leaderboard_text += f"{medal} **{username}** ({handle})\n"
        leaderboard_text += f"   📊 {rating} • {rank.title()}\n\n"
    
    await update.message.reply_text(leaderboard_text, parse_mode='Markdown')
