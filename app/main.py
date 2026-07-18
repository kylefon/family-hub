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

async def assist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Help')

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
    #app.add_handler(CommandHandler('help', assist_command))
    #app.add_handler(CommandHandler('custom', personalize_command))

    # Register error handler
    app.add_error_handler(log_error)

    print('Starting polling...')
    # Run the bot
    app.run_polling(poll_interval=2)
