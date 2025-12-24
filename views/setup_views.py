import discord
from discord import ui
from utils.config_handler import ConfigHandler

class SetupView(ui.View):
    """Основное меню настройки"""
    def __init__(self, config_handler):
        super().__init__(timeout=None)
        self.config = config_handler
    
    @ui.button(label="🎛️ Основные настройки", style=discord.ButtonStyle.primary, emoji="⚙️")
    async def main_settings(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(MainSettingsModal(self.config, interaction.guild.id))
    
    @ui.button(label="🎨 Настроить интерфейс", style=discord.ButtonStyle.secondary, emoji="🎨")
    async def interface_settings(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(InterfaceSettingsModal(self.config, interaction.guild.id))
    
    @ui.button(label="📊 Показать настройки", style=discord.ButtonStyle.success, emoji="📊")
    async def show_settings(self, interaction: discord.Interaction, button: ui.Button):
        settings = self.config.get_guild_settings(interaction.guild.id)
        
        embed = discord.Embed(
            title="⚙️ Текущие настройки",
            color=discord.Color.from_str(settings.get("embed_color", "#3498db"))
        )
        
        # Основные настройки
        embed.add_field(
            name="🔧 Основные",
            value=f"**Категория тикетов:** {self._format_channel(settings.get('ticket_category_id'), interaction.guild)}\n"
                  f"**Категория закрытых:** {self._format_channel(settings.get('closed_category_id'), interaction.guild)}\n"
                  f"**Канал логов:** {self._format_channel(settings.get('log_channel_id'), interaction.guild)}\n"
                  f"**Канал публикации:** {self._format_channel(settings.get('publish_channel_id'), interaction.guild)}\n"
                  f"**Роль админа:** {settings.get('admin_role_name', 'Admin')}",
            inline=False
        )
        
        # Настройки интерфейса
        embed.add_field(
            name="🎨 Интерфейс",
            value=f"**Заголовок:** {settings.get('ticket_title', 'Оставьте свой отзыв')}\n"
                  f"**Подзаголовок:** {settings.get('ticket_subtitle', 'С вами мы становимся лучше')}\n"
                  f"**Текст кнопки:** {settings.get('button_label', 'Оставить отзыв')}\n"
                  f"**Цвет:** {settings.get('embed_color', '#3498db')}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ui.button(label="📝 Создать панель", style=discord.ButtonStyle.primary, emoji="📝")
    async def create_panel(self, interaction: discord.Interaction, button: ui.Button):
        settings = self.config.get_guild_settings(interaction.guild.id)
        
        embed = discord.Embed(
            title=settings.get("ticket_title", "Оставьте свой отзыв"),
            description=settings.get("ticket_subtitle", "С вами мы становимся лучше"),
            color=discord.Color.from_str(settings.get("embed_color", "#3498db"))
        )
        
        embed.set_footer(text="Нажмите кнопку ниже, чтобы создать тикет")
        
        # Создание View для создания тикетов
        from views.ticket_views import CreateTicketView
        from models.ticket_models import TicketManager
        
        ticket_manager = TicketManager()
        create_view = CreateTicketView(self.config, ticket_manager)
        
        # Обновляем текст кнопки
        for child in create_view.children:
            if child.custom_id == "create_ticket_button":
                child.label = settings.get("button_label", "Оставить отзыв")
        
        await interaction.response.send_message(embed=embed, view=create_view)
    
    def _format_channel(self, channel_id, guild):
        """Форматирование ID канала в упоминание"""
        if not channel_id:
            return "Не настроено"
        return f"<#{channel_id}>"

class MainSettingsModal(ui.Modal, title="Основные настройки"):
    def __init__(self, config_handler, guild_id):
        super().__init__()
        self.config = config_handler
        self.guild_id = guild_id
        
        self.ticket_category = ui.TextInput(
            label="ID категории для тикетов",
            placeholder="123456789012345678",
            required=False,
            max_length=20
        )
        self.add_item(self.ticket_category)
        
        self.closed_category = ui.TextInput(
            label="ID категории для закрытых тикетов",
            placeholder="123456789012345678",
            required=False,
            max_length=20
        )
        self.add_item(self.closed_category)
        
        self.log_channel = ui.TextInput(
            label="ID канала для логов",
            placeholder="123456789012345678",
            required=False,
            max_length=20
        )
        self.add_item(self.log_channel)
        
        self.publish_channel = ui.TextInput(
            label="ID канала для публикации отзывов",
            placeholder="123456789012345678",
            required=False,
            max_length=20
        )
        self.add_item(self.publish_channel)
        
        self.admin_role = ui.TextInput(
            label="Название роли админа",
            placeholder="Admin",
            required=True,
            default="Admin"
        )
        self.add_item(self.admin_role)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Обновление настроек
        updated_settings = {}
        
        if self.ticket_category.value:
            updated_settings["ticket_category_id"] = self.ticket_category.value
        
        if self.closed_category.value:
            updated_settings["closed_category_id"] = self.closed_category.value
        
        if self.log_channel.value:
            updated_settings["log_channel_id"] = self.log_channel.value
        
        if self.publish_channel.value:
            updated_settings["publish_channel_id"] = self.publish_channel.value
        
        updated_settings["admin_role_name"] = self.admin_role.value
        
        self.config.update_guild_settings(self.guild_id, **updated_settings)
        
        await interaction.response.send_message(
            "✅ Основные настройки обновлены!",
            ephemeral=True
        )

class InterfaceSettingsModal(ui.Modal, title="Настройка интерфейса"):
    def __init__(self, config_handler, guild_id):
        super().__init__()
        self.config = config_handler
        self.guild_id = guild_id
        
        current_settings = self.config.get_guild_settings(guild_id)
        
        self.ticket_title = ui.TextInput(
            label="Заголовок тикета",
            placeholder="Оставьте свой отзыв",
            default=current_settings.get("ticket_title", "Оставьте свой отзыв"),
            required=True
        )
        self.add_item(self.ticket_title)
        
        self.ticket_subtitle = ui.TextInput(
            label="Подзаголовок",
            placeholder="С вами мы становимся лучше",
            default=current_settings.get("ticket_subtitle", "С вами мы становимся лучше"),
            required=True
        )
        self.add_item(self.ticket_subtitle)
        
        self.button_label = ui.TextInput(
            label="Текст на кнопке",
            placeholder="Оставить отзыв",
            default=current_settings.get("button_label", "Оставить отзыв"),
            required=True
        )
        self.add_item(self.button_label)
        
        self.embed_color = ui.TextInput(
            label="Цвет embed (HEX)",
            placeholder="#3498db",
            default=current_settings.get("embed_color", "#3498db"),
            required=True
        )
        self.add_item(self.embed_color)
    
    async def on_submit(self, interaction: discord.Interaction):
        updated_settings = {
            "ticket_title": self.ticket_title.value,
            "ticket_subtitle": self.ticket_subtitle.value,
            "button_label": self.button_label.value,
            "embed_color": self.embed_color.value
        }
        
        self.config.update_guild_settings(self.guild_id, **updated_settings)
        
        await interaction.response.send_message(
            "✅ Настройки интерфейса обновлены!",
            ephemeral=True
        )