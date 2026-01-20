import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PollHandler,
    filters,
)
from config import TELEGRAM_BOT_TOKEN
from database import (
    get_or_create_user,
    get_distinct_subjects,
    get_available_grades_for_subject,
    get_available_units_for_grade,
    get_quiz_questions,
    update_user_stats,
)
import json

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation
SUBJECT, GRADE, UNIT, QUIZ = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for a subject."""
    user = get_or_create_user(update.message.from_user)
    context.user_data["telegram_id"] = user['telegram_id']
    logger.info(f"User {user['username']} started a conversation.")

    subjects = get_distinct_subjects()
    reply_keyboard = [subjects]

    await update.message.reply_text(
        "Hi! I am the Ethiopian Educational Quiz Bot. "
        "Let's start a quiz. Please choose a subject.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return SUBJECT

async def subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected subject and asks for a grade."""
    user_response = update.message.text
    context.user_data["subject"] = user_response

    grades = get_available_grades_for_subject(user_response)
    reply_keyboard = [grades]

    await update.message.reply_text(
        f"Great! You chose {user_response}. Now, please select a grade.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return GRADE

async def grade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected grade and asks for a unit."""
    user_response = update.message.text
    context.user_data["grade"] = user_response

    subject = context.user_data["subject"]
    units = get_available_units_for_grade(subject, user_response)
    reply_keyboard = [units]

    await update.message.reply_text(
        f"You've selected Grade {user_response}. Now, choose a unit.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return UNIT

async def unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the unit and starts the quiz."""
    context.user_data["unit"] = update.message.text
    context.user_data["chat_id"] = update.message.chat_id

    await update.message.reply_text("Let's start the quiz!", reply_markup=ReplyKeyboardRemove())

    # Fetch questions
    questions = get_quiz_questions(
        context.user_data["subject"],
        context.user_data["grade"],
        context.user_data["unit"],
    )

    if not questions:
        await update.message.reply_text("Sorry, I couldn't find any questions for your selection. Please try again.")
        return ConversationHandler.END

    context.user_data["questions"] = [dict(q) for q in questions]
    context.user_data["current_question"] = 0
    context.user_data["score"] = 0

    return await ask_question(context)


async def ask_question(context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends the current question to the user."""
    questions = context.user_data["questions"]
    current_question_index = context.user_data["current_question"]
    chat_id = context.user_data["chat_id"]

    if current_question_index >= len(questions):
        telegram_id = context.user_data["telegram_id"]
        return await end_quiz(context, telegram_id)

    question = questions[current_question_index]
    options = json.loads(question['options'])

    await context.bot.send_message(chat_id, question['question_text'])

    # Send the poll
    await context.bot.send_poll(
        chat_id,
        "Choose the correct answer:",
        options,
        is_anonymous=False,
        type="quiz",
        correct_option_id=ord(question['correct_answer'].upper()) - ord('A')
    )

    return QUIZ


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's answer to a quiz question."""

    correct_option = update.poll.correct_option_id
    selected_option = -1
    for i, option in enumerate(update.poll.options):
        if option.voter_count > 0:
            selected_option = i
            break

    if selected_option == correct_option:
        context.user_data["score"] += 1

    context.user_data["current_question"] += 1
    return await ask_question(context)

async def end_quiz(context: ContextTypes.DEFAULT_TYPE, telegram_id: int) -> int:
    """Ends the quiz, shows the score, and updates user stats."""
    score = context.user_data["score"]
    total_questions = len(context.user_data["questions"])
    chat_id = context.user_data["chat_id"]

    # Update user stats in the database
    update_user_stats(telegram_id, score, total_questions)

    await context.bot.send_message(
        chat_id,
        f"Quiz finished! Your score is {score}/{total_questions}."
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Quiz cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    if TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN':
        logger.warning("Telegram bot token is not set. The bot will not run.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, subject)],
            GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, grade)],
            UNIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, unit)],
            QUIZ: [PollHandler(handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    print("Telegram bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
