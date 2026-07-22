import os
from dotenv import load_dotenv
from typing import Final

from database.base import Base, engine
from database import models

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from services.initialize_context import initialize_context
from services.add_shopping import add_shopping_item
from services.list_shopping import list_shopping_items
from services.remove_shopping import remove_shopping_items
from services.add_reminder import add_reminder
from services.reminder_worker import delete_reminder, get_due_reminders, get_group_id
from services.list_reminder import list_reminders
from services.remove_reminder import remove_reminder
from services.add_categories import add_categories
from services.list_categories import list_categories
from services.remove_categories import remove_categories

print('Bot is now starting...')

load_dotenv()

API_KEY: Final = os.getenv("API_KEY")
BOT_HANDLE: Final = os.getenv("BOT_HANDLE")

def list_to_comma_separated(string_list):
    if len(string_list) > 2:
        result = f"{', '.join(string_list[:-1])}, and {string_list[-1]}"
    elif len(string_list) == 2:
        result = " and ".join(string_list)
    else:
        result = string_list[0] if string_list else ""

    return result


async def shopping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, group = initialize_context(update.effective_user, update.effective_chat)

    if not context.args:
        await update.message.reply_text("Commands: add list or remove \nExample: /shopping add Milk")
        return

    text = update.message.text

    try:
        if not user.is_allowed:
            await update.message.reply_text("BAWAL KA. PA-APPROVE KA MUNA KAY BOSSING")
            return

        command_input = context.args

        match command_input:
            case ['add', *item]:
                if len(context.args) < 2:
                    await update.message.reply_text("Please add an item. Example: /shopping add Milk")
                    return

                items = text.removeprefix("/shopping add").strip()

                to_add = [item.strip().lower() for item in items.split(",")]

                existing_items, add_items, item_exists = add_shopping_item(user, group, to_add)
                if item_exists and not add_items:
                    await update.message.reply_text(f"{list_to_comma_separated(existing_items)} already exists. Please add other items.")
                    return
                if not item_exists and not existing_items:
                    await update.message.reply_text(f"Done adding {list_to_comma_separated(add_items)}.")
                    return
                await update.message.reply_text(f"Done adding {list_to_comma_separated(add_items)}. {list_to_comma_separated(existing_items)} already exists")
                return
            case ['list']:
                shopping_items, items_exists = list_shopping_items(user, group)
                if items_exists:
                    shopping_list = []
                    for items in shopping_items:
                        shopping_list.append(items.name)
                    all_shopping_items = "\n".join(shopping_list)
                    await update.message.reply_text(f"Here is your shopping list:\n{all_shopping_items}")
                    return
                await update.message.reply_text("wala naman laman list mo hahah. Lagay ka muna /shopping add item_name")
                return
            case ['remove', *_]:
                if len(context.args) < 2:
                    await update.message.reply_text("Please add item/s to remove. \nExample: /shopping add Milk")
                    return

                items = text.removeprefix("/shopping remove").strip()

                to_delete = [item.strip() for item in items.split(",")]

                shopping_items, items_exists = remove_shopping_items(user, group, to_delete)

                if items_exists:
                    sorted_items = "\n".join(shopping_items)
                    await update.message.reply_text(f"You will be deleting:\n{sorted_items}")
                    return

                await update.message.reply_text("nothing to delete")
                return
            case _:
                await update.message.reply_text("Unknown command")

    except ValueError:
        await update.message.reply_text("Error occured")

async def add_reminder_command(update, context, user, group, reminder):
    reminder_time, message, item_exists = add_reminder(user, group, reminder)

    if item_exists:
        await update.message.reply_text(f"Reminder to {message} already set at {reminder_time}")
        return
    if reminder_time is None:
        await update.message.reply_text(f"I couldn't understand the reminder time. Please try a different format")
        return
    await update.message.reply_text(f"Creating a reminder to {message}: {reminder_time}")
    return


async def reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, group = initialize_context(update.effective_user, update.effective_chat)

    if not context.args:
        await update.message.reply_text("Commands: add list or remove \nExample: /reminder Change Password next month")
        return

    text_message = update.message.text.splitlines()
    text = update.message.text
    try:
        if not user.is_allowed:
            await update.message.reply_text("paapprove ka muna")
            return
        command = text_message[0].split()

        match command[1:]:
            case ["list"]:
                reminders, item_exists = list_reminders(user, group)
                if item_exists:
                    reminder_list  = []
                    for items in reminders:
                        reminder_list.append(items.text)
                    all_reminders = "\n".join(reminder_list)
                    await update.message.reply_text(f"All reminders:\n\n{all_reminders}")
                    return
                await update.message.reply_text("wala naman laman list mo hahah. Lagay ka muna\n\n/reminder\nReminder name\nReminder time")
                return
            case ["remove", *_]:
                if len(context.args) < 2:
                    await update.message.reply_text("Please add item/s to remove. \nExample: /reminder remove Change Password")
                    return
                items = text.removeprefix("/reminder remove").strip()
                to_delete = [item.strip() for item in items.split(",")]
                print(f"remove command sa function {to_delete}")

                reminders, items_exists = remove_reminder(group, to_delete)

                if items_exists:
                    sorted_items = "\n".join(reminders)
                    await update.message.reply_text(f"You will be deleting:\n{sorted_items}")
                    return

                await update.message.reply_text("nothing to delete")
                return
            case []:
                reminder = text_message[1:]
                if len(reminder) < 2:
                    await update.message.reply_text(
                        "Usage:\n\n"
                        "/reminder\n"
                        "Reminder message\n"
                        "Reminder time\n"
                        "/reminder list"
                        "/reminder remove <name>"
                    )
                await add_reminder_command(update, context, user, group, text_message)
#            case _:
#               await update.message.reply_text(
#                    "Usage:\n\n"
#                    "/reminder\n"
#                    "Reminder message\n"
#                    "Reminder time\n"
#                    "/reminder list"
#                    "/reminder remove <name>"
#                )

    except ValueError:
        await update.message.reply_text("Error occured")

async def category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, group = initialize_context(update.effective_user, update.effective_chat)

    if not context.args:
        await update.message.reply_text("Commands: add list or remove \nExample: /shopping add Milk")
        return

    text = update.message.text

    try:
        if not user.is_allowed:
            await update.message.reply_text("BAWAL KA. PA-APPROVE KA MUNA KAY BOSSING")
            return

        command_input = context.args

        match command_input:
            case ['add', *item]:
                if len(context.args) < 2:
                    await update.message.reply_text("Please add an item. Example: /category add Baguio Trip")
                    return

                items = text.removeprefix("/category add").strip()

                to_add = [item.strip().lower() for item in items.split(",")]

                existing_items, add_items, item_exists = add_categories(user, group, to_add)
                if item_exists and not add_items:
                    await update.message.reply_text(f"{list_to_comma_separated(existing_items)} already exists. Please add other items.")
                    return
                if not item_exists and not existing_items:
                    await update.message.reply_text(f"Done adding {list_to_comma_separated(add_items)}.")
                    return
                await update.message.reply_text(f"Done adding {list_to_comma_separated(add_items)}. {list_to_comma_separated(existing_items)} already exists")
                return
            case ['list']:
                category_items, items_exists = list_categories(user, group)
                if items_exists:
                    category_list = []
                    for items in category_items:
                        category_list.append(items.name)
                    all_category_items = "\n".join(category_list)
                    await update.message.reply_text(f"Here is your category list:\n{all_category_items}")
                    return
                await update.message.reply_text("wala naman laman list mo hahah. Lagay ka muna /category add category_name")
                return
            case ['remove', *_]:
                if len(context.args) < 2:
                    await update.message.reply_text("Please add item/s to remove. \nExample: /category remove Baguio Trip")
                    return

                items = text.removeprefix("/category remove").strip()

                to_delete = [item.strip() for item in items.split(",")]

                category_items, items_exists = remove_categories(user, group, to_delete)

                if items_exists:
                    sorted_items = "\n".join(category_items)
                    await update.message.reply_text(f"You will be deleting:\n{sorted_items}")
                    return

                await update.message.reply_text("nothing to delete")
                return
            case _:
                await update.message.reply_text("Unknown command")

    except ValueError:
        await update.message.reply_text("Error occured")


async def reminder_service(context: ContextTypes.DEFAULT_TYPE):
    reminders = get_due_reminders()

    try:
        for reminder in reminders:
            group_id = get_group_id(reminder.group_id)
            await context.bot.send_message(chat_id=group_id,text=f"Reminder: {reminder.text}")
            delete_reminder(reminder.id)
    except ValueError:
        await update.message.reply_text("Error occured")

async def personalize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("personalize command")

async def fund_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("fund command")

# Log errors
async def log_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Start the bot
if __name__ == '__main__':

    Base.metadata.create_all(bind=engine)

    app = Application.builder().token(API_KEY).build()

    # Register command handlers
    app.add_handler(CommandHandler('shopping', shopping_command))
    app.add_handler(CommandHandler('reminder', reminder_command))
    app.add_handler(CommandHandler('category', category_command))

    app.job_queue.run_repeating(reminder_service, interval=60,first=0)

    # Register error handler
    app.add_error_handler(log_error)

    print('Starting polling...')
    # Run the bot
    app.run_polling(poll_interval=2)
