from django.contrib import admin

from resourcehandlers.admin import ResourceHandlerAdmin
from .models import RhevResourceHandler, RhevOSBuildAttribute  # , RhevNetwork, RhevDisk


class RhevResourceHandlerAdmin(ResourceHandlerAdmin):
    #form = RhevCredentialsForm
    pass

# admin.site.register(RhevDisk)
# admin.site.register(RhevNetwork)
admin.site.register(RhevOSBuildAttribute)
admin.site.register(RhevResourceHandler, RhevResourceHandlerAdmin)
