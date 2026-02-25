# 🚀 Quick Start Guide

Get your CP Master Bot up and running in 5 minutes!

## Step 1: Get Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Setup Project

### On Windows:
```cmd
setup.bat
```

### On Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
pip install -r requirements.txt
cp .env.example .env
```

## Step 3: Configure Bot Token

Edit the `.env` file and replace `your_bot_token_here` with your actual token:

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

## Step 4: Run the Bot

### On Windows:
```cmd
run.bat
```

### On Linux/Mac:
```bash
chmod +x run.sh
./run.sh
```

Or manually:
```bash
python bot.py
```

## Step 5: Test Your Bot

1. Open Telegram
2. Search for your bot (by username you created)
3. Send `/start` command
4. You should see the welcome message!

## 🎯 Your First Commands

Try these commands to test your bot:

### Set Your Handle
```
/cf tourist
```

### Get a Problem
```
/daily 1400
```

### View Contests
```
/contests
```

### Challenge a Friend (in groups)
```
/duel @friend 1400
```

## 🔥 Pro Tips

1. **Add to Group**: Add your bot to a group chat to enable duel system
2. **Set Handle**: Use `/cf <handle>` to link your Codeforces profile
3. **Daily Practice**: Use `/daily` every day for practice problems
4. **Streak Tracking**: Use `/sethandle` and `/streak` to track progress
5. **Subscribe**: Use `/subscribe` in groups for contest reminders

## ⚠️ Troubleshooting

### Bot doesn't start
- Check if BOT_TOKEN is correct in .env file
- Make sure all dependencies are installed
- Check Python version (need 3.9+)

### Commands don't work
- Make sure you're using the correct syntax
- Check if bot has permission to send messages
- Try `/help` to see available commands

### API errors
- Codeforces API might be down temporarily
- Check your internet connection
- Handle might not exist - verify spelling

## 📚 What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Explore all available commands with `/help`
- Join a group and start dueling with friends!
- Track your progress with `/streak` and `/report`

## 🤝 Need Help?

- Check the [README.md](README.md) for detailed information
- Open an issue on GitHub
- Make sure you followed all steps correctly

---

**Happy Coding! 🏆**
