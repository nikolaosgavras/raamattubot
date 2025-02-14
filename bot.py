import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Ensure the bot can read message content
bot = commands.Bot(command_prefix='!', intents=intents)  # Remove command prefix

# Dictionary to map Bible version codes to their respective JSON file paths
bible_versions = {
    'R1933': 'bibleFI/FinPR.json',
    'FB92': 'bibleFI/FinPR92.json'
}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    print(f'Received message: {message.content} from {message.author}')  # Debug log

    if message.author == bot.user:
        return

    # Check if the message contains a verse reference
    if ':' in message.content:
        try:
            # Split message into words
            words = message.content.split()
            print(f'Split words: {words}')  # Debug log

            # Look for potential verse references in the message
            for i in range(len(words) - 1):
                if ':' in words[i + 1]:  # Check if next word contains chapter:verse
                    # Check for multi-word book names
                    for j in range(i + 1):
                        potential_book = " ".join(words[j:i + 1])
                        reference = words[i + 1]
                        bible_version = 'R1933'  # Default Bible version

                        # Check if the last word is a Bible version code
                        if words[-1].lower() in map(str.lower, bible_versions.keys()):
                            bible_version = next(key for key in bible_versions if key.lower() == words[-1].lower())
                            words = words[:-1]  # Remove the version code from the words list

                        print(f'Potential book: {potential_book}, Reference: {reference}, Bible version: {bible_version}')  # Debug log

                        chapter_str, verse_range = reference.split(':')
                        chapter = int(chapter_str)

                        # Handle verse ranges (e.g., 5-10)
                        if '-' in verse_range:
                            start_verse, end_verse = map(int, verse_range.split('-'))
                        else:
                            start_verse = end_verse = int(verse_range)

                        # Load the appropriate Bible data
                        with open(bible_versions[bible_version], 'r', encoding='utf-8') as f:
                            bible_data = json.load(f)

                        # Search through the Bible data case-insensitively
                        found = False
                        for b in bible_data['books']:
                            if b['name'].lower() == potential_book.lower():
                                for c in b['chapters']:
                                    if c['chapter'] == chapter:
                                        verses_text = []
                                        for v in c['verses']:
                                            if start_verse <= v['verse'] <= end_verse:
                                                verses_text.append(f"**<{v['verse']}>** {v['text']}")
                                        if verses_text:
                                            await message.reply(f"{b['name']} {chapter}:{start_verse}-{end_verse}\n\n>>> " + " ".join(verses_text))
                                            found = True
                                        break
                                if found:
                                    break
                        if found:
                            break
        except Exception as e:
            print(f"Error processing message: {e}")

    await bot.process_commands(message)

TOKEN = os.getenv('BOT_TOKEN')
if TOKEN is None:
    print("Error: BOT_TOKEN environment variable not set.")
else:
    bot.run(TOKEN)