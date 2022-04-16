import csv
import logging
import os
import sys
from collections import OrderedDict

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre
from users.models import User

CSV_MODELS = OrderedDict([
    ('users.csv', User),
    ('category.csv', Category),
    ('genre.csv', Genre),
    ('titles.csv', Title),
    ('genre_title.csv', TitleGenre),
    ('review.csv', Review),
    ('comments.csv', Comment),
])

FK = {
    'titles.csv': {'category': Category},
    'review.csv': {
        'author': User,
        'title': Title,
    },
    'genre_title': {
        'title': Title,
        'genre': Genre,
    },
    'comments.csv': {
        'review': Review,
        'author': User}
}

formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


class Command(BaseCommand):
    help = 'Load tested data from csv-files into Rewiews app objects'

    def add_arguments(self, parser):
        parser.add_argument(
            '-p',
            '--csv_path',
            dest='csv_path',
            type=str,
            default=os.path.join(settings.BASE_DIR, 'static/data/'),
            help='Путь к папке с csv файлами'
        ),
        parser.add_argument(
            '--no_delete',
            action='store_false',
            help='Не удалять текущие данные перед заливкой новых',
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        logger.info(f'директория с csv-файлами - {csv_path}')
        files = [f for f in os.listdir(csv_path)
                 if os.path.isfile(os.path.join(csv_path, f))
                 and f in CSV_MODELS]
        for file, model in CSV_MODELS.items():
            if file not in files:
                logger.warning(f'отсутствует заявленный файл - {file}')
                continue
            if options['no_delete']:
                model.objects.all().delete()
            logger.info(f'обработка файла - {file}')
            with open(
                os.path.join(csv_path, file),
                newline='',
                encoding='utf-8'
            ) as csvfile:
                observes = []
                data = csv.reader(csvfile, delimiter=',')
                headers = next(data)
                for row in data:
                    observe = dict(zip(headers, row))
                    if file in FK:
                        for header, value in zip(headers, row):
                            if header in FK[file]:
                                observe[header] = (
                                    FK[file][header].objects.get(pk=value)
                                )
                    observes.append(model(**observe))
                model.objects.bulk_create(observes)
