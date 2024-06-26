import inspect
import logging
import os
import re

from django.urls import get_resolver
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

logger = logging.getLogger(__name__)


class TypeScriptAPIGenerator:
    def __init__(self):
        self.base_ts_path = os.path.join(os.path.dirname(__file__), "rpcClient.base.ts")

    def get_view_class(self, view_func):
        if hasattr(view_func, "view_class"):
            return view_func.view_class
        elif hasattr(view_func, "cls"):
            return view_func.cls
        elif inspect.isclass(view_func) and issubclass(view_func, (APIView, ViewSet)):
            return view_func
        return None

    def get_view_name(self, view_class):
        name = view_class.__name__
        name = re.sub(r"(View|ViewSet)$", "", name)
        return name[0].lower() + name[1:]

    def get_view_methods(self, view_class):
        if issubclass(view_class, ViewSet):
            return ["list", "create", "retrieve", "update", "partial_update", "destroy"]
        elif issubclass(view_class, APIView):
            return [method.lower() for method in view_class.http_method_names if method != "options"]
        return []

    def extract_url_params(self, pattern):
        param_pattern = r"\(\?P<(\w+)>[^)]+\)"
        params = re.findall(param_pattern, pattern)
        ts_path = re.sub(param_pattern, r"${{\1}}", pattern)
        return params, ts_path

    def analyze_views(self):
        resolver = get_resolver()
        views = {}

        for key, value in resolver.reverse_dict.items():
            if isinstance(key, str):
                continue

            for url_pattern, url_name in value[0]:
                view_func = key
                view_class = self.get_view_class(view_func)

                if view_class and issubclass(view_class, (ViewSet, APIView)):
                    view_name = self.get_view_name(view_class)
                    params, ts_path = self.extract_url_params(url_pattern)

                    if view_name not in views:
                        views[view_name] = {
                            "methods": self.get_view_methods(view_class),
                            "path": ts_path,
                            "params": params,
                        }
                    logger.debug(f"Found view: {view_name}, path: {ts_path}")
                else:
                    logger.debug(f"Skipping non-ViewSet/APIView: {view_func}")

        logger.debug(f"Analyzed views: {views}")
        return views

    def generate_url_method(self, view_name, view_data):
        params = ", ".join([f"{param}: string" for param in view_data["params"]])
        return (
            f"""  url: ({params}) => this.reverse('{view_data['path']}', {{ {', '.join(view_data['params'])} }}),\n"""
        )

    def generate_query_method(self, view_name, method, view_data):
        query_params = "id: string, " if method == "retrieve" else ""
        return f"""
  {method}: {{
    query: ({query_params}options?: any) =>
      useQuery(
        ['{view_name}', '{method}'{', id' if method == 'retrieve' else ''}],
        () => this.request('GET', this.{view_name}.url({query_params.replace(': string', '')})),
        options
      ),
  }},"""

    def generate_mutation_method(self, view_name, method, view_data):
        return f"""
  {method}: {{
    mutation: (options?: any) =>
      useMutation(
        (data: any) => this.request('{method.upper()}', this.{view_name}.url({', '.join(f"data.{param}" for param in view_data['params'])}), data),
        options
      ),
  }},"""

    def generate_typescript(self, views):
        with open(self.base_ts_path, "r") as base_file:
            base_content = base_file.read()

        dynamic_content = []

        for view_name, view_data in views.items():
            view_content = [self.generate_url_method(view_name, view_data)]

            for method in view_data["methods"]:
                if method in ["list", "retrieve"]:
                    view_content.append(self.generate_query_method(view_name, method, view_data))
                else:
                    view_content.append(self.generate_mutation_method(view_name, method, view_data))

            view_definition = f"""
{view_name} = {{
{''.join(view_content)}
}};
"""
            dynamic_content.append(view_definition)

        all_views = "\n".join(dynamic_content)
        final_content = base_content.replace("  // DYNAMIC_CONTENT_PLACEHOLDER", all_views)

        return final_content


generator = TypeScriptAPIGenerator()
