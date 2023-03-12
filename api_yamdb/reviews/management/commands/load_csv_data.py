from csv import DictReader
from django.core.management import BaseCommand

from reviews.models import Review, Comment, User
from reviews.models import Category, Genre, Title, GenreTitle

DICT = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
    GenreTitle: 'genre_title.csv'
}


class Command(BaseCommand):
    help = 'Загрузка данных из static/data'

    def handle(self, *args, **options):
        for model in DICT:
            if model.objects.exists():
                print('Данные уже загружены в базу!')
                return 'Очистите базу при помощи комманды delete_csv_data'

        print('Загрузка данных...')
        for model in DICT:
            with open(f'static/data/{DICT[model]}', encoding='utf-8') as ifile:
                reader = DictReader(ifile)
                for row in reader:
                    if 'category' in row:
                        row['category_id'] = row.pop('category')
                    if 'author' in row:
                        row['author_id'] = row.pop('author')
                    data = model(**row)
                    data.save()
