from gamer_bot import GamerBot

class Manager:

    def __init__(self):
        self.k = 0
        self.range = []
        self.gamer_bot = GamerBot()
        self.player_number = 0

    def set_k(self, k):
        self.k = k

    def set_range(self, a, b):
        self.range = [i for i in range(a, b+1)]
        self.gamer_bot.set_range(a, b)

    def set_player_number(self, player_number):
        self.player_number = player_number

    def ask_inputs(self):
        print("Добрый день, я менеджер игры!")
        print("Введите диапазон чисел через пробел:")
        a, b = map(int, input().split())
        self.set_range(a, b)
        print("Введите, сколько ходов будет идти игра:")
        k = int(input())
        self.set_k(k)
        print("Введите число, которое Вы загадали:")
        player_number = int(input())
        self.set_player_number(player_number)

    def game_iteration(self, iter):
        print(f"Ход номер {iter + 1}")
        print("Ваша очередь угадывать число:")
        player_num = int(input())
        bot_answer = self.gamer_bot.give_answer(player_num)
        print(f"Ответ бота: {bot_answer}")
        print("Очередь бота угадывать число:")
        bot_num = self.gamer_bot.ask_number()
        print(f"Бот спросил: Это число {bot_num}?")
        print("1. Нет, больше")
        print("2. Нет, меньше")
        print("3. Да")
        player_ans = int(input())
        self.gamer_bot.get_answer(player_ans)
        return player_num, bot_num

    def play(self):
        self.ask_inputs()
        player_num, bot_num = 0, 0
        for i in range(self.k):
            player_num, bot_num = self.game_iteration(i)
            if bot_num == self.player_number and player_num == self.gamer_bot.number:
                print("Ничья! Оба угадали!")
                break
            elif bot_num == self.player_number:
                print("Победа бота!")
                break
            elif player_num == self.gamer_bot.number:
                print("Победа игрока!")
                break
        else:
            if abs(bot_num - self.player_number) > abs(player_num - self.gamer_bot.number):
                print("Победа игрока!")
            elif abs(bot_num - self.player_number) < abs(player_num - self.gamer_bot.number):
                print("Победа бота!")
            else:
                print("Ничья! Оба одинаково близки!")
        print(f"Число бота: {self.gamer_bot.number}, число игрока: {self.player_number}")

        print("Конец игры!")

