import discord
from datetime import datetime
from utils.config_handler import ConfigHandler

class TicketLogger:
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigHandler()
    
    async def log_action(self, guild, action_type, details, user=None, channel=None, target=None):
        """Логирование действий с тикетами"""
        settings = self.config.get_guild_settings(guild.id)
        log_channel_id = settings.get("log_channel_id")
        
        if not log_channel_id:
            return
        
        log_channel = guild.get_channel(int(log_channel_id))
        if not log_channel:
            return
        
        # Создание embed для лога
        embed = discord.Embed(
            title=f"📝 {action_type}",
            color=self._get_color(action_type),
            timestamp=datetime.now()
        )
        
        if user:
            embed.add_field(name="👤 Пользователь", value=f"{user.mention} ({user.id})", inline=False)
        
        if channel:
            embed.add_field(name="📁 Канал", value=f"{channel.mention} ({channel.id})", inline=False)
        
        if target:
            embed.add_field(name="🎯 Цель", value=str(target), inline=False)
        
        embed.add_field(name="📋 Детали", value=details, inline=False)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    def _get_color(self, action_type):
        """Получение цвета embed в зависимости от типа действия"""
        colors = {
            "Тикет создан": discord.Color.green(),
            "Тикет закрыт": discord.Color.red(),
            "Отзыв опубликован": discord.Color.blue(),
            "Ошибка": discord.Color.orange(),
            "Настройка": discord.Color.purple()
        }
        return colors.get(action_type, discord.Color.greyple())