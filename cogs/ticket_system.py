import discord
from discord.ext import commands
from models.ticket_models import TicketManager
from utils.config_handler import ConfigHandler
from utils.logger import TicketLogger

class TicketSystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_manager = TicketManager()
        self.config = ConfigHandler()
        self.logger = TicketLogger(bot)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Инициализация при запуске бота"""
        print(f"✅ Бот {self.bot.user} готов к работе!")
        print(f"📊 Загружено серверов: {len(self.bot.guilds)}")
        
        # Устанавливаем статус бота
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="тикеты"
            ),
            status=discord.Status.online
        )
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Обработка входа на новый сервер"""
        # Автоматически создаем настройки для нового сервера
        self.config.get_guild_settings(guild.id)
        
        # Отправляем приветственное сообщение
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="🎫 Ticket Bot",
                    description="Спасибо за добавление бота!\n\n"
                               "Для настройки используйте команду `/setup`\n"
                               "Для создания панели тикетов используйте `/ticket_panel`\n\n"
                               "**Не забудьте настроить:**\n"
                               "1. Категорию для тикетов\n"
                               "2. Канал для логов\n"
                               "3. Канал для публикации отзывов\n"
                               "4. Роль админа",
                    color=discord.Color.green()
                )
                
                try:
                    await channel.send(embed=embed)
                except:
                    continue
                break
        
        await self.logger.log_action(
            guild,
            "Бот добавлен",
            f"Бот добавлен на сервер {guild.name}",
            channel=None,
            target=guild
        )
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Обработка сообщений в тикетах"""
        # Игнорируем сообщения ботов
        if message.author.bot:
            return
        
        # Проверяем, находится ли сообщение в тикете
        ticket = self.ticket_manager.get_ticket(message.channel.id)
        if ticket:
            # Добавляем сообщение в историю тикета
            ticket.add_message(
                message.author.id,
                message.content,
                message.created_at
            )

async def setup(bot):
    await bot.add_cog(TicketSystemCog(bot))