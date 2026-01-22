import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
from dotenv import load_dotenv

from game_logic import (
    Symbol,
    get_default_state,
    check_winner_from_board,
    make_ai_move,
)

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


TOKEN = os.getenv('TG_TOKEN')

# Состояния игры для ConversationHandler
CONTINUE_GAME, FINISH_GAME = range(2)

# Тип для игрового поля
BoardType = list[list[str]]


def generate_keyboard(state: BoardType) -> list[list[InlineKeyboardButton]]:
    """
    Генерация клавиатуры 3x3 для Telegram.
    Каждая кнопка содержит текущий символ ячейки.
    """
    return [
        [
            InlineKeyboardButton(state[r][c], callback_data=f'{r}{c}')
            for c in range(3)
        ]
        for r in range(3)
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик команды /start.
    Инициализирует новую игру с пустым полем.
    """
    context.user_data['keyboard_state'] = get_default_state()
    keyboard = generate_keyboard(context.user_data['keyboard_state'])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Игра в крестики-нолики!\n'
        'Вы играете за X. Ваш ход!',
        reply_markup=reply_markup
    )
    return CONTINUE_GAME


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Основная логика игры.
    Обрабатывает нажатие игрока и ход ИИ.
    """
    query = update.callback_query
    await query.answer()

    # Получаем координаты из callback_data
    data = query.data
    row, col = int(data[0]), int(data[1])

    board = context.user_data['keyboard_state']

    # Проверяем, свободна ли ячейка
    if board[row][col] != Symbol.FREE.value:
        await query.answer('Эта клетка уже занята!', show_alert=True)
        return CONTINUE_GAME

    # Ход игрока (крестик)
    board[row][col] = Symbol.CROSS.value

    # Проверка победы игрока
    result = check_winner_from_board(board)
    if result.is_finished:
        return await handle_game_end(query, board, result)

    # Ход ИИ (нолик)
    ai_move = make_ai_move(board)

    # Проверка победы ИИ или ничьей
    if ai_move:
        result = check_winner_from_board(board)
        if result.is_finished:
            return await handle_game_end(query, board, result)

    # Игра продолжается — обновляем клавиатуру
    keyboard = generate_keyboard(board)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        '🎮 Ваш ход! Поставьте X на свободное место.',
        reply_markup=reply_markup
    )

    return CONTINUE_GAME


async def handle_game_end(query, board: list[list[str]], result) -> int:
    """
    Обработка завершения игры.
    Показывает результат и предлагает сыграть снова.
    """
    keyboard = generate_keyboard(board)
    reply_markup = InlineKeyboardMarkup(keyboard)

    if result.is_draw:
        message = 'Ничья! Нажмите любую кнопку для завершения.'
    elif result.winner == Symbol.CROSS:
        message = 'Поздравляем! Вы победили! Нажмите кнопку.'
    else:
        message = 'Бот победил! Попробуйте ещё раз.'

    await query.edit_message_text(message, reply_markup=reply_markup)
    return FINISH_GAME


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Завершение игры.
    Сбрасывает состояние и предлагает начать новую игру.
    """
    query = update.callback_query
    await query.answer()

    # Сброс состояния
    context.user_data['keyboard_state'] = get_default_state()

    await query.edit_message_text(
        'Игра завершена! Для новой игры введите /start'
    )

    return ConversationHandler.END


def main() -> None:
    """Запуск бота"""
    if not TOKEN:
        logger.error("Токен бота не найден! Установите TG_TOKEN в .env файле.")
        return

    # Создание приложения
    application = Application.builder().token(TOKEN).build()

    # Настройка обработчика состояний
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONTINUE_GAME: [
                CallbackQueryHandler(game, pattern=f'^{r}{c}$')
                for r in range(3)
                for c in range(3)
            ],
            FINISH_GAME: [
                CallbackQueryHandler(end, pattern=f'^{r}{c}$')
                for r in range(3)
                for c in range(3)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)

    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
