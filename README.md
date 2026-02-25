# CP Master Bot

🏆 **Your Ultimate Competitive Programming Companion**

A powerful Telegram bot designed for competitive programmers to track ratings, get daily problems, participate in duels, and maintain solving streaks across multiple platforms.

## 🚀 Features

### ✅ Stage 1 (Current) - Core Foundation

- **Rating Tracker**
  - Link Codeforces handle
  - Compare users
  - Group leaderboard
  
- **Daily Problems**
  - Random problems by rating
  - Topic-based problem selection
  - Multi-platform support
  
- **Contest Reminders**
  - Upcoming contests list
  - Automated notifications
  - Platform filtering
  
- **Duel System**
  - Challenge friends
  - Timed competitions
  - Winner tracking
  
- **Practice Tracker**
  - Solving streaks
  - Weekly reports
  - Progress analytics

## 🏗️ Architecture

```
cp_master_bot/
│
├── bot.py                 # Main bot entry point
├── database.py            # Database operations
├── handlers/              # Command handlers
│   ├── rating.py         # Rating & comparison
│   ├── daily.py          # Daily problems
│   ├── duel.py           # Duel system
│   ├── tracker.py        # Practice tracking
│   └── reminder.py       # Contest reminders
│
├── services/              # External API services
│   ├── codeforces_api.py # Codeforces integration
│   ├── atcoder_api.py    # AtCoder integration
│   ├── leetcode_api.py   # LeetCode integration
│   └── problem_selector.py # Smart problem selection
│
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment config
└── .env                  # Environment variables
```

## 📦 Installation

### Prerequisites

- Python 3.9+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Setup Steps

1. **Clone/Download the project**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your bot token:
   ```
   BOT_TOKEN=your_bot_token_here
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## 🎮 Usage

### Basic Commands

**Getting Started**
- `/start` - Welcome message and command list
- `/help` - Detailed help information

**Rating & Profile**
- `/cf <handle>` - Set your Codeforces handle
- `/compare <user1> <user2>` - Compare two users
- `/leaderboard` - Show group rankings

**Daily Problems**
- `/daily` - Get random problem
- `/daily 1400` - Problem with specific rating
- `/topic dp` - Problem from specific topic

**Contest Reminders**
- `/contests` - View upcoming contests
- `/subscribe` - Enable contest notifications
- `/unsubscribe` - Disable notifications

**Duel System** (Groups only)
- `/duel @user 1400` - Challenge someone
- `/accept` - Accept duel invitation
- `/decline` - Decline duel
- `/duelstatus` - Check ongoing duel

**Practice Tracker**
- `/sethandle <handle>` - Link your handle
- `/streak` - Check your solving streak
- `/report` - View weekly progress

## 🌐 Supported Platforms

- ✅ **Codeforces** - Full support
- ✅ **AtCoder** - Basic support
- ✅ **LeetCode** - Basic support

## 🗄️ Database Schema

The bot uses SQLite with the following tables:

- `users` - User profiles and handles
- `chats` - Group/chat settings
- `contests` - Cached contest information
- `duels` - Competitive duel tracking
- `problems` - Cached problem data
- `submissions` - User submission history
- `streaks` - Daily solving streaks
- `daily_problems` - Daily problem assignments

## 🚀 Deployment

### Heroku

1. Create a Heroku app
2. Set environment variables:
   ```bash
   heroku config:set BOT_TOKEN=your_token_here
   ```
3. Deploy:
   ```bash
   git push heroku main
   ```

### VPS/Local Server

1. Use screen or tmux to run in background:
   ```bash
   screen -S cpbot
   python bot.py
   ```
2. Detach with `Ctrl+A, D`

### Docker (Coming Soon)

## 📈 Roadmap

### Stage 2 - Enhanced Rating System
- Rating change notifications
- Historical rating graphs
- Prediction algorithms

### Stage 3 - Advanced Daily Problems
- Personalized recommendations
- Difficulty progression
- Problem of the week

### Stage 4 - Tournament System
- Multi-user tournaments
- Bracket generation
- Prize tracking

### Stage 5 - Analytics Dashboard
- Detailed statistics
- Performance insights
- Comparison analytics

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [Codeforces API](https://codeforces.com/apiHelp)
- [Kenkoooo AtCoder API](https://github.com/kenkoooo/AtCoderProblems)
- [LeetCode GraphQL API](https://leetcode.com/graphql)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact via Telegram: [@your_username]

---

**Made with ❤️ for the CP community**

🏆 Happy Coding! 🚀
