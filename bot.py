import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

bible_versions = {
    'R1933': 'bibleFI/FinPR.json',
    'FB92': 'bibleFI/FinPR92.json',
    'ESV': 'bibleEN/ESV.json'
}

apocryphal_books = {
    "Tobit", "Judith", "Baruch", "Sirach", "Ecclesiasticus",
    "1 Maccabees", "2 Maccabees", "Wisdom"
}

non_deuterocanonical_versions = {"FB92", "ESV"}

# Load Bible data once and create a hashmap for faster lookup
bible_data_cache = {}
for version, path in bible_versions.items():
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        book_lookup = {}
        for book in data['books']:
            chapters = {c['chapter']: {v['verse']: v['text'] for v in c['verses']} for c in book['chapters']}
            book_lookup[book['name'].lower()] = chapters
        bible_data_cache[version] = book_lookup

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if ':' in message.content:
        try:
            words = message.content.split()
            for i in range(len(words) - 1):
                if ':' in words[i + 1]:
                    for j in range(i + 1):
                        potential_book = " ".join(words[j:i + 1]).lower()
                        reference = words[i + 1]
                        bible_version = 'R1933'

                        if words[-1].lower() in bible_versions:
                            bible_version = words[-1].upper()
                            words = words[:-1]

                        if bible_version in non_deuterocanonical_versions and potential_book in apocryphal_books:
                            await message.reply("Tämä käännös ei tue apokryfikirjoja")
                            return

                        chapter_str, verse_range = reference.split(':')
                        chapter = int(chapter_str)
                        
                        start_verse, end_verse = (map(int, verse_range.split('-'))
                                                  if '-' in verse_range else (int(verse_range), int(verse_range)))

                        # Quick lookup using preloaded hashmap
                        book_data = bible_data_cache[bible_version].get(potential_book)
                        if book_data:
                            chapter_data = book_data.get(chapter)
                            if chapter_data:
                                verses_text = [f"**<{v}>** {chapter_data[v]}" for v in range(start_verse, end_verse + 1) if v in chapter_data]
                                if verses_text:
                                    await message.reply(f"{potential_book.title()} {chapter}:{start_verse}-{end_verse} ({bible_version})\n\n>>> " + " ".join(verses_text))
                                    return
        except Exception as e:
            print(f"Error processing message: {e}")

    await bot.process_commands(message)

TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: BOT_TOKEN environment variable not set.")
