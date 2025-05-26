import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Токен и API ключ
TOKEN = '7304006066:AAEfuzsNvAoLHM_1OV0UsZGPBh5QAKBQ-kc'
API_SECRET_KEY = 'supersecrettoken123'  # Ваш API ключ

# Настроим логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SurveyBot:
    def __init__(self):
        self.survey_data = {}  # ключ: chat_id, значение: {question_id: question_text}
        self.current_question = {}  # Словарь для текущего вопроса
        self.answers = {}  # Словарь с ответами
        self.survey_ids = {}  # Словарь с ID опросов

    def get_survey_from_server(self, survey_id):
        headers = {
            'X-API-KEY': API_SECRET_KEY
        }

        url = f'https://telegrambot-teamproject.onrender.com/api/survey/?id={survey_id}'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    async def start(self, update: Update, context):
        await update.message.reply_text("Введите ID опроса, чтобы начать.")

    async def handle_answer(self, update: Update, context):

        chat_id = update.effective_chat.id
        user_input = update.message.text.strip()

        if chat_id not in self.survey_ids:
            self.survey_ids[chat_id] = user_input
            survey_data = self.get_survey_from_server(user_input)

            if survey_data:
                self.current_question[chat_id] = 0
                self.answers[chat_id] = []
                self.survey_data[chat_id] = {}

                for question in survey_data['questions']:
                    self.survey_data[chat_id][question['id']] = question['text']

                await update.message.reply_text('Начинаем опрос!')

                await self.ask_question(update, chat_id)
            else:
                await update.message.reply_text("Опрос не найден.")
        else:
            # Обработка ответа на текущий вопрос
            question_number = self.current_question[chat_id]
            answer = update.message.text  # Получаем ответ от пользователя

            self.answers[chat_id].append({
                'question_id': list(self.survey_data[chat_id].keys())[question_number],
                'answer': answer
            })

            self.current_question[chat_id] += 1
            await self.ask_question(update, chat_id)

    async def ask_question(self, update: Update, chat_id):
        survey_data = self.get_survey_from_server(self.survey_ids[chat_id])

        total_questions = len(survey_data['questions'])

        if self.current_question[chat_id] >= total_questions:
            await self.finish_survey(update, chat_id)
            return

        question = survey_data['questions'][self.current_question[chat_id]]

        text = question['text']
        options = [opt['text'] for opt in question['options']]

        keyboard = [[option] for option in options]
        reply_markup = {'keyboard': keyboard, 'one_time_keyboard': True}
        logger.info(f"Отправляем вопрос: {question['id']} - {text}")

        await update.message.reply_text(text, reply_markup=reply_markup)

    async def finish_survey(self, update: Update, chat_id):

        await update.message.reply_text('Спасибо за участие в опросе!')
        self.send_all_answers_to_server(chat_id)  # Отправка всех ответов на сервер

        del self.current_question[chat_id]
        del self.answers[chat_id]
        del self.survey_ids[chat_id]
        del self.survey_data[chat_id]

    def send_all_answers_to_server(self, chat_id):
        answers = self.answers[chat_id]

        if not answers:
            logger.warning(f"Ответов для пользователя {chat_id} нет.")
            return
        data = {
            'user_info': {
                'user_id': chat_id,
                'full_name': 'Имя Фамилия'  #
            },
            'answers': answers
        }

        logger.info(f"Отправляем все данные: {data}")

        headers = {
            'X-API-KEY': API_SECRET_KEY
        }

        response = requests.post('http://telegrambot-teamproject.onrender.com/api/answers/', json=data, headers=headers)

        if response.status_code == 200:
            logger.info("Все ответы успешно отправлены на сервер.")
        else:
            logger.error(f"Ошибка при отправке данных: {response.status_code}, {response.text}")

def main():

    bot = SurveyBot()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_answer))
    application.run_polling()

if __name__ == '__main__':
    main()
