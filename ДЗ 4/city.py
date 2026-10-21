from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"



class MiddleNameStrategy:
    def make(self, child_first_name, child_gender,
             father, mother,
             family):
        ...


class PatronymicFromFather(MiddleNameStrategy):
    def make(self, child_first_name, child_gender, father, mother, family):
        if father is None:
            return NewBranchStrategy(f"Ветка_{family.surname}").make(
                child_first_name, child_gender, father, mother, family
            )

        suffix = "ович" if child_gender == Gender.MALE else "овна"
        return father.first_name + suffix


class NewBranchStrategy(MiddleNameStrategy):
    def __init__(self, branch_name = "НоваяВетка"):
        self.branch_name = branch_name

    def make(self, child_first_name, child_gender, father, mother, family):
        if mother is not None:
            suffix = "ович" if child_gender == Gender.MALE else "овна"
            return mother.first_name[:len(mother.first_name)-1] + suffix
        return self.branch_name


class Family:
    def __init__(self, father = None,
                 mother = None,
                 surname = None,
                 city = None):
        self.father = father
        self.mother = mother
        self.children = []
        self.surname = surname or (
            father.last_name if father else mother.last_name if mother else "Бесфамильные"
        )
        self.city = city

        if father:
            father.family = self
        if mother:
            mother.family = self

    def add_child(self, first_name, gender, birth_year, middle_name = None, strategy = None):
        if middle_name is None:
            strategy = strategy or PatronymicFromFather()
            middle_name = strategy.make(
                first_name, gender, self.father, self.mother, self
            )

        child = Person(
            first_name=first_name,
            last_name=self.surname,
            gender=gender,
            birth_year=birth_year,
            middle_name=middle_name,
            family=self
        )
        self.children.append(child)

        if self.city is not None:
            self.city.people.append(child)

        return child

@dataclass
class Person:
    first_name: str
    last_name: str
    gender: Gender
    birth_year: int
    middle_name: Optional[str] = None
    family: Optional[Family] = None


class City:
    def __init__(self, name):
        self.name = name
        self.families = []
        self.people = []

    def settle_family(self, family):
        family.city = self
        self.families.append(family)

        for person in (family.father, family.mother, *family.children):
            if person is not None and person not in self.people:
                self.people.append(person)

    def new_family(self, father = None, mother = None, surname = None):
        family = Family(father=father, mother=mother, surname=surname)
        self.settle_family(family)
        return family


city = City("Москва")
print(f"Создан город: {city.name}")

father = Person("Иван", "Петров", Gender.MALE, 1980)
mother = Person("Анна", "Петрова", Gender.FEMALE, 1982)

family = city.new_family(father, mother)

print(f"Поселили семью: {family.surname}")
print(f"  Отец:  {father.first_name} {father.last_name}")
print(f"  Мать:  {mother.first_name} {mother.last_name}")

child1 = family.add_child("Сергей", Gender.MALE, 2010)

print(f"\nРебёнок 1: {child1.first_name} {child1.middle_name} {child1.last_name} "
      f"(отчество по отцу)")

child2 = family.add_child(
    "Ольга", Gender.FEMALE, 2012,
    strategy=NewBranchStrategy("НоваяВетка")
)
print(f"Ребёнок 2: {child2.first_name} {child2.middle_name} {child2.last_name} "
      f"(новая ветка)")

child3 = family.add_child("Пётр", Gender.MALE, 2015, middle_name="Сергеевич")
print(f"Ребёнок 3: {child3.first_name} {child3.middle_name} {child3.last_name} "
      f"(отчество задано вручную)")

print(f"\nВсего жителей в городе: {len(city.people)}")

for p in city.people:
    print(f"  - {p.first_name} {p.middle_name or ''} {p.last_name}, "
          f"род. {p.birth_year}")


father2 = Person("Олег", "Сидоров", Gender.MALE, 1975)
mother2 = Person("Мария", "Сидорова", Gender.FEMALE, 1977)
family2 = city.new_family(father2, mother2)
child4 = family2.add_child("Дмитрий", Gender.MALE, 2008)

print()
print(f"Вторая семья: {family2.surname}")
print(f"  Ребёнок: {child4.first_name} {child4.middle_name} {child4.last_name}")
print(f"Всего семей в городе: {len(city.families)}")
print(f"Всего жителей в городе: {len(city.people)}")