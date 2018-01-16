from __future__ import division

import os
import time

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from common.classes import TrueWithMessage, FalseWithMessage
from externalcontent.models import OSBuildAttribute
from infrastructure.models import Server, ServerNetworkCard
from resourcehandlers.models import ResourceHandler, ResourceNetwork
from settings import VARDIR
from utilities.exceptions import CloudBoltException
from utilities.logger import ThreadLogger

import ovirtsdk4 as sdk
import ovirtsdk4.types as types

logger = ThreadLogger(__name__)

ONE_GIG = 2 ** 30


class RhevNetwork(ResourceNetwork):
    """
    Represents a RHEV network, extending the base ResourceNetwork class
    """
    uuid = models.CharField(max_length=36, default="")


@python_2_unicode_compatible
class RhevOSBuildAttribute(OSBuildAttribute):
    """
    Extends the base OSBuildAttribute class to represent the details of
    templates in RHEV
    """
    template_name = models.CharField(max_length=100)
    uuid = models.CharField(max_length=100)

    def get_resource_handler(self):
        return self.rhevresourcehandler_set.first()

    def __str__(self):
        return self.template_name

    class Meta(OSBuildAttribute.Meta):
        verbose_name = "RHEV OS Build Attribute"


class RhevResourceHandler(ResourceHandler):
    """
    This class extends the ResourceHandler class to include
    elements specific to RHEV's Cloud Platform
    """
    cert_directory = os.path.join(VARDIR, "opt/cloudbolt/rhev")

    clusterName = models.CharField(max_length=100, default="")
    can_sync_vms = True
    networks = models.ManyToManyField(RhevNetwork, blank=True)
    os_build_attributes = models.ManyToManyField(RhevOSBuildAttribute, blank=True)
    type_name = "RHEV"

    _api = []

    @property
    def api(self):
        # Immediately return the cached API instance if it exists
        if self._api:
            return self._api[0]

        api_kwargs = {
            'url': self.get_api_url(self.protocol, self.ip, self.port),
            'username': self.serviceaccount,
            'password': self.servicepasswd,
            'ca_file': self.get_cert_filename(self.ip, self.port),
        }

        """
        Skip SSL cert validation if global SSL verification is disabled
        """
        should_verify_ssl = bool(self.get_ssl_verification())
        if should_verify_ssl is False:
            api_kwargs['validate_cert_chain'] = False

        api = sdk.Connection(**api_kwargs)
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

    def verify_connection(self):
        """
        Raise an exception if connection was NOT successful.
        """
        # This method is required on all RHs.  Currently this does nothing to verify the
        # credentials or connetion to RHEV; however, forms.RhevCredentialsForm does.

    def poweron_resource(self, resource_id, pxe=None):
        """
        Powers on the server specified by resource_id
        """
        server = Server.objects.get(id=resource_id)
        try:
            vm = self.api.vms_service(id=server.resource_handler_svr_id)
            vm.start()
        except Error as e:
            message = "Power on response for server {0}: {1}"
            logger.info(message.format(resource_id, e.detail))
            return False
        return True

    def poweroff_resource(self, resource_id):
        """
        Powers off the server specified by resource_id
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

        except sdk.Error as e:
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
        Adds NICs to the server specified by resource_id.

        `delete_first`: Indicates that any NICs already associated with the
        server should be removed before new ones are added
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
                    except sdk.Error as e:
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
                    # if not nic_obj:
                    #     params = types.HostNic(
                    #         name=nic_name,
                    #         interface="virtio",
                    #         network=cluster_obj.networks.get(id=network.uuid),
                    #         mac=types.MAC(mac) if mac else None,
                    #     )
                    #     nic_obj = vm_obj.nics.add(params)
                    # else:
                    #     net_obj = cluster_obj.networks.get(id=network.uuid),
                    #     nic_obj.set_network(net_obj)
                    # mac = nic_obj.mac.address
                    break
                    # TODO: fix this with types.NicConfiguration?
                except sdk.Error as e:
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
        Provisions a new VM using the information provided by the server
        specified by resource_id
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
            cpu_topology = types.CpuTopology(
                cores=1,
                sockets=server.cpu_cnt,
            )
            temp = dict(
                name=server.get_vm_name(),
                cpu=types.CPU(topology=cpu_topology),
                memory=server.mem_size * ONE_GIG,
                display=types.Display(type_="spice"),
                cluster=cluster,
                template=template,
            )
            logger.info("sending: {0}".format(temp))
            params = types.VM(**temp)
            new_vm = self.api.vms.add(vm=params)
            uuid = new_vm.id
            logger.info("new vm uuid: {0}".format(uuid))

            server.resource_handler_svr_id = uuid
            server.save()
        except sdk.Error as e:
            message = ("Create resource response for server {0}: {1}"
                       .format(server.hostname, e.detail))
            logger.info(message)
            raise CloudBoltException(message)

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
            # exception so that the server record can still be deleted from CB
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

        except sdk.Error as e:
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
        TODO: Implement a more sophisticated method for determining task
        progress
        """
        return True, 100

    @staticmethod
    def get_credentials_form():
        """
        Return the RHEV-specific credentials form
        """
        from .forms import RhevCredentialsForm
        return RhevCredentialsForm

    @staticmethod
    def get_settings_form():
        """
        Return the RHEV-specific settings form
        """
        from .forms import RhevSettingsForm
        return RhevSettingsForm

    @staticmethod
    def get_quick_setup_settings_form(quick_setup=False):
        """
        Return the RHEV-specific Quick Setup form
        """
        from .forms import RhevQuickSetupSettingsForm
        return RhevQuickSetupSettingsForm

    def get_all_vms(self):
        """
        Queries RHEV for all its VMs and imports them into CloudBolt
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
        """
        Queries RHEV for all its networks so they can be imported into CloudBolt
        """
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
        """
        Adds a RhevNetwork to this RH, creating it if needed.
        """
        network, created = RhevNetwork.objects.get_or_create(**kwargs)
        self.networks.add(network)
        return network, created

    def discover_templates(self):
        """
        Finds the set of templates for the resource handler, for use in places
        like the Import templates button

        Returns a 3-tuple:
            rhevm_templates[{}]    a list of dictionaries representing the
            RHEV-specific template details for each template
            not_in_cb[{}]       a list of templates that don't exist in CB
            only_in_cb[osba]    a list of OSBuildAttributes that exist in CB but
            no longer have equivalent templates on RHEV
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
