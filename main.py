from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue
import datetime,pytz
from SeleniumBot import GiphyBot, parse_html


TOKEN: Final = '6832956980:AAH_SZt8geqWswqvmP4anlBsvpiZUuNsAp4'
BOT_USERNAME: Final = '@view_tracker_giffy_bot'


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me! I am a banana!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    template = '''1> /setup : Sets the tracker for giphy\n2> /rem : Delets the tracker for giphy'''
    await update.message.reply_text(template)

async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    print(chat_id)
    id = context.args[0]
    #context.job_queue.run_repeating(alarm, 20, chat_id=chat_id, name=str(id),data=id)
    context.job_queue.run_daily(alarm,
                                datetime.time(hour=19, minute=46, tzinfo=pytz.timezone('Asia/Kolkata')),
                                days=(0, 1, 2, 3, 4, 5, 6),  name=str(id),data=id,chat_id=chat_id)

    
    await update.message.reply_text(f"Giphy View Tracker successfully set for {id}!")

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove the job if the user changed their mind."""
    id = context.args[0]
    job_removed = remove_job_if_exists(str(id), context)
    text = "Giphy View Tracker successfully cancelled!" if job_removed else "You have no Giphy View Tracker with id"
    await update.message.reply_text(text)
    


# Responses

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
   
    job = context.job
    id = job.data
    print(id)
   
    message = id + ":\n"
    try:
        Bot = GiphyBot(id)
        html = Bot.target_html()
    except:
        message = message + 'No Giphy with given Id \n'
        await context.bot.send_message(job.chat_id, text=message)
        return
    try:
        views = parse_html(html)
    except:
        message = message + 'Giphy doesnt have views \n'
        await context.bot.send_message(job.chat_id, text=message)
        return
        
    message = message + f"Total Views Today: {views}" + "\n===========\n"

    await context.bot.send_message(job.chat_id, text=message)

def handle_response(text: str) -> str:

    '''
    1> setup : Sets the tracker for giphy
    2> delete : Delets the tracker for giphy

    '''
    return 'I do not understand what you wrote. Use /help to use bot'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}" ')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)



async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('setup', setup_command))
    app.add_handler(CommandHandler('rem', remove_command))
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #app.job_queue.run_repeating(run, 10)

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print("Polling...")
    app.run_polling(poll_interval=3)