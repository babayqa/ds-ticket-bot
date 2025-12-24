import discord
from discord.ext import commands
from discord import app_commands
from utils.config_handler import ConfigHandler
from views.setup_views import SetupView

class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigHandler()
    
    @app_commands.command(name="setup", description="Настройка системы тикетов")
    @app_commands.default_permissions(administrator=True)
    async def setup_command(self, interaction: discord.Interaction):
        """Команда для настройки системы тикетов"""
        embed = discord.Embed(
            title="⚙️ Настройка системы тикетов",
            description="Используйте кнопки ниже для настройки системы.\n\n"
                       "**Необходимые настройки:**\n"
                       "1. Основные настройки (категории, каналы, роль)\n"
                       "2. Настройка интерфейса (тексты, цвета)\n"
                       "3. Создание панели тикетов\n\n"
                       "**Как получить ID:**\n"
                       "1. Включите режим разработчика (Настройки → Дополнительно)\n"
                       "2. ПКМ по элементу → Копировать ID",
            color=discord.Color.blue()
        )
        
        embed.set_footer(text="Настройте сначала основные параметры, затем интерфейс")
        
        await interaction.response.send_message(
            embed=embed,
            view=SetupView(self.config),
            ephemeral=True
        )
    
    @app_commands.command(name="ticket_panel", description="Создать панель для создания тикетов")
    @app_commands.default_permissions(administrator=True)
    async def ticket_panel_command(self, interaction: discord.Interaction):
        """Создание панели тикетов"""
        settings = self.config.get_guild_settings(interaction.guild.id)
        
        embed = discord.Embed(
            title=settings.get("ticket_title", "Оставьте свой отзыв"),
            description=settings.get("ticket_subtitle", "С вами мы становимся лучше"),
            color=discord.Color.from_str(settings.get("embed_color", "#3498db"))
        )
        
        embed.set_footer(text="Нажмите кнопку ниже, чтобы создать тикет")
        
        # Импорт здесь чтобы избежать циклического импорта
        from views.ticket_views import CreateTicketView
        from models.ticket_models import TicketManager
        
        ticket_manager = TicketManager()
        view = CreateTicketView(self.config, ticket_manager)
        
        # Обновляем текст кнопки
        for child in view.children:
            if child.custom_id == "create_ticket_button":
                child.label = settings.get("button_label", "Оставить отзыв")
        
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(SetupCog(bot))