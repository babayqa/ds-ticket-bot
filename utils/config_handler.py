import json
import os
from pathlib import Path

class ConfigHandler:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.guild_settings_path = self.data_dir / "guild_settings.json"
        self.config_path = Path("config.json")
        
        self.load_config()
        self.load_guild_settings()
    
    def load_config(self):
        """Загрузка конфигурации по умолчанию"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # Конфигурация по умолчанию
            self.config = {
                "default_settings": {
                    "ticket_category_id": None,
                    "closed_category_id": None,
                    "log_channel_id": None,
                    "publish_channel_id": None,
                    "admin_role_name": "Admin",
                    "embed_color": "#3498db",
                    "ticket_title": "Оставьте свой отзыв",
                    "ticket_subtitle": "С вами мы становимся лучше",
                    "button_label": "Оставить отзыв",
                    "button_color": "primary",
                    "ticket_message": "📝 Пожалуйста, напишите ваш отзыв в этот канал.\n\nАдминистрация рассмотрит его в ближайшее время.",
                    "welcome_message": "🎫 Добро пожаловать в тикет поддержки! Опишите вашу проблему или оставьте отзыв."
                }
            }
            self.save_config()
    
    def load_guild_settings(self):
        """Загрузка настроек серверов"""
        if self.guild_settings_path.exists():
            with open(self.guild_settings_path, 'r', encoding='utf-8') as f:
                self.guild_settings = json.load(f)
        else:
            self.guild_settings = {}
            self.save_guild_settings()
    
    def get_guild_settings(self, guild_id):
        """Получение настроек для сервера"""
        guild_id = str(guild_id)
        if guild_id not in self.guild_settings:
            self.guild_settings[guild_id] = self.config["default_settings"].copy()
            self.save_guild_settings()
        return self.guild_settings[guild_id]
    
    def update_guild_settings(self, guild_id, **kwargs):
        """Обновление настроек сервера"""
        guild_id = str(guild_id)
        if guild_id not in self.guild_settings:
            self.guild_settings[guild_id] = self.config["default_settings"].copy()
        
        self.guild_settings[guild_id].update(kwargs)
        self.save_guild_settings()
        return self.guild_settings[guild_id]
    
    def save_config(self):
        """Сохранение конфигурации"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def save_guild_settings(self):
        """Сохранение настроек серверов"""
        with open(self.guild_settings_path, 'w', encoding='utf-8') as f:
            json.dump(self.guild_settings, f, indent=4, ensure_ascii=False)