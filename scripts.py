import os
import random

import django
import configparser

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from datacenter.models import Schoolkid, Mark, Subject, Lesson, Chastisement, Commendation


def fix_marks(schoolkid):
    """Исправляет оценки 2 и 3 на 5 для указанного ученика."""
    Mark.objects.filter(schoolkid=schoolkid, points__in=[2, 3]).update(points=5)


def delete_chastisements(schoolkid):
    """Удаляет все замечания для ученика."""
    Chastisement.objects.filter(schoolkid=schoolkid).delete()


def create_commendation(schoolkid, subject_title):
    """Создает похвалу для ученика по указанному предмету."""
    try:
        subject = Subject.objects.get(
            title=subject_title,
            year_of_study=schoolkid.year_of_study
        )
    except Subject.DoesNotExist:
        raise ValueError(f"Предмет '{subject_title}' не найден.")

    lessons = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject=subject
    )

    if not list(lessons):
        raise ValueError(f"Уроки по предмету '{subject}' не найдены.")

    lesson = random.choice(list(lessons))
    commendation = random.choice(
        ["Молодец!", "Отлично!", "Хорошо!", "Прекрасно!", "Великолепно!"]
    )
    Commendation.objects.create(
        text=commendation,
        created=lesson.date,
        schoolkid=schoolkid,
        subject=subject,
        teacher=lesson.teacher
    )


def get_shcoolkid(name):
    """Находит ученика по имени."""
    try:
        return Schoolkid.objects.get(full_name__contains=name)
    except Schoolkid.DoesNotExist:
        raise ValueError(f"Ученик с именем '{name}', не найден.")
    except Schoolkid.MultipleObjectsReturned:
        raise ValueError(f"Учеников с именем '{name}' несколько, уточните запрос.")


def main():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    name = config.get('DEFAULT', 'name', fallback="Фролов Иван")
    subject_title = config.get('DEFAULT', 'subject_title', fallback="Математика")

    try:
        schoolkid = get_shcoolkid(name)
        fix_marks(schoolkid)
        delete_chastisements(schoolkid)
        create_commendation(schoolkid, subject_title)
        print("Операция выполнена успешно!")
        print(f"Исправлены оценки для ученика с именем '{name}'.")
        print(f"Добавлена похвала по предмету '{subject_title}'.")
    except Exception as error:
        print(f"Ошибка при выполнении программы: {error}")


if __name__ == "__main__":
    main()
