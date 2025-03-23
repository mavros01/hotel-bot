import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Твой токен от BotFather (замени его после сброса!)
TOKEN = '7870381505:AAHeEF7oEJvpvc-xEJD4Q4F8111dlxWpfYM'
# Твой Telegram ID
YOUR_ID = 198389894

# Функция для создания кнопок с оценками от 1 до 10
def create_rating_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data='1'),
            InlineKeyboardButton("2", callback_data='2'),
            InlineKeyboardButton("3", callback_data='3'),
            InlineKeyboardButton("4", callback_data='4'),
            InlineKeyboardButton("5", callback_data='5'),
        ],
        [
            InlineKeyboardButton("6", callback_data='6'),
            InlineKeyboardButton("7", callback_data='7'),
            InlineKeyboardButton("8", callback_data='8'),
            InlineKeyboardButton("9", callback_data='9'),
            InlineKeyboardButton("10", callback_data='10'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сбрасываем все данные пользователя, чтобы начать опрос заново
    context.user_data.clear()
    
    # Разнообразим описание
    welcome_message = (
        "🌟 Добро пожаловать в гостиницу Олимп! 🌟\n"
        "Мы очень ценим ваше мнение, скажите, понравилось ли вам у нас.(это займет 1-2 минуты)\n"
        "Давайте начнём с оценки: на сколько вы бы оценили наш отель (от 1 до 10)?\n"
        "Выберите оценку, нажав на кнопку ниже:"
    )
    
    # Сохраняем начальные данные пользователя
    context.user_data['review'] = {}
    context.user_data['step'] = 'rating'  # Текущий шаг: оценка
    
    # Отправляем сообщение с кнопками
    await update.message.reply_text(welcome_message, reply_markup=create_rating_keyboard())

# Обработка нажатий на кнопки (оценка)
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if context.user_data.get('step') == 'rating':
        # Сохраняем оценку
        rating = query.data
        context.user_data['review']['rating'] = rating
        
        # Переходим к следующему вопросу (номер комнаты)
        context.user_data['step'] = 'room_number'
        await query.message.reply_text(
            "Спасибо за вашу оценку! 😊\n"
            "Укажите пожалуйста номер комнаты, в которой вы проживаете:"
        )

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.message.from_user.first_name
    step = context.user_data.get('step')

    if step == 'room_number':
        # Сохраняем номер комнаты
        context.user_data['review']['room_number'] = user_message
        context.user_data['step'] = 'service'
        await update.message.reply_text(
            "Спасибо за ваш ответ! 🙏\n"
            "Теперь расскажите, вам понравилось наше обслуживание? (Напишите пару слов или предложений)"
        )

    elif step == 'service':
        # Сохраняем отзыв об обслуживании
        context.user_data['review']['service'] = user_message
        context.user_data['step'] = 'room'
        await update.message.reply_text(
            "Спасибо за ваш ответ! 🙏\n"
            "А что скажете о вашем номере? Удобно ли вам было?"
        )

    elif step == 'room':
        # Сохраняем отзыв о номере
        context.user_data['review']['room'] = user_message
        context.user_data['step'] = 'comment'
        await update.message.reply_text(
            "Отлично, мы почти закончили! 😊\n"
            "Теперь вы можете оставить дополнительный комментарий, если хотите (или напишите 'нет', чтобы пропустить):"
        )

    elif step == 'comment':
        # Сохраняем комментарий
        comment = user_message if user_message.lower() != 'нет' else "Без комментария"
        context.user_data['review']['comment'] = comment
        
        # Формируем полный отзыв
        review = context.user_data['review']
        full_review = (
            f"Новый отзыв от {user_name}:\n"
            f"Оценка: {review['rating']}/10\n"
            f"Номер комнаты: {review['room_number']}\n"
            f"Обслуживание: {review['service']}\n"
            f"Номер: {review['room']}\n"
            f"Комментарий: {review['comment']}"
        )
        
        # Сохраняем отзыв в файл
        with open('reviews.txt', 'a', encoding='utf-8') as file:
            file.write(f"{full_review}\n{'-'*30}\n")
        
        # Отправляем тебе отзыв
        await context.bot.send_message(
            chat_id=YOUR_ID,
            text=full_review
        )
        
        # Завершаем опрос
        await update.message.reply_text(
            "Спасибо за ваш отзыв! 🌟 Мы очень ценим ваше мнение и будем рады видеть вас снова!\n"
            "Если хотите оставить ещё один отзыв, просто нажмите /start."
        )
        
        # Очищаем данные
        context.user_data.clear()

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
