import inspect
from django.urls import get_resolver
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from jinja2 import Environment, FileSystemLoader
import os
import re

class TypeScriptAPIGenerator:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.env.get_template('api.ts.j2')

    def get_view_name(self, view):
        return view.__class__.__name__

    def get_view_methods(self, view):
        if isinstance(view, ViewSet):
            return ['list', 'create', 'retrieve', 'update', 'partial_update', 'destroy']
        elif isinstance(view, APIView):
            return [method.lower() for method in view.http_method_names if method != 'options']
        return []

    def extract_url_params(self, path):
        # Extract URL parameters using regex
        param_pattern = r'\(\?P<(\w+)>[^)]+\)'
        params = re.findall(param_pattern, path)

        # Replace regex patterns with TypeScript template literals
        ts_path = re.sub(param_pattern, r'${{\1}}', path)

        return params, ts_path

    def analyze_views(self):
        resolver = get_resolver()
        views = {}

        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'callback') and (isinstance(pattern.callback, ViewSet) or isinstance(pattern.callback, APIView)):
                view_name = self.get_view_name(pattern.callback)
                params, ts_path = self.extract_url_params(pattern.pattern.regex.pattern)
                views[view_name] = {
                    'methods': self.get_view_methods(pattern.callback),
                    'path': ts_path,
                    'params': params,
                }

        return views

    def generate_typescript(self, views):
        return self.template.render(views=views)

generator = TypeScriptAPIGenerator()
