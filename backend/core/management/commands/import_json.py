import json
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from progress.bar import PixelBar


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file")
        parser.add_argument("-a", "--app")
        parser.add_argument("-m", "--model")

    def handle(self, *args, **options):
        app_label = options.get("app")
        model_name = options.get("model")
        model = apps.get_model(app_label=app_label, model_name=model_name)
        with open(options.get("file"), "r", encoding="utf-8") as file:
            try:
                text = json.load(file)
            except TypeError:
                try:
                    text = json.loads(file.readlines()[0])
                except TypeError:
                    raise CommandError("JSON is not a valid.")
            bar = PixelBar(
                f"Adding data in model {model.__name__}", max=len(text)
            )
            for item in text:
                model.objects.create(**item)
                bar.next()
        bar.finish()
        self.stdout.write(self.style.SUCCESS("Success!"))
