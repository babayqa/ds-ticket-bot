from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Ticket:
    """Модель тикета"""
    channel_id: int
    creator_id: int
    guild_id: int
    created_at: datetime
    closed_at: Optional[datetime] = None
    status: str = "open"  # open, closed, published
    messages: list = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
    
    def add_message(self, author_id: int, content: str, timestamp: datetime):
        """Добавление сообщения в историю тикета"""
        self.messages.append({
            "author_id": author_id,
            "content": content,
            "timestamp": timestamp.isoformat()
        })
    
    def close(self):
        """Закрытие тикета"""
        self.status = "closed"
        self.closed_at = datetime.now()
    
    def publish(self):
        """Публикация тикета"""
        self.status = "published"
        self.closed_at = datetime.now()

class TicketManager:
    """Менеджер для работы с тикетами"""
    def __init__(self):
        self.active_tickets = {}  # channel_id -> Ticket
    
    def create_ticket(self, channel_id: int, creator_id: int, guild_id: int) -> Ticket:
        """Создание нового тикета"""
        ticket = Ticket(
            channel_id=channel_id,
            creator_id=creator_id,
            guild_id=guild_id,
            created_at=datetime.now()
        )
        self.active_tickets[channel_id] = ticket
        return ticket
    
    def get_ticket(self, channel_id: int) -> Optional[Ticket]:
        """Получение тикета по ID канала"""
        return self.active_tickets.get(channel_id)
    
    def close_ticket(self, channel_id: int):
        """Закрытие тикета"""
        ticket = self.get_ticket(channel_id)
        if ticket:
            ticket.close()
            # Можно сохранить в базу данных здесь
            # self.save_to_database(ticket)
    
    def user_has_active_ticket(self, user_id: int, guild_id: int) -> bool:
        """Проверка, есть ли у пользователя активный тикет"""
        for ticket in self.active_tickets.values():
            if ticket.creator_id == user_id and ticket.guild_id == guild_id and ticket.status == "open":
                return True
        return False