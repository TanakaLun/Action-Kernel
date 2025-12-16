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
TYPR = os.environ.get("TYPR", "GKI Kernel")
KERNEL_VERSION = os.environ.get("KERNEL_VERSION", "")
BUILD_INFO = os.environ.get("BUILD_INFO", "")
SUB_LEVEL = os.environ.get("SUB_LEVEL", "")
OS_PATCH_LEVEL = os.environ.get("OS_PATCH_LEVEL", "")
ZIP_NAME = os.environ.get("ZIP_NAME", "")

# 构建特性
BETTER_NET = os.environ.get("BETTER_NET", "false")
BASEBAND_GUARD = os.environ.get("BASEBAND_GUARD", "false")
LZ4KD = os.environ.get("LZ4KD", "false")
USE_O2 = os.environ.get("USE_O2", "false")

def check_environ():
    global CHAT_ID, MESSAGE_THREAD_ID, TYPR
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
    
    print(f"[+] TYPR: {TYPR}")
    print(f"[+] Kernel Version: {KERNEL_VERSION}")
    print(f"[+] Build Info: {BUILD_INFO}")

def get_features_from_env():
    """从环境变量中获取特性信息"""
    features = []
    
    if BETTER_NET.lower() == "true":
        features.append("Network Optimizations")
    if BASEBAND_GUARD.lower() == "true":
        features.append("Baseband Guard")
    if LZ4KD.lower() == "true":
        features.append("LZ4KD Compression")
    if USE_O2.lower() == "true":
        features.append("O2 Optimization")
    
    return features

def extract_features_from_filename(filename):
    """从文件名中提取特性信息（备用方法）"""
    features = []
    feature_mapping = {
        '_NET': "Network Optimizations",
        '_BBG': "Baseband Guard",
        '_LZ4KD': "LZ4KD Compression",
        '_O2': "O2 Optimization",
        '_STOCK': "Stock Configuration",
    }
    
    for keyword, feature_name in feature_mapping.items():
        if keyword in filename:
            features.append(feature_name)
    
    return features

def generate_caption(filename, features):
    """生成包含构建信息的消息"""
    # 设备标签格式
    type_tag = TYPR.lower().replace(" ", "")
    
    # 构建消息
    caption = f"""
🚀 **New GKI Kernel Build Available!**
#gki #kernel #{type_tag}

📱 **TYPR:** {TYPR}
🔢 **Android:** 12
⚙️ **Kernel:** {KERNEL_VERSION}
📊 **Version:** 5.10.{SUB_LEVEL} ({OS_PATCH_LEVEL})
📦 **File:** `{filename}`

🔧 **Build Information:**
{BUILD_INFO}

✅ **Enabled Features:**
{chr(10).join([f'• {feature}' for feature in features]) if features else '• Stock configuration'}

⚠️ **Note:** This is a GKI (Generic Kernel Image) kernel. Flash at your own risk!
""".strip()
    
    return caption

async def main():
    print("[+] Uploading to Telegram")
    check_environ()
    files = sys.argv[1:]
    print("[+] Files to upload:", files)
    
    if len(files) <= 0:
        print("[-] No files to upload")
        exit(1)
    
    print("[+] Logging in to Telegram with bot")
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    session_dir = os.path.join(script_dir, "telegram_bot")
    
    async with await TelegramClient(session=session_dir, api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN) as bot:
        # 为每个文件生成消息
        captions = []
        for file in files:
            filename = os.path.basename(file)
            # 优先从环境变量获取特性，其次从文件名提取
            features = get_features_from_env()
            if not features:
                features = extract_features_from_filename(filename)
            caption = generate_caption(filename, features)
            captions.append(caption)
        
        # 只给最后一个文件附加完整消息
        final_captions = [""] * len(files)
        final_captions[-1] = captions[-1]
        
        print("[+] Caption for last file:")
        print("---")
        print(final_captions[-1])
        print("---")
        print(f"[+] Features: {get_features_from_env()}")
        
        print("[+] Sending files to Telegram...")
        await bot.send_file(
            entity=CHAT_ID, 
            file=files, 
            caption=final_captions, 
            reply_to=MESSAGE_THREAD_ID, 
            parse_mode="markdown"
        )
        print("[+] Upload completed successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[-] An error occurred: {e}")
        import traceback
        traceback.print_exc()
        exit(1)