import datetime
import telebot
from telebot import types
from db.tables import users, tasks, con

bot = telebot.TeleBot("7116715789:AAGkxwnNd5QG0uO5rOjkIafqmPwrIyEK6Gc")

def generate_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/register")
    markup.add(btn1)

    return markup

@bot.message_handler(commands=['start'])
def start_command(mess):
    bot.send_message(mess.chat.id, "Привет, я помогу вам с управлением вашим списком дел!", reply_markup=generate_keyboard())

@bot.message_handler(commands=['register'])
def start_register(mess):
    user = mess.from_user.id
    bot.send_message(user, "Введите ваше имя:")
    ins = users.insert().values(
        tgid=user
    )
    con.execute(ins)
    con.commit()
    bot.register_next_step_handler(mess, get_name)

def get_name(mess):
    user = mess.from_user.id
    name = mess.text.strip()
    bot.send_message(user, f"Привет, {name}! Введите вашу фамилию:")
    ins = users.update().where(users.c.tgid == user).values(
        name=name
    )
    con.execute(ins)
    con.commit()
    bot.register_next_step_handler(mess, get_surname)


def get_surname(mess):
    user = mess.from_user.id
    surname = mess.text.strip()
    ins = users.update().where(users.c.tgid == user).values(
        surname=surname
    )
    con.execute(ins)
    con.commit()
    bot.send_message(user, f"Введите возраст:")
    bot.register_next_step_handler(mess, get_age)

def get_age(mess):
    user = mess.from_user.id
    age = int(mess.text.strip())
    ins = users.update().where(users.c.tgid == user).values(
        age=age
    )
    con.execute(ins)
    con.commit()
    bot.send_message(user, "Введите вашу почту:")
    bot.register_next_step_handler(mess, get_email)


def get_email(mess):
    user = mess.from_user.id
    email = mess.text.strip() # TODO: проверка на корректность
    ins = users.update().where(users.c.tgid == user).values(
        email=email
    )
    con.execute(ins)
    con.commit()
    bot.send_message(user, "Регистрация завершена!")


@bot.message_handler(commands=['add_task'])
def start_add_task(mess):
    user = mess.from_user.id
    bot.send_message(user, "Введите название задачи:")
    bot.register_next_step_handler(mess, get_task_title)

def get_task_title(mess):
    user = mess.from_user.id
    title = mess.text.strip()
    bot.send_message(user, f"Привет! Введите описание задачи:")
    ins = tasks.insert().values(
        tgid=user,
        title=title,
    )
    con.execute(ins)
    con.commit()
    ins_id = tasks.select().where((tasks.c.tgid == user) & (tasks.c.title == title))
    task_id = con.execute(ins_id).fetchall()[-1][0]
    bot.register_next_step_handler(mess, get_task_description, task_id)

def get_task_description(mess, id):
    user = mess.from_user.id
    description = mess.text.strip()
    ins = tasks.update().where(tasks.c.id == id).values(
        description=description,
    )
    con.execute(ins)
    con.commit()
    bot.send_message(user, "Задача добавлена!")


@bot.message_handler(commands=["all_tasks"])
def all_tasks(mess):
    user = mess.from_user.id
    ins = tasks.select().where(tasks.c.tgid == user)
    tasks_list = con.execute(ins).fetchall()
    if not tasks_list:
        bot.send_message(user, "У вас нет созданных задач.")
        return
    mess_from_bot = "Ваш список задач: \n"
    markup = types.InlineKeyboardMarkup()
    for task in tasks_list:
        mess_from_bot += f"ID: {task[0]}, Название: {task[2]}\n"
        btn = types.InlineKeyboardButton(text=f"ID: {task[0]}, {task[2]}", callback_data=f"/task {task[0]}")
        markup.add(btn)
    bot.send_message(user, mess_from_bot, reply_markup=markup)


def generate_keybord_succes():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Выполнено")
    markup.add(btn1)
    btn2 = types.KeyboardButton("Продолжить работу")
    markup.add(btn2)

    return markup


@bot.message_handler(commands=['task'])
def get_task(mess):
    user = mess.from_user.id
    task_id = int(mess.text.strip().split()[1])
    ins = tasks.select().where((tasks.c.tgid == user) & (tasks.c.id == task_id))
    task_data = con.execute(ins).fetchall()
    if not task_data:
        bot.send_message(user, "Такой задачи не существует.")
        return
    task = task_data[-1]
    markup = generate_keybord_succes()
    bot.send_message(user, f"ID: {task[0]}, Название: {task[2]} \nОписание: {task[3]} \n Статус: {task[4]}", reply_markup=markup)
    bot.register_next_step_handler(mess, succes_task, task)

def succes_task(mess, task):
    if mess.text == "Выполнено":
        ins = tasks.update().where(tasks.c.id == task[0]).values(
            status=True
        )
        con.execute(ins)
        con.commit()
        bot.send_message("Задаче присвоен статус Выполнено")
    else:
        bot.send_message("Хорошо, продолжим работу", reply_markup=generate_keyboard())


bot.polling(non_stop=True)
