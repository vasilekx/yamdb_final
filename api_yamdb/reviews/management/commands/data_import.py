# reviews/management/commands/data_import.py

import csv
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _

from reviews.models import Category, Comment, Genre, Review, Title, User

ALREDY_LOADED_ERROR_MESSAGE = _(
    'База данных не пуста! '
    'Если вам нужно перезагрузить данные из CSV-файла, '
    'сначала удалите файл db.sqlite3. '
    'Затем запустите "python manage.py migrate" '
    'для создания новой пустой базы данных.'
)

data_files_list = [
    ['users.csv', User],
    ['category.csv', Category],
    ['genre.csv', Genre],
    ['titles.csv', Title],
    ['review.csv', Review],
    ['comments.csv', Comment],
]

genre_title = [
    'genre_title.csv',
    Title,
    os.path.join(settings.BASE_DIR, 'static/data', 'genre_title.csv')
]


def get_dirs(list_files: list) -> None:
    for i, lst in enumerate(list_files):
        data_files_list[i].append(
            os.path.join(settings.BASE_DIR, 'static/data', lst[0])
        )


def import_data(list_data: list) -> None:
    for file, model, path in list_data:
        with open(path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            header = next(reader)
            for row in reader:
                import_dict = {
                    key: value for key, value in zip(header, row)
                }
                if file == 'titles.csv':
                    category = Category.objects.get(
                        pk=import_dict['category']
                    )
                    import_dict['category'] = category
                    title = model(**import_dict)
                    title.save()
                    with open(genre_title[2], 'r', encoding='utf-8') as f:
                        reader_titles = csv.reader(
                            f,
                            delimiter=',',
                            quotechar='"'
                        )
                        header_t = next(reader_titles)
                        for row_t in reader_titles:
                            import_dict_titles = {
                                key: value for key, value in zip(header_t,
                                                                 row_t)
                            }
                            title_id = import_dict['id']
                            genge_title_id = import_dict_titles['title_id']
                            if title_id == genge_title_id:
                                genre = Genre.objects.get(
                                    pk=import_dict_titles['genre_id']
                                )
                                title.genre.add(genre)
                elif file == 'review.csv':
                    title = Title.objects.get(
                        id=import_dict['title_id']
                    )
                    import_dict['title'] = title
                    user = User.objects.get(
                        id=import_dict['author']
                    )
                    import_dict['author'] = user
                    model.objects.create(**import_dict)

                elif file == 'comments.csv':
                    review = Review.objects.get(
                        id=import_dict['review_id']
                    )
                    import_dict['review'] = review
                    user = User.objects.get(
                        id=import_dict['author']
                    )
                    import_dict['author'] = user
                    model.objects.create(**import_dict)
                else:
                    model.objects.create(**import_dict)


class Command(BaseCommand):
    help = _('Загрузка данных')

    def handle(self, *args, **options):
        for lst in data_files_list:
            if lst[1].objects.exists():
                self.stdout.write(
                    self.style.WARNING(ALREDY_LOADED_ERROR_MESSAGE)
                )
                return
        get_dirs(data_files_list)
        self.stdout.write(_('Загрузка данных...'))
        try:
            import_data(data_files_list)
            self.stdout.write(
                self.style.SUCCESS(_('Модели импортированы'))
            )
        except Exception:
            self.stdout.write(
                self.style.ERROR(_('Не удалось выполнить импорт'))
            )
