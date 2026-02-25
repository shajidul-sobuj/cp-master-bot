"""
Contest Reminder Handler - Manages contest notifications
Commands: /contests, /subscribe, /unsubscribe
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from database import (
    get_chat, create_or_update_chat, update_chat_reminders,
    get_upcoming_contests
)
from services.codeforces_api import get_contests as get_cf_contests

logger = logging.getLogger(__name__)


async def show_contests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show upcoming contests from all platforms.
    Usage: /contests
    """
    msg = await update.message.reply_text("🔍 Fetching upcoming contests...")
    
    # Fetch contests from Codeforces
    cf_contests = await get_cf_contests()
    
    if not cf_contests:
        await msg.edit_text(
            "❌ Couldn't fetch contests. Please try again later!"
        )
        return
    
    # Filter upcoming contests
    now = datetime.now()
    upcoming = []
    
    for contest in cf_contests:
        start_time = datetime.fromtimestamp(contest['startTimeSeconds'])
        if start_time > now:
            upcoming.append({
                'name': contest['name'],
                'start_time': start_time,
                'duration': contest['durationSeconds'] // 60,  # in minutes
                'platform': 'Codeforces',
                'url': f"https://codeforces.com/contest/{contest['id']}"
            })
    
    if not upcoming:
        await msg.edit_text(
            "📅 No upcoming contests found!\n"
            "Check back later."
        )
        return
    
    # Sort by start time
    upcoming.sort(key=lambda x: x['start_time'])
    
    # Format message
    contests_text = "📅 **Upcoming Contests** 📅\n\n"
    
    for idx, contest in enumerate(upcoming[:5], 1):  # Show top 5
        start = contest['start_time']
        time_until = start - now
        
        days = time_until.days
        hours = time_until.seconds // 3600
        minutes = (time_until.seconds % 3600) // 60
        
        time_str = ""
        if days > 0:
            time_str = f"in {days}d {hours}h"
        elif hours > 0:
            time_str = f"in {hours}h {minutes}m"
        else:
            time_str = f"in {minutes}m"
        
        contests_text += f"**{idx}. {contest['name']}**\n"
        contests_text += f"🏢 Platform: {contest['platform']}\n"
        contests_text += f"⏰ Starts: {time_str}\n"
        contests_text += f"⏱️ Duration: {contest['duration']} min\n"
        contests_text += f"🔗 {contest['url']}\n\n"
    
    contests_text += "Use /subscribe to get contest reminders!"
    
    await msg.edit_text(contests_text, parse_mode='Markdown')


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Subscribe to contest reminders.
    Usage: /subscribe
    """
    chat = update.effective_chat
    
    # Create/update chat in database
    create_or_update_chat(chat.id, chat.type, chat.title)
    
    # Enable reminders
    success = update_chat_reminders(chat.id, True)
    
    if success:
        await update.message.reply_text(
            "✅ **Contest reminders enabled!**\n\n"
            "You'll be notified 30 minutes before contests start.\n"
            "Use /unsubscribe to disable reminders.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Failed to enable reminders. Please try again!"
        )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Unsubscribe from contest reminders.
    Usage: /unsubscribe
    """
    chat = update.effective_chat
    
    # Disable reminders
    success = update_chat_reminders(chat.id, False)
    
    if success:
        await update.message.reply_text(
            "❌ **Contest reminders disabled!**\n\n"
            "You won't receive contest notifications.\n"
            "Use /subscribe to enable them again.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Failed to disable reminders. Please try again!"
        )


async def send_contest_reminder(context, chat_id, contest_info):
    """
    Send contest reminder to a chat.
    This is called by the job scheduler.
    """
    reminder_text = f"""
🔔 **Contest Starting Soon!** 🔔

**{contest_info['name']}**

🏢 Platform: {contest_info['platform']}
⏰ Starts in: 30 minutes
⏱️ Duration: {contest_info['duration']} minutes

🔗 {contest_info['url']}

Get ready! Good luck! 🚀
    """
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=reminder_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send reminder to {chat_id}: {e}")
