import json
import os
import time

from config import NUKE_STATS_FILE, PREMIUM_FILE


def save_nuke_stats(user_id, guild):
    try:
        with open(NUKE_STATS_FILE, "r") as f:
            stats = json.load(f)
    except FileNotFoundError:
        stats = {"users": {}, "servers": {}}

    stats.setdefault("users", {})
    stats.setdefault("servers", {})

    user_id = str(user_id)
    guild_id = str(guild.id)

    if user_id not in stats["users"]:
        stats["users"][user_id] = {"uses": 1}
    else:
        stats["users"][user_id]["uses"] += 1

    if guild_id not in stats["servers"]:
        stats["servers"][guild_id] = {
            "user_id": user_id,
            "member_count": guild.member_count,
            "server_name": guild.name
        }

    with open(NUKE_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


def load_premium_users():
    if not os.path.exists(PREMIUM_FILE):
        return []
    with open(PREMIUM_FILE, "r") as f:
        return json.load(f)


def save_premium_users(user_ids):
    os.makedirs(os.path.dirname(PREMIUM_FILE), exist_ok=True)
    with open(PREMIUM_FILE, "w") as f:
        json.dump(user_ids, f, indent=2)


def is_premium_user(user_id: int):
    premium_users = load_premium_users()
    return user_id in premium_users


def load_config():
    if not os.path.exists("config.json"):
        return {}
    with open("config.json", "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)


def get_user_config(user_id):
    config = load_config()
    return config.get(str(user_id), {})


def set_user_config(user_id, key, value):
    config = load_config()
    user_str = str(user_id)
    if user_str not in config:
        config[user_str] = {}
    config[user_str][key] = value
    save_config(config)


def get_show_username(user_id):
    return get_user_config(user_id).get("show_username", True)


def set_show_username(user_id, value: bool):
    set_user_config(user_id, "show_username", value)


def get_channel_name(user_id):
    return get_user_config(user_id).get("channel_name", "zne-on-top")


def set_channel_name(user_id, value: str):
    set_user_config(user_id, "channel_name", value)


def get_webhook_name(user_id):
    return get_user_config(user_id).get("webhook_name", "zne")


def set_webhook_name(user_id, value: str):
    set_user_config(user_id, "webhook_name", value)


def get_webhook_message(user_id):
    return get_user_config(user_id).get("webhook_message", "zne owns this")


def set_webhook_message(user_id, value: str):
    set_user_config(user_id, "webhook_message", value)


def get_server_name(user_id):
    return get_user_config(user_id).get("server_name", "zne owns this")


def set_server_name(user_id, value: str):
    set_user_config(user_id, "server_name", value)


def get_role_name(user_id):
    return get_user_config(user_id).get("role_name", "join zne")


def set_role_name(user_id, value: str):
    set_user_config(user_id, "role_name", value)


class CooldownManager:
    def __init__(self, cooldown_seconds: int):
        self.cooldown_seconds = cooldown_seconds
        self.user_timestamps = {}

    def can_use(self, user_id: int) -> (bool, int):
        now = time.time()
        last_time = self.user_timestamps.get(user_id, 0)
        elapsed = now - last_time
        if elapsed >= self.cooldown_seconds:
            self.user_timestamps[user_id] = now
            self.cleanup()
            return True, 0
        else:
            return False, int(self.cooldown_seconds - elapsed)

    def cleanup(self):
        now = time.time()
        to_delete = [user for user, ts in self.user_timestamps.items() if now - ts > self.cooldown_seconds]
        for user in to_delete:
            del self.user_timestamps[user]


cooldown_manager = CooldownManager(100)
