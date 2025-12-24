import discord
from discord import ui
import asyncio
from utils.config_handler import ConfigHandler
from models.ticket_models import TicketManager

class CreateTicketView(ui.View):
    """View для создания тикета"""
    def __init__(self, config_handler, ticket_manager):
        super().__init__(timeout=None)
        self.config = config_handler
        self.ticket_manager = ticket_manager
    
    @ui.button(label="Оставить отзыв", style=discord.ButtonStyle.primary, custom_id="create_ticket_button", emoji="📝")
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # Проверка на наличие активного тикета
        if self.ticket_manager.user_has_active_ticket(interaction.user.id, interaction.guild.id):
            await interaction.response.send_message(
                "❌ У вас уже есть активный тикет! Дождитесь его закрытия.",
                ephemeral=True
            )
            return
        
        # Получение настроек сервера
        settings = self.config.get_guild_settings(interaction.guild.id)
        
        # Создание канала тикета
        category_id = settings.get("ticket_category_id")
        category = None
        if category_id:
            category = discord.utils.get(interaction.guild.categories, id=int(category_id))
        
        # Настройка прав доступа
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_messages=True,
                attach_files=True
            )
        }
        
        # Добавление прав для админов
        admin_role_name = settings.get("admin_role_name", "Admin")
        admin_role = discord.utils.get(interaction.guild.roles, name=admin_role_name)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_messages=True,
                manage_messages=True,
                manage_channels=True,
                attach_files=True
            )
        
        # Создание канала
        channel_name = f"отзыв-{interaction.user.name[:15]}"
        try:
            ticket_channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=f"Отзыв от {interaction.user.name} | ID: {interaction.user.id}"
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ошибка при создании тикета: {e}",
                ephemeral=True
            )
            return
        
        # Создание записи о тикете
        ticket = self.ticket_manager.create_ticket(
            ticket_channel.id,
            interaction.user.id,
            interaction.guild.id
        )
        
        # Отправка приветственного сообщения
        embed_color = discord.Color.from_str(settings.get("embed_color", "#3498db"))
        embed = discord.Embed(
            title="📝 Тикет отзыва",
            description=settings.get("ticket_message", "Пожалуйста, напишите ваш отзыв здесь."),
            color=embed_color
        )
        embed.add_field(name="👤 Автор", value=interaction.user.mention, inline=True)
        embed.add_field(name="📅 Создан", value=discord.utils.format_dt(interaction.created_at, 'R'), inline=True)
        embed.set_footer(text="Администрация ответит вам в ближайшее время")
        
        # View для управления тикетом (виден только админам)
        control_view = TicketControlView(self.config, self.ticket_manager, ticket.creator_id)
        
        await ticket_channel.send(
            content=f"{interaction.user.mention}, {settings.get('welcome_message', 'добро пожаловать!')}",
            embed=embed,
            view=control_view
        )
        
        await interaction.response.send_message(
            f"✅ Тикет создан: {ticket_channel.mention}",
            ephemeral=True
        )
        
        # Логирование
        from utils.logger import TicketLogger
        logger = TicketLogger(interaction.client)
        await logger.log_action(
            interaction.guild,
            "Тикет создан",
            f"Тикет создан пользователем {interaction.user.name}",
            user=interaction.user,
            channel=ticket_channel
        )

class TicketControlView(ui.View):
    """View для управления тикетом (только для админов)"""
    def __init__(self, config_handler, ticket_manager, creator_id):
        super().__init__(timeout=None)
        self.config = config_handler
        self.ticket_manager = ticket_manager
        self.creator_id = creator_id
    
    @ui.button(label="✅ Опубликовать", style=discord.ButtonStyle.success, custom_id="publish_ticket", emoji="📢")
    async def publish_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # Проверка прав (админ или создатель тикета)
        if not await self._check_admin_permissions(interaction):
            return
        
        # Получение истории сообщений
        ticket = self.ticket_manager.get_ticket(interaction.channel.id)
        if not ticket:
            await interaction.response.send_message("❌ Тикет не найден!", ephemeral=True)
            return
        
        # Получение всех сообщений от создателя
        creator_messages = []
        async for message in interaction.channel.history(limit=200, oldest_first=True):
            if message.author.id == self.creator_id and message.content and not message.author.bot:
                creator_messages.append(message.content)
        
        if not creator_messages:
            await interaction.response.send_message("❌ Не найдено сообщений для публикации!", ephemeral=True)
            return
        
        # Получение настроек
        settings = self.config.get_guild_settings(interaction.guild.id)
        publish_channel_id = settings.get("publish_channel_id")
        
        if not publish_channel_id:
            await interaction.response.send_message("❌ Канал для публикации не настроен!", ephemeral=True)
            return
        
        publish_channel = interaction.guild.get_channel(int(publish_channel_id))
        if not publish_channel:
            await interaction.response.send_message("❌ Канал для публикации не найден!", ephemeral=True)
            return
        
        # Получение информации о создателе
        creator = await interaction.guild.fetch_member(self.creator_id)
        
        # Создание embed для публикации
        embed_color = discord.Color.from_str(settings.get("embed_color", "#3498db"))
        publish_embed = discord.Embed(
            title="📢 Новый отзыв",
            description="\n\n".join(creator_messages),
            color=embed_color,
            timestamp=interaction.created_at
        )
        
        if creator:
            publish_embed.set_author(
                name=f"Отзыв от {creator.display_name}",
                icon_url=creator.avatar.url if creator.avatar else None
            )
        
        publish_embed.set_footer(text="Спасибо за ваш отзыв!")
        
        # Публикация отзыва
        try:
            await publish_channel.send(embed=publish_embed)
            
            # Обновление статуса тикета
            ticket.publish()
            
            await interaction.response.send_message("✅ Отзыв опубликован! Тикет будет закрыт через 5 секунд...")
            
            # Логирование
            from utils.logger import TicketLogger
            logger = TicketLogger(interaction.client)
            await logger.log_action(
                interaction.guild,
                "Отзыв опубликован",
                f"Отзыв опубликован в {publish_channel.mention}",
                user=interaction.user,
                channel=interaction.channel,
                target=creator
            )
            
            # Закрытие тикета через 5 секунд
            await asyncio.sleep(5)
            await self._close_ticket(interaction.channel)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Ошибка при публикации: {e}", ephemeral=True)
    
    @ui.button(label="❌ Закрыть", style=discord.ButtonStyle.danger, custom_id="close_ticket", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # Проверка прав
        if not await self._check_admin_permissions(interaction):
            return
        
        await interaction.response.send_message("🔒 Тикет будет закрыт через 3 секунды...")
        
        # Логирование
        from utils.logger import TicketLogger
        logger = TicketLogger(interaction.client)
        await logger.log_action(
            interaction.guild,
            "Тикет закрыт",
            "Тикет закрыт без публикации",
            user=interaction.user,
            channel=interaction.channel
        )
        
        await asyncio.sleep(3)
        await self._close_ticket(interaction.channel)
    
    async def _check_admin_permissions(self, interaction: discord.Interaction) -> bool:
        """Проверка прав пользователя"""
        settings = self.config.get_guild_settings(interaction.guild.id)
        admin_role_name = settings.get("admin_role_name", "Admin")
        admin_role = discord.utils.get(interaction.guild.roles, name=admin_role_name)
        
        has_permission = (
            interaction.user.guild_permissions.administrator or
            (admin_role and admin_role in interaction.user.roles)
        )
        
        if not has_permission:
            await interaction.response.send_message(
                "❌ У вас нет прав для управления тикетами!",
                ephemeral=True
            )
            return False
        
        return True
    
    async def _close_ticket(self, channel):
        """Закрытие тикета"""
        ticket = self.ticket_manager.get_ticket(channel.id)
        if ticket:
            ticket.close()
        
        # Перемещение в категорию закрытых тикетов (если настроена)
        settings = self.config.get_guild_settings(channel.guild.id)
        closed_category_id = settings.get("closed_category_id")
        
        if closed_category_id:
            closed_category = discord.utils.get(channel.guild.categories, id=int(closed_category_id))
            if closed_category:
                try:
                    await channel.edit(category=closed_category, name=f"закрыто-{channel.name}")
                    
                    # Удаление прав на отправку сообщений
                    overwrites = channel.overwrites
                    for target, overwrite in overwrites.items():
                        if isinstance(target, discord.Member) and target.id != channel.guild.me.id:
                            overwrite.send_messages = False
                            await channel.set_permissions(target, overwrite=overwrite)
                    
                    await asyncio.sleep(60)  # Даем время для просмотра
                    await channel.delete()
                    
                except:
                    pass
            else:
                await channel.delete()
        else:
            await channel.delete()