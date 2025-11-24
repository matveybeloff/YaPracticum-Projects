import csv
import logging
import sys
from pathlib import Path
from typing import Iterable

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from recipes.models import Ingredient

LOG_FILE = Path(__file__).resolve().parent / "import_csv.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Импорт ингредиентов из CSV в recipes.Ingredient. По умолчанию "
        "ищет файл foodgram/data/ingredients.csv. Кодировки: cp1251, "
        "utf-8-sig"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file",
            help=(
                "Путь к CSV-файлу с ингредиентами. По умолчанию используется "
                "'foodgram/data/ingredients.csv'"
            ),
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help=(
                "Очистить таблицу перед импортом (используйте осторожно на "
                "продакшене)."
            ),
        )
        parser.add_argument(
            "--encoding",
            choices=["utf-8-sig", "utf-8", "cp1251"],
            help=(
                "Кодировка CSV (по умолчанию автоподбор: cp1251, затем "
                "utf-8-sig)"
            ),
        )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR).parent
        default_csv = base_dir / "data" / "ingredients.csv"

        path = Path(options.get("file") or default_csv)
        if not path.exists():
            raise CommandError(
                f"Файл с ингредиентами не найден: {path}"
            )
        if path.suffix.lower() != ".csv":
            raise CommandError("Ожидается файл с расширением .csv")

        enc_forced = options.get("encoding")
        rows = list(self._read_csv(path, encoding=enc_forced))
        if not rows:
            raise CommandError(
                "Не удалось прочитать данные из CSV (проверьте файл)"
            )

        if options.get("truncate"):
            logger.warning("Очистка таблицы ингредиентов...")
            Ingredient.objects.all().delete()
            self._reset_pk_sequence()

        created, updated, skipped = self._import_ingredients(rows)
        logger.info(
            "Результаты импорта: создано=%s, обновлено=%s, пропущено=%s",
            created,
            updated,
            skipped,
        )

    # ___ Чтение ___
    def _read_csv(
        self, filepath: Path, encoding: str | None = None
    ) -> Iterable[dict]:
        encodings = (
            [encoding] if encoding else ["utf-8-sig", "utf-8", "cp1251"]
        )
        for enc in encodings:
            try:
                with filepath.open(encoding=enc, newline="") as csv_file:
                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        yield {
                            k.strip(): (
                                v.strip() if isinstance(v, str) else v
                            )
                            for k, v in row.items()
                        }
                return
            except UnicodeDecodeError:
                continue

    # ___ Импорт ___
    def _import_ingredients(self, rows: Iterable[dict]):
        def pick_value(source: dict, keys: list[str]) -> str | None:
            for k in keys:
                if k in source and source[k]:
                    return str(source[k]).strip()
            return None

        total = 0
        unique_pairs: set[tuple[str, str]] = set()
        for row in rows:
            total += 1
            name = pick_value(row, ["name", "title"])
            unit = pick_value(row, ["measurement_unit", "unit", "measure"])
            if not name or not unit:
                vals = list(row.values())
                if len(vals) >= 2:
                    name = name or str(vals[0]).strip()
                    unit = unit or str(vals[1]).strip()
            if name and unit:
                unique_pairs.add((name, unit))

        if not unique_pairs:
            return 0, 0, total

        existing = set(
            Ingredient.objects.values_list("name", "measurement_unit")
        )
        to_insert = [
            Ingredient(name=n, measurement_unit=u)
            for (n, u) in unique_pairs
            if (n, u) not in existing
        ]

        created = 0
        if to_insert:
            with transaction.atomic():
                Ingredient.objects.bulk_create(
                    to_insert,
                    ignore_conflicts=True,
                    batch_size=1000,
                )
            created = len(to_insert)
        updated = 0
        skipped = total - created
        return created, updated, skipped

    def _reset_pk_sequence(self):
        from django.db import connection

        vendor = connection.vendor
        try:
            with connection.cursor() as cursor:
                table = Ingredient._meta.db_table
                if vendor == "sqlite":
                    cursor.execute(
                        "DELETE FROM sqlite_sequence WHERE name=%s",
                        [table],
                    )
                elif vendor == "postgresql":
                    cursor.execute(
                        (
                            "SELECT setval(pg_get_serial_sequence(%s, 'id'), "
                            "1, false)"
                        ),
                        [table],
                    )
        except Exception as exc:
            logger.warning("Could not reset PK sequence: %s", exc)
