"""
CP Master Bot - Main Entry Point
A Telegram bot for competitive programming enthusiasts
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from database import init_db
from handlers import rating, daily, duel, tracker, reminder

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = f"""
🏆 **Welcome to CP Master Bot, {user.first_name}!**

Your ultimate competitive programming companion!

**📋 Available Commands:**

**Rating & Profile:**
• /cf <handle> - Set Codeforces handle
• /compare <user1> <user2> - Compare ratings
• /leaderboard - Group leaderboard

**Daily Problems:**
• /daily - Get random problem
• /daily <rating> - Problem by rating
• /topic <topic> - Problem by topic

**Contest Reminders:**
• /contests - Upcoming contests
• /subscribe - Enable reminders
• /unsubscribe - Disable reminders

**Duel System (Groups):**
• /duel @user <rating> - Challenge a user
• /accept - Accept duel
• /decline - Decline duel

**Practice Tracker:**
• /sethandle <handle> - Link CF handle
• /streak - Your current streak
• /report - Weekly progress

Let's start your CP journey! 🚀
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
📚 **CP Master Bot Help**

**Rating Commands:**
/cf <handle> - Link your Codeforces handle
/compare <user1> <user2> - Compare two users
/leaderboard - Show group rankings

**Daily Problems:**
/daily - Random problem
/daily 1400 - Problem with specific rating
/topic dp - Problem from specific topic

**Contest Reminders:**
/contests - Upcoming contests list
/subscribe - Enable contest notifications
/unsubscribe - Disable notifications

**Duel System:**
/duel @user 1400 - Challenge someone
/accept - Accept incoming duel
/decline - Decline duel
/duelstatus - Check ongoing duel

**Practice Tracker:**
/sethandle <handle> - Link your handle
/streak - Check solving streak
/report - Weekly solve report

Need more help? Join our support group!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the bot."""
    # Get token from environment variable
    TOKEN = os.getenv('BOT_TOKEN')
    
    if not TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    # Initialize database
    init_db()
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Rating handlers
    application.add_handler(CommandHandler("cf", rating.set_handle))
    application.add_handler(CommandHandler("compare", rating.compare_users))
    application.add_handler(CommandHandler("leaderboard", rating.leaderboard))
    
    # Daily problem handlers
    application.add_handler(CommandHandler("daily", daily.get_daily_problem))
    application.add_handler(CommandHandler("topic", daily.get_problem_by_topic))
    
    # Contest reminder handlers
    application.add_handler(CommandHandler("contests", reminder.show_contests))
    application.add_handler(CommandHandler("subscribe", reminder.subscribe))
    application.add_handler(CommandHandler("unsubscribe", reminder.unsubscribe))
    
    # Duel handlers
    application.add_handler(CommandHandler("duel", duel.challenge_user))
    application.add_handler(CommandHandler("accept", duel.accept_duel))
    application.add_handler(CommandHandler("decline", duel.decline_duel))
    application.add_handler(CommandHandler("duelstatus", duel.duel_status))
    
    # Practice tracker handlers
    application.add_handler(CommandHandler("sethandle", tracker.set_handle))
    application.add_handler(CommandHandler("streak", tracker.show_streak))
    application.add_handler(CommandHandler("report", tracker.weekly_report))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting CP Master Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
