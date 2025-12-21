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
DEVICE = os.environ.get("DEVICE")
KERNEL_VERSION = os.environ.get("KERNEL_VERSION", "")

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
    
    print(f"[+] Device from env: {DEVICE}")
    print(f"[+] Kernel Version: {KERNEL_VERSION}")

def extract_features_from_filename(filename):
    """从文件名中提取特性信息"""
    features = []
    feature_mapping = {
        '_KSU': "KernelSU",
        '_BetterNet': "BetterNet",
        '_BBG': "Baseband Guard",
        '_LZ4KD': "LZ4KD",
        '_LZ4': "LZ4",
        '_HymoFS': "HymoFS",
    }
    
    for keyword, feature_name in feature_mapping.items():
        if keyword in filename:
            features.append(feature_name)
    
    return features

def generate_caption(filename, features):
    """生成包含 Linux 版本信息的消息"""
    # 构建特性列表字符串
    if features:
        features_text = "\n".join([f"✓ {feature}" for feature in features])
    else:
        features_text = "No additional features"
    
    # 设备标签格式
    device_tag = DEVICE.lower().replace(" ", "")
    
    # 使用提取的内核版本号
    version_display = KERNEL_VERSION
    
    # 生成消息
    caption = f"""
**New Build Published!**
#oki
#{device_tag}

**Device:** {DEVICE}
**Kernel:** {version_display}
**File:** `{filename}`

**Enabled Features:**
{features_text}
""".strip()
    
    # 如果消息太长，截断
    if len(caption) > 1024:
        caption = f"""
**New Build Published!**
#{device_tag}

**Device:** {DEVICE}
**Kernel:** {version_display}
**File:** `{filename}`
**Features:** {', '.join(features) if features else 'Standard'}
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
        # 为每个文件生成消息
        captions = []
        for file in files:
            filename = os.path.basename(file)
            features = extract_features_from_filename(filename)
            caption = generate_caption(filename, features)
            captions.append(caption)
        
        # 只给最后一个文件附加完整消息
        final_captions = [""] * len(files)
        final_captions[-1] = captions[-1]
        
        print("[+] Caption for last file: ")
        print("---")
        print(final_captions[-1])
        print("---")
        print(f"[+] Features detected: {extract_features_from_filename(os.path.basename(files[-1]))}")
        
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