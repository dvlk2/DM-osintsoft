import requests
import os
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

os.system('cls' if os.name == 'nt' else 'clear')

print("\033[95m" + r"""
    ██████╗ ███╗   ███╗
    ██╔══██╗████╗ ████║
    ██║  ██║██╔████╔██║
    ██║  ██║██║╚██╔╝██║
    ██████╔╝██║ ╚═╝ ██║
    ╚═════╝ ╚═╝     ╚═╝
""" + "\033[0m")
print("\033[96m" + "═" * 60 + "\033[0m")
print("\033[93m" + "       DM AVATAR COMPARE — поиск по аватаркам" + "\033[0m")
print("\033[96m" + "═" * 60 + "\033[0m\n")

username = input("\033[92m┌─[ Введите ник]\n└──> \033[0m").strip()

if not username:
    print("\033[91m[!] Пусто\033[0m")
    exit()

# ========== ПЛОЩАДКИ ==========
sites = {
    "VK": "https://vk.com/{}",
    "OK": "https://ok.ru/profile/{}",
    "Mail.ru": "https://my.mail.ru/{}",
    "Rutube": "https://rutube.ru/u/{}/",
    "Yappy": "https://yappy.ru/profile/{}",
    "Zen": "https://zen.yandex.ru/{}",
    "Pikabu": "https://pikabu.ru/@{}",
    "Drive2": "https://www.drive2.ru/users/{}/",
    "4pda": "https://4pda.to/forum/index.php?showuser={}",
    "Habr": "https://habr.com/ru/users/{}/",
    "StopGame": "https://stopgame.ru/users/profile/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Twitch": "https://twitch.tv/{}",
    "Pinterest": "https://pinterest.com/{}",
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "CodePen": "https://codepen.io/{}",
    "Medium": "https://medium.com/@{}",
    "Pastebin": "https://pastebin.com/u/{}",
    "Imgur": "https://imgur.com/user/{}",
    "Behance": "https://www.behance.net/{}",
    "Dribbble": "https://dribbble.com/{}",
    "DeviantArt": "https://www.deviantart.com/{}",
    "Spotify": "https://open.spotify.com/user/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Chess.com": "https://www.chess.com/member/{}"
}

def get_avatar_url(site_name, page_url):
    """Пытается найти прямую ссылку на аватарку со страницы"""
    try:
        r = requests.get(page_url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None
        
        # Паттерны для разных сайтов
        patterns = [
            r'(https?://[^"\']+\.(jpg|png|jpeg|webp|svg))',
            r'(https?://sun[0-9]+[^"\']+\.(jpg|png|jpeg|webp))',
            r'(https?://[^"\']+avatars[^"\']+\.(jpg|png|jpeg|webp))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, r.text, re.I)
            if match:
                return match.group(1)
    except:
        pass
    return None

def download_avatar(url):
    """Скачивает аватарку и возвращает MD5 хеш"""
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            return hashlib.md5(r.content).hexdigest()
    except:
        pass
    return None

print(f"\n\033[96m[>] Цель: {username}\033[0m")
print(f"[>] Сканирую {len(sites)} площадок...\n")

# ========== СБОР ПРОФИЛЕЙ И АВАТАРОК ==========
profiles = []  # (site_name, url, avatar_hash)

def process_site(site_name, url_pattern):
    url = url_pattern.format(username)
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            avatar_url = get_avatar_url(site_name, url)
            avatar_hash = None
            if avatar_url:
                avatar_hash = download_avatar(avatar_url)
            return (site_name, url, avatar_hash)
    except:
        pass
    return None

with ThreadPoolExecutor(max_workers=15) as executor:
    futures = {executor.submit(process_site, name, url): name for name, url in sites.items()}
    
    for future in as_completed(futures):
        res = future.result()
        if res:
            profiles.append(res)
            name, url, hash_val = res
            if hash_val:
                print(f"\033[92m[✓] {name:<12} -> аватарка найдена\033[0m")
            else:
                print(f"\033[93m[?] {name:<12} -> профиль есть, аватарку не скачал\033[0m")

print("\n")

# ========== ГРУППИРОВКА ПО АВАТАРКАМ ==========
same_avatars = {}  # hash -> [(site_name, url)]
no_avatar = []     # где нет аватарки

for site_name, url, avatar_hash in profiles:
    if avatar_hash:
        if avatar_hash not in same_avatars:
            same_avatars[avatar_hash] = []
        same_avatars[avatar_hash].append((site_name, url))
    else:
        no_avatar.append((site_name, url))

# Отделяем где аватарки одинаковые (больше 1) от уникальных
duplicate_groups = {h: sites_list for h, sites_list in same_avatars.items() if len(sites_list) > 1}
unique_avatars = {h: sites_list for h, sites_list in same_avatars.items() if len(sites_list) == 1}

# ========== ВЫВОД ==========
print("\033[96m" + "═" * 60 + "\033[0m")
print("\033[93m[🔄] ГДЕ АВАТАРКИ ОДИНАКОВЫЕ (скорее всего, один человек)\033[0m")
print("\033[96m" + "═" * 60 + "\033[0m\n")

if duplicate_groups:
    for hash_val, sites_list in duplicate_groups.items():
        print(f"\033[92m┌─ Группа с одинаковой аватаркой:\033[0m")
        for site_name, url in sites_list:
            print(f"\033[92m│  • {site_name}: {url}\033[0m")
        print(f"\033[92m└─\033[0m\n")
else:
    print("\033[90m  Нет совпадений\033[0m\n")

print("\033[96m" + "═" * 60 + "\033[0m")
print("\033[93m[🆕] ГДЕ АВАТАРКИ РАЗНЫЕ (уникальные)\033[0m")
print("\033[96m" + "═" * 60 + "\033[0m\n")

if unique_avatars:
    for hash_val, sites_list in unique_avatars.items():
        for site_name, url in sites_list:
            print(f"\033[90m  • {site_name}: {url}\033[0m")
else:
    print("\033[90m  Нет\033[0m")

print("\n\033[96m" + "═" * 60 + "\033[0m")
print("\033[93m[❌] ГДЕ НЕТ АВАТАРКИ (не удалось скачать)\033[0m")
print("\033[96m" + "═" * 60 + "\033[0m\n")

if no_avatar:
    for site_name, url in no_avatar:
        print(f"\033[90m  • {site_name}: {url}\033[0m")
else:
    print("\033[90m  Нет\033[0m")

# ========== СОХРАНЕНИЕ ==========
with open(f"{username}_dm_compare.txt", "w", encoding="utf-8") as f:
    f.write(f"DM AVATAR COMPARE — {username}\n")
    f.write("═" * 50 + "\n\n")
    
    f.write("[ОДИНАКОВЫЕ АВАТАРКИ]\n")
    for hash_val, sites_list in duplicate_groups.items():
        f.write(f"  Группа ({hash_val[:8]}...):\n")
        for site_name, url in sites_list:
            f.write(f"    - {site_name}: {url}\n")
        f.write("\n")
    
    f.write("\n[УНИКАЛЬНЫЕ АВАТАРКИ]\n")
    for hash_val, sites_list in unique_avatars.items():
        for site_name, url in sites_list:
            f.write(f"  - {site_name}: {url}\n")
    
    f.write("\n[НЕТ АВАТАРКИ]\n")
    for site_name, url in no_avatar:
        f.write(f"  - {site_name}: {url}\n")

print(f"\n\033[92m[✓] Отчёт сохранён: {username}_dm_compare.txt\033[0m")
print("\n\033[96m" + "═" * 60 + "\033[0m")
print("\033[92m[+] Готово.\033[0m")