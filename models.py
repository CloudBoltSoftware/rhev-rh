from __future__ import division

import os
import time

from django.db import models

from common.classes import TrueWithMessage, FalseWithMessage
from externalcontent.models import OSBuildAttribute
from infrastructure.models import Server, ServerNetworkCard
from resourcehandlers.models import ResourceHandler, ResourceNetwork
from settings import VARDIR
from utilities.exceptions import CloudBoltException
from utilities.logger import ThreadLogger

import ovirtsdk.api
import ovirtsdk.infrastructure
import ovirtsdk.xml

logger = ThreadLogger(__name__)

ONE_GIG = 2 ** 30


class RhevNetwork(ResourceNetwork):

    """
    TODO
    """
    uuid = models.CharField(max_length=36, default="")


class RhevOSBuildAttribute(OSBuildAttribute):
    template_name = models.CharField(max_length=100)
    uuid = models.CharField(max_length=100)

    def get_resource_handler(self):
        return self.rhevresourcehandler_set.first()

    def __unicode__(self):
        return self.template_name

    class Meta:
        verbose_name = "RHEV OS Build Attribute"


class RhevResourceHandler(ResourceHandler):

    """
    This class extends the ResourceHandler class to include
    elements specific to RHEV's Cloud Platform
    """
    cert_directory = os.path.join(VARDIR, "opt/cloudbolt/rhev")

    clusterName = models.CharField(max_length=100, default="")
    can_sync_vms = True
    networks = models.ManyToManyField(RhevNetwork, blank=True, null=True)
    os_build_attributes = models.ManyToManyField(RhevOSBuildAttribute,
                                                 null=True,
                                                 blank=True)
    type_name = "RHEV"

    _api = []

    @property
    def api(self):
        if self._api:
            api = self._api[0]
        else:
            api_url = self.get_api_url(self.protocol, self.ip, self.port)
            cert_filename = self.get_cert_filename(self.ip, self.port)
            api = ovirtsdk.api.API(url=api_url,
                                   username=self.serviceaccount,
                                   password=self.servicepasswd,
                                   ca_file=cert_filename)
            self._api.append(api)

        return api

    @classmethod
    def get_api_url(cls, protocol, ip, port):
        return "{0}://{1}:{2}/api".format(protocol, ip, port)

    @classmethod
    def get_cert_filename(cls, ip, port):
        filename = "{0}:{1}-ca.crt".format(ip, port)
        return os.path.join(cls.cert_directory, filename)

    def __init__(self, *args, **kwargs):
        super(RhevResourceHandler, self).__init__(*args, **kwargs)
        self.cluster_query = 'cluster="{0}"'.format(self.clusterName)

    def poweron_resource(self, resource_id, pxe=None):
        """
        TODO
        """
        server = Server.objects.get(id=resource_id)
        try:
            vm = self.api.vms.get(id=server.resource_handler_svr_id)
            vm.start()
        except ovirtsdk.infrastructure.errors.RequestError as e:
            message = "Power on response for server {0}: {1}"
            logger.info(message.format(resource_id, e.detail))
            return False
        return True

    def poweroff_resource(self, resource_id):
        """
        TODO
        """
        server = Server.objects.get(id=resource_id)
        if not server.resource_handler_svr_id:
            # in the case where prov failed badly, it is possible for the
            # server.resource_handler_svr_id to be ""
            message = ("Could not power off server {0}: no "
                       "resource_handler_svr_id set")
            logger.info(message.format(server.hostname))
            return False

        try:
            vm = self.api.vms.get(id=server.resource_handler_svr_id)
            vm.stop()

        except ovirtsdk.infrastructure.errors.RequestError as e:
            message = "Power off response for server {0}: {1}"
            logger.info(message.format(server.hostname, e.detail))
            return False

        # Give it 2 minutes to shut down, continually checking the state.
        is_up = True
        t_end = time.time() + 120
        while time.time() < t_end:
             #  Continually refresh the object...
             vm = self.api.vms.get(id=server.resource_handler_svr_id)
             if vm.status.state == 'down':
                  is_up = False
                  break
 
        if is_up:
            message = "Host is not powered down after 2 minutes."
            logger.info(message)
            return False

        return True

    def configure_network(self, resource_id, job=None):
        server = Server.objects.get(id=resource_id)

        # try to power on for three minutes
        tries = 36
        while tries > 0 and not self.poweron_resource(resource_id):
            tries -= 1
            time.sleep(5)

        if tries == 0:
            message = "Power on failed for server {0}".format(server.hostname)
            logger.info(message)
            # TODO: set server to powered off state in cloudbolt

    def add_nics_to_server(self, resource_id, delete_first=True):
        """
        TODO
        """
        server = Server.objects.get(id=resource_id)

        server_net_list = server.get_network_list()
        if not server_net_list:
            raise CloudBoltException(
                "No networks found! At least one is needed to build a "
                "server using this Resource Handler ({0})".format(self))

        vm_obj = self.api.vms.get(id=server.resource_handler_svr_id)
        cluster_obj = self.api.clusters.get(name=self.clusterName)

        # remove all existing NICs if flag set to do so
        if delete_first:
            for nic_obj in vm_obj.nics.list():
                logger.info("Removing NIC from server {0}".format(server.hostname))
                # try to delete NIC for three minutes
                tries = 10
                while tries > 0:
                    try:
                        nic_obj.delete()
                        break
                    except ovirtsdk.infrastructure.errors.RequestError, e:
                        message = "Waiting to delete NIC from server {0}.  Error: {1}"
                        logger.info(message.format(server.hostname, e))
                    tries -= 1
                    time.sleep(5)
                else:
                    message = "Delete NIC failed for server {0}".format(server.hostname)
                    logger.info(message)
                    raise CloudBoltException(message)

        # add requested NICs
        network_counter = 0
        for network in server_net_list:
            mac, ip = server.get_mac_ip(network_counter)

            nic_name = "nic{0}".format(network_counter + 1)
            nic_obj = vm_obj.nics.get(name=nic_name)
            # try to add NIC for three minutes
            logger.info("Adding NIC to server {0}".format(server.hostname))
            tries = 36
            while tries > 0:
                try:
                    # Check to see if nic already exists, update the network if
                    # it does, create it if it doesn't
                    if not nic_obj:
                        params = ovirtsdk.xml.params.NIC(
                            name=nic_name,
                            interface="virtio",
                            network=cluster_obj.networks.get(id=network.uuid),
                            mac=ovirtsdk.xml.params.MAC(mac) if mac else None,
                        )
                        nic_obj = vm_obj.nics.add(params)
                    else:
                        net_obj = cluster_obj.networks.get(id=network.uuid),
                        nic_obj.set_network(net_obj)
                    mac = nic_obj.mac.address
                    break
                except ovirtsdk.infrastructure.errors.RequestError, e:
                    # This may catch more errors than we want
                    message = "Waiting to add nic to server {0}"
                    logger.info(message.format(server.hostname))
                    logger.debug(e)
                tries -= 1
                time.sleep(5)
            else:
                message = "Add nic failed for server {}".format(server.hostname)
                logger.info(message)
                # TODO: set NIC to actual state in cloudbolt
                raise CloudBoltException(message)

            nic, created = ServerNetworkCard.objects.get_or_create(
                index=network_counter,
                server=server)
            network_counter += 1
            if ip:
                nic.ip = ip
                nic.bootproto = "dhcp" if ip == "dhcp" else "static"
            nic.network = network
            nic.mac = mac
            nic.save()

    def create_resource(self, resource_id, use_template):
        """
        TODO
        """
        server = Server.objects.get(id=resource_id)
        logger.info("creating new vm {0}".format(server.hostname))

        os_attributes = self.os_build_attributes.filter(
            os_build=server.os_build)
        template_name = os_attributes[0].cast().template_name

        cluster = self.api.clusters.get(name=self.clusterName)
        if cluster is None:
            message = ("No cluster named {0!r} found when creating server {1}"
                       .format(self.clusterName, server.hostname))
            logger.info(message)
            raise CloudBoltException(message)

        # template = self.api.templates.get(name=template_name)
        # Fix for the ovirt API's bug when dealing with sub-versioned templates
        # This will use the last created version of the given template.
        # If we were using the latest version of the ovirt SDK, we would
        # be using the template sub-version number - written by Adam Byers @
        # Dell 11/13/15 - ZenDesk ticket #2186
        # https://www.pivotaltracker.com/story/show/118569893
        template = None
        currtime = None
        for tmplt in self.api.templates.list():
            if tmplt.name == template_name:
                if not currtime or (tmplt.get_creation_time() > currtime):
                    currtime = tmplt.get_creation_time()
                    template = tmplt
        if template is None:
            message = ("No template named {0!r} found when creating server {1}"
                       .format(template_name, server.hostname))
            logger.info(message)
            raise CloudBoltException(message)

        try:
            cpu_topology = ovirtsdk.xml.params.CpuTopology(
                cores=1,
                sockets=server.cpu_cnt,
            )
            temp = dict(
                name=server.get_vm_name(),
                cpu=ovirtsdk.xml.params.CPU(topology=cpu_topology),
                memory=server.mem_size * ONE_GIG,
                display=ovirtsdk.xml.params.Display(type_="spice"),
                cluster=cluster,
                template=template,
            )
            logger.info("sending: {0}".format(temp))
            params = ovirtsdk.xml.params.VM(**temp)
            new_vm = self.api.vms.add(vm=params)
            uuid = new_vm.id
            logger.info("new vm uuid: {0}".format(uuid))

            server.resource_handler_svr_id = uuid
            server.save()
        except ovirtsdk.infrastructure.errors.RequestError as e:
            message = ("Create resource response for server {0}: {1}"
                       .format(server.hostname, e.detail))
            logger.info(message)
            raise CloudBoltException(message)

        # Used to return "this is a fake task id" which shows up on the job
        # detail page. The string is found no where else in the code base,
        # instead we will use the empty string
        return ""

    def delete_resource(self, resource_id):
        """
        Delete the VM specified by resource_id

        Return FalseWithMessage on failure/warning with msg set to the reason
        Return TrueWithMessage on success
        """
        server = Server.objects.get(id=resource_id)
        if not server.resource_handler_svr_id:
            # in the case where prov failed badly, we need to avoid throwing an
            # exception so that the server record can still be deleted from C2
            message = ("Could not delete server {0}: no "
                       "resource_handler_svr_id set".format(server.hostname))
            logger.info(message)
            return FalseWithMessage(message)

        if not self.poweroff_resource(resource_id):
            message = "Unable to power down host."
            return FalseWithMessage(message)

        try:
            vm = self.api.vms.get(id=server.resource_handler_svr_id)
            vm.delete()

        except ovirtsdk.infrastructure.errors.RequestError as e:
            message = "Delete response for server {0}: {1}".format(
                server.hostname, e.detail)
            logger.info(message)
            return FalseWithMessage(message)

        return TrueWithMessage("Deleted")

    def get_uuid(self, resource_id):
        """Retrieve the UUID of the given VM"""
        server = Server.objects.get(id=resource_id)
        return server.resource_handler_svr_id

    def is_task_complete(self, resource_id, task_id):
        """
        TODO
        """
        return True, 100

    @staticmethod
    def get_credentials_form():
        """
        TODO
        """
        from .forms import RhevCredentialsForm
        return RhevCredentialsForm

    @staticmethod
    def get_settings_form():
        """
        TODO
        """
        from .forms import RhevSettingsForm
        return RhevSettingsForm

    @staticmethod
    def get_quick_setup_settings_form(quick_setup=False):
        from .forms import RhevQuickSetupSettingsForm
        return RhevQuickSetupSettingsForm

    def get_all_vms(self):
        """
        TODO
        """
        logger.info("Connecting to RHEV to enumerate its VM list.")

        dictify = lambda t: dict(name=t.name, uuid=t.id, description=t.os.type_)

        all_vms = []
        api_vms = self.api.vms.list(query=self.cluster_query)
        from types import NoneType
        logger.info("Found {} VMs ({}).".format(len(api_vms) if type(api_vms) is NoneType else "no", type(api_vms)))
        for vm_obj in api_vms:
            logger.info("+Inspecting VM {} ({}).".format(vm_obj, type(vm_obj)))
            translate_power = dict(up="POWERON", down="POWEROFF")
            power = translate_power.get(vm_obj.status.state, "UNKNOWN")
            logger.info("  Power: {} --> {}".format(vm_obj.status.state, power))

            cpus = vm_obj.cpu.topology.sockets * vm_obj.cpu.topology.cores

            total_disk = sum(disk_obj.size for disk_obj in vm_obj.disks.list())

            all_nics = vm_obj.nics.list()
            primary_mac = all_nics[0].mac.address if all_nics else "NONE"
            # nics = [dict(mac=nic.mac.address, network=nic.network.id)
            #        for nic in all_nics]

            # import here to prevent circular import problem
            from c2_wrapper import guess_os_family
            guess = guess_os_family(dictify(
                self.api.templates.get(id=vm_obj.template.id)))

            vm_dict = dict(hostname=vm_obj.name,
                           mac=primary_mac,
                           uuid=vm_obj.id,
                           os_family=guess,
                           status="ACTIVE",
                           power_status=power,
                           cpu_cnt=int(cpus),
                           disk_size=int(total_disk / ONE_GIG),
                           mem_size=vm_obj.memory / ONE_GIG,
                           # nics=nics,
                           )
            logger.info("  Dict: {}".format(vm_dict))
            all_vms.append(vm_dict)

        return all_vms

    def get_all_networks(self):
        all_nets = []
        net_objs = self.api.clusters.get(name=self.clusterName).networks.list()
        for net_obj in net_objs:
            # We return the "network" value set to the UUID because CB treats
            # the "network" attribute as the unique identifier for the network
            net_dict = dict(name=net_obj.name,
                            network=net_obj.id,
                            uuid=net_obj.id,
                            )
            all_nets.append(net_dict)
        return all_nets

    def add_network(self, **kwargs):
        network, created = RhevNetwork.objects.get_or_create(**kwargs)
        self.networks.add(network)
        return network, created

    def discover_templates(self):
        """
        TODO
        """
        all_templates = self.api.templates.list(query=self.cluster_query)
        dictify = lambda t: dict(name=t.name, uuid=t.id, description=t.os.type_)
        rhevm_templates = [dictify(t) for t in all_templates]
        rhevm_uuids = set(t.id for t in all_templates)

        all_osba = self.os_build_attributes.all()
        cb_uuids = set(osba.uuid for osba in all_osba)

        not_in_cb = [t for t in rhevm_templates if t["uuid"] not in cb_uuids]
        only_in_cb = [osba for osba in all_osba if osba.uuid not in rhevm_uuids]

        return rhevm_templates, not_in_cb, only_in_cb

    def add_template_attrs(self, os_build, template_name, **kwargs):
        """
        Add a RHEV OS build attr, creating it if needed

        Also store the uuid for each template, based on
        what was discovered and returned by discover_templates() (this is
        somewhat unique to RHEV - VMware and some others do not have return a
        UUID for templates).
        """
        osbuild_attribute, created = RhevOSBuildAttribute.objects.get_or_create(
            os_build=os_build, template_name=template_name,
            uuid=kwargs.get("uuid", ""))
        self.os_build_attributes.add(osbuild_attribute)
        return created

    def get_extra_details_tech(self):
        """Return tech-specific details to be shown in RH list view.
        """
        return dict(Cluster=self.clusterName)


RH_CLASS = RhevResourceHandler
