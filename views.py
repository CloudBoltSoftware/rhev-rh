from infrastructure.models import Environment


def get_detail_tabs(handler, profile):
    """
    Append rhev specific tabs to base resource handler tabs.

    See resourcehandlers.views.get_detail_tabs for more info.
    """
    from resourcehandlers.views import NETWORK_TABLE_VALUES, get_detail_tabs as get_basic_tabs
    tabs = get_basic_tabs(handler, profile)

    rh_envs = handler.environment_set.all().order_by('name')
    templates = handler.osbuildattribute_set.exclude(template_name=None)

    for template in templates:
        if template.os_build:
            envs = template.os_build.environments.filter(id__in=rh_envs)
        else:
            envs = Environment.objects.none()
        template.envs = envs

    tabs.insert(1, ('Images', 'images', dict(template='resourcehandlers/tab-templates.html', context={
        'templates': templates, 'handler_can_discover_templates': True
    })))
    tabs.insert(2, ('Networks', 'networks', dict(template='resourcehandlers/tab-networks.html', context={
        'networks': handler.networks.all().values(*NETWORK_TABLE_VALUES)
    })))
    return tabs
