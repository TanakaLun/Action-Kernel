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
KSU_TYPE = os.environ.get("KSU_TYPE", "").lower()
BETTER_NET = os.environ.get("BETTER_NET", "").lower() == "true"
BASEBAND_GUARD = os.environ.get("BASEBAND_GUARD", "").lower() == "true"
LZ4KD = os.environ.get("LZ4KD", "").lower() == "true"
ADIOS = os.environ.get("ADIOS", "").lower() == "true"
BBR = os.environ.get("BBR", "").lower() == "true"
KPM = os.environ.get("KPM", "").lower() == "true"
SUSFS = os.environ.get("SUSFS", "").lower() == "true"
MOUNT_TYPE = os.environ.get("MOUNT_TYPE", "").lower()

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
    print(f"[+] Features from env:")
    print(f"    KSU_TYPE: {KSU_TYPE}")
    print(f"    BetterNet: {BETTER_NET}")
    print(f"    Baseband Guard: {BASEBAND_GUARD}")
    print(f"    LZ4KD: {LZ4KD}")
    print(f"    ADIOS: {ADIOS}")
    print(f"    BBR: {BBR}")
    print(f"    KPM: {KPM}")
    print(f"    SUSFS: {SUSFS}")
    print(f"    MOUNT_TYPE: {MOUNT_TYPE}")

def get_features_from_env():
    """从环境变量获取特性信息"""
    features = []
    
    if KSU_TYPE != "none":
        features.append(f"KernelSU ({KSU_TYPE.capitalize()})")
        
    if BETTER_NET:
        features.append("BetterNet")
    
    if BASEBAND_GUARD:
        features.append("Baseband Guard")
    
    if LZ4KD:
        features.append("LZ4KD")
    
    if ADIOS:
        features.append("ADIOS")
    
    if BBR:
        features.append("BBR")

    if KPM:
        features.append("KPM")
    
    if SUSFS:
        features.append("SUSFS")
      
    if MOUNT_TYPE != "Default":
        features.append(f"Mounting scheme ({MOUNT_TYPE.capitalize()})")
    
    return features

def generate_caption(filename, features):
    """生成包含 Linux 版本信息的消息"""
    if features:
        features_text = "\n".join([f"{feature} ✓" for feature in features])
    else:
        features_text = "No additional features"
    
    device_tag = DEVICE.lower().replace(" ", "")
    
    version_display = KERNEL_VERSION
    
    caption = f"""
**New Build Published!**
#oki
#{device_tag}

**Device:** {DEVICE}
**Kernel:** 
```{version_display}
```

**Enabled Features:** 
```{features_text}
```
""".strip()

    if len(caption) > 1024:
        caption = f"""
**New Build Published!**
#{device_tag}

**Device:** {DEVICE}
**Kernel:** {version_display}
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