import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import json
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Файл для хранения данных пользователей
DATA_FILE = 'user_data.json'

# Загрузка данных из файла
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Сохранение данных в файл
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать! Используйте /mine для добычи $GOLD\n"
        "Команда доступна раз в час!"
    )

# Команда /mine
async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or update.effective_user.first_name
    
    # Загружаем данные
    data = load_data()
    
    # Инициализируем данные пользователя если их нет
    if user_id not in data:
        data[user_id] = {
            'balance': 0,
            'last_mine': None,
            'username': username
        }
    
    user_data = data[user_id]
    now = datetime.now()
    
    # Проверяем, когда была последняя добыча
    if user_data['last_mine']:
        last_mine = datetime.fromisoformat(user_data['last_mine'])
        time_diff = now - last_mine
        
        # Если не прошёл час
        if time_diff < timedelta(hours=1):
            wait_time = timedelta(hours=1) - time_diff
            minutes = int(wait_time.total_seconds() // 60)
            seconds = int(wait_time.total_seconds() % 60)
            
            await update.message.reply_text(
                f"⏳ Следующая добыча будет доступна через {minutes} минут {seconds} секунд!"
            )
            return
    
    # Начисляем 1000 $GOLD
    user_data['balance'] += 1000
    user_data['last_mine'] = now.isoformat()
    user_data['username'] = username
    
    # Сохраняем данные
    save_data(data)
    
    await update.message.reply_text(
        f"✅ {username}, вы успешно добыли 1000 $GOLD!\n"
        f"💰 Ваш текущий баланс: {user_data['balance']} $GOLD"
    )

# Команда /balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    
    if user_id in data:
        balance = data[user_id]['balance']
        await update.message.reply_text(f"💰 Ваш баланс: {balance} $GOLD")
    else:
        await update.message.reply_text("У вас ещё нет $GOLD. Используйте /mine чтобы начать!")

# Команда /top (топ пользователей)
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    
    if not data:
        await update.message.reply_text("Пока нет данных о пользователях.")
        return
    
    # Сортируем пользователей по балансу
    sorted_users = sorted(
        data.items(),
        key=lambda x: x[1]['balance'],
        reverse=True
    )[:10]  # Топ-10
    
    message = "🏆 Топ 10 пользователей по балансу:\n\n"
    for i, (user_id, user_data) in enumerate(sorted_users, 1):
        username = user_data.get('username', 'Без имени')
        balance = user_data['balance']
        message += f"{i}. {username}: {balance} $GOLD\n"
    
    await update.message.reply_text(message)

# Основная функция
def main():
    # Токен вашего бота (замените на свой)
    TOKEN = "8555836186:AAHhkR0xh9LNdAyGxQORHV41ZgPo0oFvgGM"
    
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mine", mine))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("top", top))
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()  # Убрали allowed_updates

if __name__ == '__main__':
    main()
