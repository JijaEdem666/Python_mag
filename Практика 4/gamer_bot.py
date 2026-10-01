import random

class GamerBot:

    def __init__(self):
        self.range = []
        self.number = 0
        self.opponent_number = 0

    def set_range(self, a, b):
        self.range = [i for i in range(a, b+1)]
        self.generate_number()

    def generate_number(self):
        self.number = random.choice(self.range)
        #print(f"Бот загадал {self.number}")

    def give_answer(self, number):
        if number < self.number:
            return "Нет, больше"
        elif number > self.number:
            return "Нет, меньше"
        else:
            return "Да"

    def ask_number_1(self):
        self.opponent_number = self.range[len(self.range) // 2]
        return self.opponent_number

    def ask_number_2(self):
        self.opponent_number = random.choice(self.range)
        return self.opponent_number

    def ask_number(self):
        return self.ask_number_2()

    def get_answer(self, answer):
        if answer == 1:
            self.range = self.range[self.range.index(self.opponent_number) + 1:]
        elif answer == 2:
            self.range = self.range[:self.range.index(self.opponent_number)]
        #print(self.range)

