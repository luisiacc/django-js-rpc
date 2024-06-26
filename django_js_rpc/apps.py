from django.apps import AppConfig
from django.conf import settings
import os

class DjangoJsRpcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_js_rpc'

    def ready(self):
        from .generator import generator

        output_dir = getattr(settings, 'JS_RPC_OUTPUT_DIR', '')
        output_file = os.path.join(output_dir, 'rpcClient.ts')

        os.makedirs(output_dir, exist_ok=True)

        views = generator.analyze_views()
        typescript_code = generator.generate_typescript(views)

        with open(output_file, 'w') as f:
            f.write(typescript_code)

        print(f"TypeScript API client generated at: {output_file}")
