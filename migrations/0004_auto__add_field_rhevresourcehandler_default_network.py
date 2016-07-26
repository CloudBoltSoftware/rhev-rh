# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'RhevResourceHandler.default_network'
        db.add_column('rhev_rhevresourcehandler', 'default_network',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='resource_handlers_using_as_default', null=True, to=orm['rhev.RhevNetwork']),
                      keep_default=False)

        # Adding M2M table for field networks on 'RhevResourceHandler'
        db.create_table('rhev_rhevresourcehandler_networks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rhevresourcehandler', models.ForeignKey(orm['rhev.rhevresourcehandler'], null=False)),
            ('rhevnetwork', models.ForeignKey(orm['rhev.rhevnetwork'], null=False))
        ))
        db.create_unique('rhev_rhevresourcehandler_networks', ['rhevresourcehandler_id', 'rhevnetwork_id'])


    def backwards(self, orm):
        # Deleting field 'RhevResourceHandler.default_network'
        db.delete_column('rhev_rhevresourcehandler', 'default_network_id')

        # Removing M2M table for field networks on 'RhevResourceHandler'
        db.delete_table('rhev_rhevresourcehandler_networks')


    models = {
        'accounts.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
            'allow_auto_approval': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ancestry_string': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'approvers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'approvers'", 'blank': 'True', 'to': "orm['accounts.UserProfile']"}),
            'custom_field_options': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['orders.CustomFieldValue']", 'null': 'True', 'blank': 'True'}),
            'custom_fields': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['infrastructure.CustomField']", 'null': 'True', 'blank': 'True'}),
            'environments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['infrastructure.Environment']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levels_to_show': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Group']", 'null': 'True', 'blank': 'True'}),
            'quota_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quota.ServerQuotaSet']", 'null': 'True'}),
            'requestors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'requestors'", 'blank': 'True', 'to': "orm['accounts.UserProfile']"}),
            'resource_admins': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'resource_admins'", 'blank': 'True', 'to': "orm['accounts.UserProfile']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.GroupType']"}),
            'user_admins': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_admins'", 'blank': 'True', 'to': "orm['accounts.UserProfile']"}),
            'viewers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'viewers'", 'blank': 'True', 'to': "orm['accounts.UserProfile']"})
        },
        'accounts.grouptype': {
            'Meta': {'object_name': 'GroupType'},
            'group_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'accounts.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'environment_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ldap': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['utilities.LDAPUtility']", 'null': 'True', 'blank': 'True'}),
            'server_list_args': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'externalcontent.application': {
            'Meta': {'ordering': "['name']", 'object_name': 'Application'},
            'environments': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'applications'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['infrastructure.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'os_builds': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['externalcontent.OSBuild']", 'null': 'True', 'blank': 'True'})
        },
        'externalcontent.osbuild': {
            'Meta': {'ordering': "['name']", 'object_name': 'OSBuild'},
            'environments': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'os_builds'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['infrastructure.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'os_family': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'os_build_set'", 'null': 'True', 'to': "orm['externalcontent.OSFamily']"}),
            'os_versions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['externalcontent.OSVersion']", 'null': 'True', 'blank': 'True'}),
            'use_handler_template': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'externalcontent.osbuildattribute': {
            'Meta': {'object_name': 'OSBuildAttribute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'os_build': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['externalcontent.OSBuild']"}),
            'real_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'})
        },
        'externalcontent.osfamily': {
            'Meta': {'ordering': "['name']", 'object_name': 'OSFamily'},
            'display_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['externalcontent.OSFamily']"})
        },
        'externalcontent.osversion': {
            'Meta': {'object_name': 'OSVersion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'infrastructure.customfield': {
            'Meta': {'ordering': "['name']", 'object_name': 'CustomField'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hide_single_value': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_on_servers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        'infrastructure.datacenter': {
            'Meta': {'ordering': "('longitude',)", 'object_name': 'DataCenter'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'computed_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'geocode_error': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '55'})
        },
        'infrastructure.environment': {
            'Meta': {'ordering': "['name']", 'object_name': 'Environment'},
            'auto_approval': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'custom_field_options': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['orders.CustomFieldValue']", 'null': 'True', 'blank': 'True'}),
            'custom_fields': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['infrastructure.CustomField']", 'null': 'True', 'blank': 'True'}),
            'data_center': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['infrastructure.DataCenter']", 'null': 'True', 'blank': 'True'}),
            'groups_served': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['accounts.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '55'}),
            'preconfiguration_options': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['orders.PreconfigurationValueSet']", 'null': 'True', 'blank': 'True'}),
            'preconfigurations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['infrastructure.Preconfiguration']", 'null': 'True', 'blank': 'True'}),
            'provision_engine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['provisionengines.ProvisionEngine']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'resource_handler': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resourcehandlers.ResourceHandler']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'resource_pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['infrastructure.ResourcePool']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'infrastructure.preconfiguration': {
            'Meta': {'ordering': "['name']", 'object_name': 'Preconfiguration'},
            'custom_fields': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['infrastructure.CustomField']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_applications': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'include_os_build': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'infrastructure.resourcepool': {
            'Meta': {'ordering': "['name']", 'object_name': 'ResourcePool'},
            'custom_fields': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['infrastructure.CustomField']", 'null': 'True', 'blank': 'True'}),
            'global_scope': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_hostname': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'include_ipaddress': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'include_mac': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': '1', 'blank': '1'})
        },
        'orders.customfieldvalue': {
            'Meta': {'object_name': 'CustomFieldValue'},
            'boolean_value': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'datetime_value': ('django.db.models.fields.DateTimeField', [], {'null': '1', 'blank': '1'}),
            'decimal_value': ('django.db.models.fields.DecimalField', [], {'null': '1', 'max_digits': '15', 'decimal_places': '10', 'blank': '1'}),
            'email_value': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': '1', 'blank': '1'}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['infrastructure.CustomField']"}),
            'file_value': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': '1', 'blank': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'int_value': ('django.db.models.fields.IntegerField', [], {'null': '1', 'blank': '1'}),
            'ip_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': '1', 'blank': '1'}),
            'ldap_value': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['utilities.LDAPUtility']", 'null': 'True', 'blank': 'True'}),
            'network_value': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resourcehandlers.ResourceNetwork']", 'null': '1', 'blank': '1'}),
            'str_value': ('django.db.models.fields.CharField', [], {'max_length': '975', 'null': '1', 'blank': '1'})
        },
        'orders.preconfigurationvalueset': {
            'Meta': {'object_name': 'PreconfigurationValueSet'},
            'applications': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['externalcontent.Application']", 'null': 'True', 'blank': 'True'}),
            'cpu_cnt': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'custom_field_values': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['orders.CustomFieldValue']", 'null': 'True', 'blank': 'True'}),
            'disk_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'mem_size': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '4', 'blank': 'True'}),
            'os_build': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['externalcontent.OSBuild']", 'null': 'True', 'blank': 'True'}),
            'preconfiguration': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['infrastructure.Preconfiguration']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'provisionengines.provisionengine': {
            'Meta': {'object_name': 'ProvisionEngine'},
            'custom_fields': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['infrastructure.CustomField']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'provision_technology': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['provisionengines.ProvisionTechnology']"}),
            'real_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'serviceaccount': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'servicepasswd': ('secrets.fields.EncryptedPasswordField', [], {})
        },
        'provisionengines.provisiontechnology': {
            'Meta': {'object_name': 'ProvisionTechnology'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': '1', 'blank': '1'})
        },
        'quota.quota': {
            'Meta': {'object_name': 'Quota'},
            '_unlimited_descendents': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'available': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '15', 'decimal_places': '10'}),
            'delegated': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '15', 'decimal_places': '10'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quota.Quota']", 'null': 'True', 'blank': 'True'}),
            'total_used': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'used': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'})
        },
        'quota.serverquotaset': {
            'Meta': {'object_name': 'ServerQuotaSet'},
            'cpu_cnt': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['quota.Quota']"}),
            'disk_size': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['quota.Quota']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mem_size': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['quota.Quota']"}),
            'vm_cnt': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['quota.Quota']"})
        },
        'resourcehandlers.resourcehandler': {
            'Meta': {'ordering': "['name']", 'object_name': 'ResourceHandler'},
            'custom_fields': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['infrastructure.CustomField']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'limit_fields': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'limit_fields'", 'symmetrical': 'False', 'through': "orm['resourcehandlers.ResourceLimitItem']", 'to': "orm['infrastructure.CustomField']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '443'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'real_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'resource_technology': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resourcehandlers.ResourceTechnology']"}),
            'serviceaccount': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'servicepasswd': ('secrets.fields.EncryptedPasswordField', [], {})
        },
        'resourcehandlers.resourcelimititem': {
            'Meta': {'unique_together': "(('handler', 'custom_field'),)", 'object_name': 'ResourceLimitItem'},
            'custom_field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['infrastructure.CustomField']"}),
            'handler': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resourcehandlers.ResourceHandler']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum': ('django.db.models.fields.IntegerField', [], {'default': 'None'})
        },
        'resourcehandlers.resourcenetwork': {
            'Meta': {'object_name': 'ResourceNetwork'},
            'addressing_schema': ('django.db.models.fields.CharField', [], {'default': "'dhcp'", 'max_length': '10'}),
            'custom_field_values': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['orders.CustomFieldValue']", 'null': 'True', 'blank': 'True'}),
            'dns1': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'dns2': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'dns_domain': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'netmask': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'real_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'vlan': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'resourcehandlers.resourcetechnology': {
            'Meta': {'object_name': 'ResourceTechnology'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modulename': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'rhev.rhevdisk': {
            'Meta': {'object_name': 'RhevDisk'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'rhev.rhevnetwork': {
            'Meta': {'object_name': 'RhevNetwork', '_ormbases': ['resourcehandlers.ResourceNetwork']},
            'resourcenetwork_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['resourcehandlers.ResourceNetwork']", 'unique': 'True', 'primary_key': 'True'})
        },
        'rhev.rhevosbuildattribute': {
            'Meta': {'object_name': 'RhevOSBuildAttribute', '_ormbases': ['externalcontent.OSBuildAttribute']},
            'osbuildattribute_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['externalcontent.OSBuildAttribute']", 'unique': 'True', 'primary_key': 'True'}),
            'template_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rhev.rhevresourcehandler': {
            'Meta': {'ordering': "['name']", 'object_name': 'RhevResourceHandler', '_ormbases': ['resourcehandlers.ResourceHandler']},
            'default_network': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resource_handlers_using_as_default'", 'null': 'True', 'to': "orm['rhev.RhevNetwork']"}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['rhev.RhevNetwork']", 'null': 'True', 'blank': 'True'}),
            'os_build_attributes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['rhev.RhevOSBuildAttribute']", 'null': 'True', 'blank': 'True'}),
            'resourcehandler_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['resourcehandlers.ResourceHandler']", 'unique': 'True', 'primary_key': 'True'})
        },
        'utilities.ldaputility': {
            'Meta': {'object_name': 'LDAPUtility'},
            'auto_create_user': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'base_dn': ('django.db.models.fields.CharField', [], {'default': "'dc=example,dc=com'", 'max_length': '50'}),
            'disabled_filter': ('django.db.models.fields.CharField', [], {'default': "'userAccountControl:1.2.840.113556.1.4.803:=2'", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'email_format': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ldap_domain': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ldap_filter': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ldap_first': ('django.db.models.fields.CharField', [], {'default': "'givenName'", 'max_length': '50'}),
            'ldap_last': ('django.db.models.fields.CharField', [], {'default': "'sn'", 'max_length': '50'}),
            'ldap_mail': ('django.db.models.fields.CharField', [], {'default': "'mail'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'ldap_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'serviceaccount': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'servicepasswd': ('secrets.fields.EncryptedPasswordField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        }
    }

    complete_apps = ['rhev']