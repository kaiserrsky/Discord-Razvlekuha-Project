import asyncio
import discord
import logging
import yt_dlp
from TOKEN import TOKEN, FFMPEG_PATH
from discord.ext import commands
import random

RUSSIAN_NOUNS = open('russian_nouns.txt', encoding='utf-8').read().split('\n')
values = {'start_hangman': False}

FFMPEG_OPTIONS = {"before_options": "-ss 00:00:00", "options": "-vn -t 30"}
YDL_OPTIONS = {"format": "bestaudio", "noplaylist": True}

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="/")


class HangmanReady(discord.ui.View):
    @discord.ui.button(label="Понятно. Приступить к игре", row=0, style=discord.ButtonStyle.green)
    async def ready(self, interaction, button: discord.ui.Button):
        await interaction.response.send_message("Приступаем к игре")
        values['start_hangman'] = True
        self.stop()


class MyView(discord.ui.View):

    @discord.ui.button(label="Opening 1", row=0, style=discord.ButtonStyle.secondary, emoji='1️⃣')
    async def first_button_callback(self, interaction, choice_opening):
        discord.ui.button(label="Opening 1", row=0, style=discord.ButtonStyle.primary, emoji='1️⃣')
        await interaction.response.send_message("Правильно")

    @discord.ui.button(label="Opening 2", row=0, style=discord.ButtonStyle.secondary, emoji='2️⃣')
    async def second_button_callback(self, interaction, choice_opening):
        await interaction.response.send_message("Нет")

    @discord.ui.button(label="Opening 3", row=1, style=discord.ButtonStyle.secondary, emoji='3️⃣')
    async def third_button_callback(self, interaction, choice_opening):
        await interaction.response.send_message("ГОООООООООООООООЛ")

    @discord.ui.button(label="Opening 4", row=1, style=discord.ButtonStyle.secondary, emoji='4️⃣')
    async def fourth_button_callback(self, interaction, choice_opening):
        await interaction.response.send_message("бз бз бз.... я пчела")


class BulletCountChoose(discord.ui.View):
    @discord.ui.button(label="1 bullet", custom_id="1", row=0, style=discord.ButtonStyle.secondary)
    async def first_button_callback(self, interaction, button: discord.ui.Button):
        await interaction.response.send_message("Выбран режим с 1 пулей")
        values['bulletin_counter'] = 1
        self.stop()

    @discord.ui.button(label="2 bullets", custom_id="2", row=1, style=discord.ButtonStyle.secondary)
    async def second_button_callback(self, interaction, button: discord.ui.Button):
        await interaction.response.send_message("Выбран режим с 2 пулями")
        values['bulletin_counter'] = 2
        self.stop()

    @discord.ui.button(label="3 bullets", custom_id="3", row=2, style=discord.ButtonStyle.secondary)
    async def third_button_callback(self, interaction, button: discord.ui.Button):
        await interaction.response.send_message("Выбран режим с 3 пулями")
        values['bulletin_counter'] = 3
        self.stop()


class PreshootView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=20.0)
        self.choice = None

    @discord.ui.button(label="Выстрелить!", row=0, style=discord.ButtonStyle.danger)
    async def shoot(self, interaction, button: discord.ui.Button):
        self.choice = True
        await interaction.response.send_message("Вы решили нажать на курок")
        self.stop()


class ContinueRussianRoulette(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30.0)
        self.choice = None

    @discord.ui.button(label="Продолжить", row=0, style=discord.ButtonStyle.danger)
    async def continue_button(self, interaction, button: discord.ui.Button):
        self.choice = True
        await interaction.response.send_message("Вы решили нажать на курок")
        self.stop()

    @discord.ui.button(label="Выйти из игры", row=0, style=discord.ButtonStyle.green)
    async def stop_button(self, interaction, button: discord.ui.Button):
        self.choice = False
        await interaction.response.send_message("Вы решили не нажимать на курок")
        self.stop()


class StartHangman(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30.0)
        values['start_hangman'] = False

    @discord.ui.button(label="Правила", row=0, style=discord.ButtonStyle.danger)
    async def rules_button(self, interaction, button: discord.ui.Button):
        is_ready = HangmanReady()
        await interaction.response.send_message("Правила игры в виселицу:"
                                                "\n1. Бот генерирует рандомное существительное из русского языка, "
                                                "ваша задача - угадать слово, загаданное ботом"
                                                "\n2. Слово состоит из русских символов нижнего регистра"
                                                "\n3. Каждый ход игрок пишет одну букву, если буква есть в слове,"
                                                " то эти 'буквы открываются', иначе тратится одна попытка"
                                                "\n4. За игру игрок может допустить 5 ошибок"
                                                "\n5. Допустив 6 ошибок игрок проигрывает и считается повешеным"
                                                "\n6. Если игрок угадал слово, не совершив 6 ошибок,"
                                                " он счиатется победителем"
                                                "\nЧтобы начать игру нажмите кнопку ниже", view=is_ready)
        await is_ready.wait()
        self.stop()

    @discord.ui.button(label="Начать", row=0, style=discord.ButtonStyle.green)
    async def start_button(self, interaction, button: discord.ui.Button):
        values['start_hangman'] = True
        await interaction.response.send_message("Начинаем игру в виселицу")
        self.stop()


@bot.tree.command(name="animeguesser", description="КЕФИР")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('Выбирай опенинг или будешь смотреть Boku no Pico ДЕСЯЦ ЧАСОВ!,!!',
                                            view=MyView())
    search = "https://youtu.be/t-3VRjLF7vI?si=TpFJtKtD4N5oLKlw"  # <- сылка на ютуб видео

    if not interaction.user.voice:
        await interaction.channel.send("Вы не в войсе")
    voice = await interaction.user.voice.channel.connect()
    await interaction.channel.send("Fine")

    info = yt_dlp.YoutubeDL(YDL_OPTIONS).extract_info(search, download=False)
    url, title = info["url"], info["title"]  # url = аудио файл, title = название видео в ютубе

    source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS, executable=FFMPEG_PATH)
    source = discord.PCMVolumeTransformer(source, volume=0.45)
    # ВАЖНО: нужно указывать СВОЙ путь для ffmpeg.exe

    voice.play(source)

    while voice.is_playing():
        await asyncio.sleep(0.2)
    await voice.disconnect()


@bot.tree.command(name="russian_roulette", description="Традиционная русская рулетка")
async def russian_roulette(interaction: discord.Interaction):
    bulletin_choose = BulletCountChoose()
    pull_the_trigger = PreshootView()
    continue_opt = ContinueRussianRoulette()
    await interaction.response.send_message('Выбери количество пуль для игры:',
                                            view=bulletin_choose)
    await bulletin_choose.wait()

    bulletin_choose.choice = values['bulletin_counter']
    if bulletin_choose.choice > 1:
        await interaction.channel.send(f'В БАРАБАНЕ {bulletin_choose.choice} ПУЛИ')
    else:
        await interaction.channel.send(f'В БАРАБАНЕ {bulletin_choose.choice} ПУЛЯ')
    await asyncio.sleep(1)
    alive = 1
    bullet_pos = 0
    bulletoptions = "123456"
    dead_bullet_pos = (''.join(random.sample(bulletoptions, len(bulletoptions))))[:bulletin_choose.choice]
    await interaction.followup.send('Ты уверен что хочешь нажать? Нажми кнопку для выстрела:',
                                    view=pull_the_trigger)
    await pull_the_trigger.wait()
    while alive:
        bullet_pos += 1
        if pull_the_trigger.choice:
            await interaction.channel.send('окак')
            await asyncio.sleep(3)
            for sec in range(3, 0, -1):
                await interaction.channel.send(str(sec))
                await asyncio.sleep(1)
            if str(bullet_pos) in dead_bullet_pos:
                await interaction.channel.send(f'Вы получили пулю в лоб и проиграли.'
                                               f'\n Ваша пуля была: {bullet_pos} '
                                               f'\n Проигрышные позиции были {dead_bullet_pos.split()}')
                alive = 0

            else:
                await interaction.followup.send('Ты уверен что хочешь нажать? Нажми кнопку для выстрела:',
                                                view=continue_opt)
                await continue_opt.wait()
                if continue_opt.choice:
                    pass
                elif continue_opt.choice is False:
                    await interaction.channel.send("Игрок вышел из игры живым"
                                                   f'\n Ваша последняя пуля была: {bullet_pos}'
                                                   f'\n Проигрышные позиции были: {dead_bullet_pos.split()}')
                    alive = 0
                else:
                    await interaction.channel.send(f"Игрок трусливо убежал от игры..."
                                                   f"\n Ваша последняя пуля была: {bullet_pos}"
                                                   f"\n Проигрышные позиции были: {dead_bullet_pos.split()}")
                    alive = 0
        else:
            await interaction.channel.send("Игрок трусливо убежал от игры...")
            alive = 0
    print('Игра закончена')


@bot.tree.command(name="hangman", description="Игра в виселицу")
async def hangman(interaction: discord.Interaction):
    def check(message):
        return message.author == interaction.user

    hangman_config = StartHangman()
    await interaction.response.send_message('Вы выбрали игру в виселицу, нажмите... '
                                            '\n Правила - получить список правил игры'
                                            '\n Играть - начать игру', view=hangman_config)
    await hangman_config.wait()
    if values['start_hangman'] is True:
        await interaction.followup.send('Ждем, пока бот выберет слово')
        answer_word = random.choice(RUSSIAN_NOUNS)
        while '-' in answer_word or ' ' in answer_word:
            answer_word = random.choice(RUSSIAN_NOUNS)
        await asyncio.sleep(3)

        secret_word = '-' * len(answer_word)
        error_counter = 0
        attempt = 0
        used_letters = []
        while error_counter != 6:
            if attempt == 0:
                await interaction.channel.send(f'Ваше слово: {secret_word}\nИспользованных букв нет')

            if attempt > 0:
                await interaction.channel.send(f'Ваше слово: {secret_word}\nИспользованных буквы: {used_letters}'
                                               f' Число ошибок {error_counter}')
            if secret_word.count('-') == 0:
                break

            await interaction.channel.send('Введите вашу букву')

            try:
                letter = (await bot.wait_for('message', check=check, timeout=120.0)).content
                await interaction.channel.send(f"Вы написали: {letter}")

                if (len(str(letter)) == 1 and str(letter).lower() in 'йцукенгшщзхъфывапролджэячсмитьбю'
                        and not str(letter).lower() in used_letters):
                    exchance_counter = 0
                    for i in range(len(secret_word)):
                        if answer_word[i] == letter:
                            secret_word = secret_word[:i] + letter + secret_word[i + 1:]
                            exchance_counter += 1

                    if exchance_counter > 0:
                        await interaction.channel.send(f'Поздравляю вы правильно угадали букву')
                    else:
                        await interaction.channel.send(f'Ошибка! Неверная буква')
                        error_counter += 1
                    attempt += 1
                    used_letters.append(letter)
                    await asyncio.sleep(1)
                else:
                    await interaction.channel.send(f"Неверный формат.\n"
                                                   f"Напишите НОВУЮ ОДНУ РУССКУЮ букву")
            except asyncio.TimeoutError:
                await interaction.channel.send("Время вышло!")
                error_counter = 6
                await asyncio.sleep(1)

        if error_counter == 6:
            await interaction.channel.send(f"Вы проиграли и были повешены, загаданное слово было {answer_word}")
        else:
            await interaction.channel.send(f"Поздравляю, вы выиграли!\n"
                                           f"Вы угадали слово '{answer_word}' за {attempt} попыток")
    else:
        interaction.response.send_message(' ... ')


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to Discord!")
    try:
        guild = discord.Object(1171003166985302046)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        logger.info(f"Successfully synced {len(synced)} command(s) to discord")
    except Exception as e:
        logger.info(f"SOMETHING WENT WRONG: {e}")


bot.run(TOKEN)