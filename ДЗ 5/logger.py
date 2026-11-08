import time
from enum import Enum


class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    FATAL = 50


class FamilyEvents(Enum):
    CITY_CREATED = "CITY-001"
    FAMILY_SETTLED = "FAM-001"
    CHILD_ADDED = "FAM-002"
    MIDDLE_NAME_GEN = "FAM-003"
    VALIDATION_ERROR = "PER-500"


class ImageEvents(Enum):
    CONVERT_START = "IMG-100"
    CONVERT_OK = "IMG-101"
    CONVERT_ERROR = "IMG-500"
    PALETTE_INVALID = "IMG-501"


class LogRecord:
    def __init__(self, timestamp, level, source, message,
                 event_id, user=None, extra=None):
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message
        self.event_id = event_id
        self.user = user
        self.extra = extra if extra is not None else {}

    def format(self):
        t  = time.localtime(self.timestamp)
        ms = int((self.timestamp - int(self.timestamp)) * 1000)
        ts = "%04d-%02d-%02d %02d:%02d:%02d.%03d" % (
            t.tm_year, t.tm_mon, t.tm_mday,
            t.tm_hour, t.tm_min, t.tm_sec, ms
        )
        user = self.user if self.user else "-"
        line = "[%s] [%s] [%s] [event_id=%s] [user=%s] %s" % (
            ts, self.level.name, self.source,
            self.event_id, user, self.message
        )
        if self.extra:
            parts = []
            for k in self.extra:
                parts.append("%s=%s" % (k, self.extra[k]))
            line += " | extra: " + ", ".join(parts)
        return line


class LoggerManager:
    def __init__(self, log_file="Log.txt", min_level=LogLevel.DEBUG, source="App", user=None):
        self.log_file       = log_file
        self.min_level      = min_level
        self.default_source = source
        self.default_user   = user
        self.records        = []

        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("=== Log started at %s ===\n" % self._now_str())

    def _now_str(self):
        t = time.localtime()
        return "%04d-%02d-%02d %02d:%02d:%02d" % (
            t.tm_year, t.tm_mon, t.tm_mday,
            t.tm_hour, t.tm_min, t.tm_sec
        )

    def log(self, level, message, event_id,
            source=None, user=None, extra=None, exc=None):
        full_extra = dict(extra) if extra else {}
        if exc is not None:
            full_extra["exception"]         = type(exc).__name__
            full_extra["exception_message"] = str(exc)

        record = LogRecord(
            timestamp=time.time(),
            level=level,
            source=source or self.default_source,
            message=message,
            event_id=event_id,
            user=user or self.default_user,
            extra=full_extra
        )
        self.records.append(record)
        if level.value >= self.min_level.value:
            self._write_to_file(record)
        return record


    def debug(self, message, event_id, **kw):
        return self.log(LogLevel.DEBUG, message, event_id, **kw)

    def info(self, message, event_id, **kw):
        return self.log(LogLevel.INFO, message, event_id, **kw)

    def warn(self, message, event_id, **kw):
        return self.log(LogLevel.WARN, message, event_id, **kw)

    def error(self, message, event_id, **kw):
        return self.log(LogLevel.ERROR, message, event_id, **kw)

    def fatal(self, message, event_id, **kw):
        return self.log(LogLevel.FATAL, message, event_id, **kw)


    def _write_to_file(self, record):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(record.format() + "\n")


    def filter_by_level(self, level):
        return [r for r in self.records if r.level == level]

    def filter_by_source(self, source):
        return [r for r in self.records if r.source == source]

    def filter_by_event_id(self, event_id):
        return [r for r in self.records if r.event_id == event_id]

    def count_by_level(self):
        result = {}
        for r in self.records:
            n = r.level.name
            result[n] = result.get(n, 0) + 1
        return result

    def summary(self):
        lines = ["=== Log summary ==="]
        lines.append("Всего записей: %d" % len(self.records))
        counts = self.count_by_level()
        for name in ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]:
            if name in counts:
                lines.append("  %s: %d" % (name, counts[name]))
        return "\n".join(lines)



class Gender:
    MALE   = "male"
    FEMALE = "female"


class MiddleNameStrategy:
    def make(self, first_name, gender, father, mother, family):
        raise NotImplementedError


class PatronymicFromFather(MiddleNameStrategy):
    def make(self, first_name, gender, father, mother, family):
        if father is None:
            return NewBranchStrategy("Ветка_%s" % family.surname).make(
                first_name, gender, father, mother, family
            )
        suffix = "ович" if gender == Gender.MALE else "овна"
        return father.first_name + suffix


class NewBranchStrategy(MiddleNameStrategy):
    def __init__(self, branch_name="НоваяВетка"):
        self.branch_name = branch_name

    def make(self, first_name, gender, father, mother, family):
        if mother is not None:
            suffix = "ович" if gender == Gender.MALE else "овна"
            return mother.first_name + suffix
        return self.branch_name


class Person:
    def __init__(self, first_name, last_name, gender, birth_year,
                 middle_name=None, family=None):
        self.first_name  = first_name
        self.last_name   = last_name
        self.gender      = gender
        self.birth_year  = birth_year
        self.middle_name = middle_name
        self.family      = family

    def full_name(self):
        mn = (" " + self.middle_name) if self.middle_name else ""
        return "%s%s %s" % (self.first_name, mn, self.last_name)


class Family:
    def __init__(self, father=None, mother=None, surname=None, city=None):
        self.father   = father
        self.mother   = mother
        self.children = []
        self.surname  = surname or (
            father.last_name if father
            else mother.last_name if mother
            else "Безымянные"
        )
        self.city   = city
        self.logger = city.logger if city is not None else None

        if father is not None:
            father.family = self
        if mother is not None:
            mother.family = self

    def add_child(self, first_name, gender, birth_year,
                  middle_name=None, strategy=None):
        try:
            if middle_name is None:
                if strategy is None:
                    strategy = PatronymicFromFather()
                middle_name = strategy.make(
                    first_name, gender, self.father, self.mother, self
                )
                if self.logger is not None:
                    self.logger.debug(
                        "Сгенерировано отчество '%s' для '%s'"
                        % (middle_name, first_name),
                        event_id=FamilyEvents.MIDDLE_NAME_GEN,
                        source="Family",
                        extra={"child": first_name,
                               "strategy": type(strategy).__name__}
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

            if self.logger is not None:
                self.logger.info(
                    "Добавлен ребёнок: %s" % child.full_name(),
                    event_id=FamilyEvents.CHILD_ADDED,
                    source="Family",
                    extra={"family": self.surname,
                           "child": child.first_name,
                           "year": birth_year}
                )
            return child

        except Exception as e:
            if self.logger is not None:
                self.logger.error(
                    "Ошибка при добавлении ребёнка: %s" % e,
                    event_id=FamilyEvents.VALIDATION_ERROR,
                    source="Family",
                    exc=e,
                    extra={"family": self.surname, "child": first_name}
                )
            raise


class City:
    def __init__(self, name, logger=None):
        self.name     = name
        self.families = []
        self.people   = []
        self.logger   = logger if logger is not None else LoggerManager(source="City")

        self.logger.info(
            "Создан город '%s'" % name,
            event_id=FamilyEvents.CITY_CREATED,
            source="City",
            extra={"city": name}
        )

    def settle_family(self, family):
        family.city   = self
        family.logger = self.logger
        self.families.append(family)

        members = [p for p in (family.father, family.mother, *family.children)
                   if p is not None]
        for p in members:
            if p not in self.people:
                self.people.append(p)

        self.logger.info(
            "Поселена семья '%s'" % family.surname,
            event_id=FamilyEvents.FAMILY_SETTLED,
            source="City",
            extra={"surname": family.surname, "members": len(members)}
        )

    def new_family(self, father=None, mother=None, surname=None):
        family = Family(father=father, mother=mother,
                        surname=surname, city=self)
        self.settle_family(family)
        return family



def main():
    print("=== Демонстрация LoggerManager (без import) ===\n")
    print(LogLevel.DEBUG)
    logger = LoggerManager(
        log_file="Log.txt",
        min_level=LogLevel.DEBUG,
        source="Main",
        user="student"
    )


    logger.debug("Инициализация модулей",
                 event_id="APP-001", source="App")
    logger.info("Программа запущена",
                event_id="APP-002", source="App")
    logger.warn("Параметр не задан, берём значение по умолчанию",
                event_id="APP-003", source="Config",
                extra={"param": "max_families", "default": 100})


    try:
        x = 1 / 0
    except ZeroDivisionError as e:
        logger.error("Деление на ноль при расчёте статистики",
                     event_id="STAT-500", source="Statistics",
                     exc=e, extra={"operation": "division"})

    logger.fatal("Критическая ошибка файловой системы",
                 event_id="FS-999", source="FS",
                 extra={"path": "/data", "errno": 28})


    print("--- Работа города и семей ---")
    city = City("Москва", logger=logger)

    father = Person("Иван", "Петров", Gender.MALE, 1980)
    mother = Person("Анна", "Петрова", Gender.FEMALE, 1982)

    family = city.new_family(father, mother)

    child1 = family.add_child("Сергей", Gender.MALE, 2010)
    print("Ребёнок 1:", child1.full_name(), "(отчество по отцу)")

    child2 = family.add_child("Ольга", Gender.FEMALE, 2012,
                              strategy=NewBranchStrategy("НоваяВетка"))
    print("Ребёнок 2:", child2.full_name(), "(новая ветка)")

    child3 = family.add_child("Пётр", Gender.MALE, 2015,
                              middle_name="Сергеевич")
    print("Ребёнок 3:", child3.full_name(), "(отчество задано вручную)")

    father2 = Person("Олег", "Сидоров", Gender.MALE, 1975)
    mother2 = Person("Мария", "Сидорова", Gender.FEMALE, 1977)
    family2 = city.new_family(father2, mother2)
    child4 = family2.add_child("Дмитрий", Gender.MALE, 2008)
    print("Ребёнок 4:", child4.full_name())

    print("\nВсего семей: %d" % len(city.families))
    print("Всего жителей: %d" % len(city.people))


    logger.debug("Начато преобразование Цветное->Монохром",
                 event_id=ImageEvents.CONVERT_START,
                 source="ImageConverter",
                 extra={"from": "ColorImage", "to": "MonochromeImage"})
    logger.info("Преобразование завершено",
                event_id=ImageEvents.CONVERT_OK,
                source="ImageConverter")
    logger.error("Некорректная палитра: длина 128 вместо 256",
                 event_id=ImageEvents.PALETTE_INVALID,
                 source="ImageConverter",
                 extra={"palette_size": 128})

    # ---- Анализ ----
    print("\n" + logger.summary())

    print("\nТолько ERROR и выше:")
    for r in logger.records:
        if r.level.value >= LogLevel.ERROR.value:
            print("  " + r.format())

    print("\nЗаписи по источнику 'Family':")
    for r in logger.filter_by_source("Family"):
        print("  " + r.format())

    print("\nЗаписи с event_id = FAM-002 (добавление ребёнка):")
    for r in logger.filter_by_event_id(FamilyEvents.CHILD_ADDED):
        print("  " + r.format())

    print("\nВсе записи сохранены в Log.txt")


if __name__ == "__main__":
    main()