import inspect
import api_apps.app_params
fx =inspect.signature(api_apps.app_params.AppParam)
print(fx)