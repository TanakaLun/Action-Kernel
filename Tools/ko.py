import asyncio
import os
import sys
import re
from telethon import TelegramClient

API_ID = 611335
API_HASH = "d524b414d21f4d37f08684c1df41ac9c"

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHATID")
MESSAGE_THREAD_ID = os.environ.get("MESSAGE_THREAD_ID")

def check_environ():
    global CHAT_ID, MESSAGE_THREAD_ID, DEVICE
    if BOT_TOKEN is None:
        print("[-] Invalid BOT_TOKEN")
        exit(1)
    if CHAT_ID is None:
        print("[-] Invalid CHAT_ID")
        exit(1)
    else:
        try:
            CHAT_ID = int(CHAT_ID)
        except:
            pass
    if MESSAGE_THREAD_ID is not None and MESSAGE_THREAD_ID != "":
        try:
            MESSAGE_THREAD_ID = int(MESSAGE_THREAD_ID)
        except:
            print("[-] Invalid MESSAGE_THREAD_ID")
            exit(1)
    else:
        MESSAGE_THREAD_ID = None

def generate_caption(filename, features):
    
    caption = f"""
**New Build Published!**
#IPSET-KO
""".strip()

    if len(caption) > 1024:
        caption = f"""
**New Build Published!**
#IPSET-KO
""".strip()
    
    return caption

async def main():
    print("[+] Uploading to telegram")
    check_environ()
    files = sys.argv[1:]
    print("[+] Files:", files)
    
    if len(files) <= 0:
        print("[-] No files to upload")
        exit(1)
    
    print("[+] Logging in Telegram with bot")
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    session_dir = os.path.join(script_dir, "ksubot")
    
    async with await TelegramClient(session=session_dir, api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN) as bot:
        captions = []
        for file in files:
            filename = os.path.basename(file)
            features = get_features_from_env()
            caption = generate_caption(filename, features)
            captions.append(caption)
        
        final_captions = [""] * len(files)
        final_captions[-1] = captions[-1]
        
        print("[+] Caption for last file: ")
        print("---")
        print(final_captions[-1])
        print("---")
        print(f"[+] Features from env: {get_features_from_env()}")
        
        print("[+] Sending")
        await bot.send_file(
            entity=CHAT_ID, 
            file=files, 
            caption=final_captions, 
            reply_to=MESSAGE_THREAD_ID, 
            parse_mode="markdown"
        )
        print("[+] Done!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[-] An error occurred: {e}")