import cy_kit
import apps.services.apps
@cy_kit.container()
class Container:
    class Services:
        app_services:apps.services.apps.AppServices = cy_kit.single(apps.services.apps.AppServices)
