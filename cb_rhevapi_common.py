import ovirtsdk.api
import ovirtsdk.infrastructure
import ovirtsdk.xml


class TechnologyWrapper:

    def __init__(self, rv_host, rv_port, rv_user, rv_pass, rv_protocol="https"):
        self.stuff = rv_host, rv_port, rv_user, rv_pass, rv_protocol
