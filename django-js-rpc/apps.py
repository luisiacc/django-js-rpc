import os

from django.apps import AppConfig
from django.conf import settings


class DjangoTsApiGeneratorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_ts_api_generator"

    def ready(self):
        # Import here to avoid circular import issues
        from .generator import generator

        # Define the output path for the generated TypeScript file
        output_dir = getattr(settings, "TS_API_OUTPUT_DIR", "")
        output_file = os.path.join(output_dir, "rpcClient.ts")

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate the TypeScript file
        views = generator.analyze_views()
        typescript_code = generator.generate_typescript(views)

        with open(output_file, "w") as f:
            f.write(typescript_code)

        print(f"TypeScript API client generated at: {output_file}")
