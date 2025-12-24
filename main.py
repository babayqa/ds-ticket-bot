import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("❌ ОШИБКА: Токен не найден в .env файле!")
    print("Создайте файл .env с содержимым: DISCORD_TOKEN=ваш_токен")
    exit()

print(f"✅ Токен получен")

# Настройка интентов
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Создаем бота с tree команд
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Событие при запуске
@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} успешно запущен!')
    print(f'🔗 Пригласительная ссылка: https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8')
    print(f'📊 Серверов: {len(bot.guilds)}')
    
    # Синхронизация команд
    try:
        synced = await bot.tree.sync()
        print(f"✅ Синхронизировано {len(synced)} команд")
        
        # Показать список команд
        print("📋 Доступные команды:")
        for cmd in synced:
            print(f"  /{cmd.name} - {cmd.description}")
    except Exception as e:
        print(f"❌ Ошибка синхронизации команд: {e}")
    
    # Устанавливаем статус
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="тикеты | /setup"
        ),
        status=discord.Status.online
    )

# Загрузка когов
async def load_extensions():
    extensions = ["cogs.ticket_system", "cogs.setup_cog"]
    
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Загружен: {ext}")
        except Exception as e:
            print(f"❌ Ошибка загрузки {ext}: {e}")

# Основная функция
async def main():
    print("🚀 Запуск бота...")
    
    # Загружаем расширения
    await load_extensions()
    
    # Запускаем бота
    try:
        await bot.start(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ Неверный токен! Проверьте .env файл")
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")

# Запуск
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")