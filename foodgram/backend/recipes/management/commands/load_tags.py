from django.core.management.base import BaseCommand

from recipes.models import Tag

DEFAULT_TAGS = [
    {"name": "Завтрак", "slug": "breakfast"},
    {"name": "Обед", "slug": "lunch"},
    {"name": "Ужин", "slug": "dinner"},
]


class Command(BaseCommand):
    help = "Создание дефолтных тегов (Завтрак, Обед, Ужин)"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        for row in DEFAULT_TAGS:
            obj, created = Tag.objects.get_or_create(
                slug=row["slug"], defaults=row
            )
            if created:
                created_count += 1
            else:
                if obj.name != row["name"]:
                    obj.name = row["name"]
                    obj.save(update_fields=["name"])
                    updated_count += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Created: {created_count}, updated: {updated_count}"
            )
        )
