import json
import os
import shutil

from django.conf import settings

from django_yarnpkg.management.base import BaseYarnCommand
from django_yarnpkg.yarn import yarn_adapter

from ...util.frontend_helpers import get_apps_with_assets


class Command(BaseYarnCommand):
    help = "Create webpack bundles for AlekSIS"  # noqa

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)

        # Write webpack entrypoints for all apps
        assets = {
            app: {"dependOn": "core", "import": os.path.join(path, "index")}
            for app, path in get_apps_with_assets().items()
        }
        assets["core"] = os.path.join(settings.BASE_DIR, "aleksis", "core", "assets", "index")
        with open(os.path.join(settings.NODE_MODULES_ROOT, "webpack-entrypoints.json"), "w") as out:
            json.dump(assets, out)

        # Install Node dependencies
        yarn_adapter.install(settings.YARN_INSTALLED_APPS)

        # Run webpack
        config_path = os.path.join(settings.BASE_DIR, "aleksis", "core", "webpack.config.js")
        shutil.copy(config_path, settings.NODE_MODULES_ROOT)
        yarn_adapter.call_yarn(["run", "webpack"])
