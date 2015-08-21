import sys
import time

from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build


# list instances
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items']


# create instance
def create_instance(compute, project, zone, name, package):
    source_disk_image = \
        "projects/debian-cloud/global/images/debian-7-wheezy-v20150320"
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    startup_script = open('startup-script.sh', 'r').read()


    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        'tags': {
            'items': [
                'http-server'
            ]
        },

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],



        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }, {
                'key': 'url',
                'value': 'image'#image_url
            }, {
                'key': 'package',
                'value': package
            }, {
                # Every project has a default Cloud Storage bucket that's
                # the same name as the project.
                'key': 'bucket',
                'value': project
            }]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()


# delete_instance
def delete_instance(compute, project, zone, name):
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()


# wait_for_operation
def wait_for_operation(compute, project, zone, operation):
    sys.stdout.write('Waiting for operation to finish')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print "done."
            if 'error' in result:
                raise Exception(result['error'])
            return result
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)



# START run
def run(project, zone, instance_name, package):
    credentials = GoogleCredentials.get_application_default()
    compute = build('compute', 'v1', credentials=credentials)

    print 'Creating instance.'

    #creating instance
    operation = create_instance(compute, project, zone, instance_name, package)

    #execute operations
    wait_for_operation(compute, project, zone, operation['name'])

    #listing instances
    instances = list_instances(compute, project, zone)

    print 'Instances in project %s and zone %s:' % (project, zone)
    for instance in instances:
        print ' - ' + instance['name']

    print """ Instance created """

    raw_input()

    print 'Deleting instance.'

    operation = delete_instance(compute, project, zone, instance_name)
    wait_for_operation(compute, project, zone, operation['name'])



def main():
    project = raw_input('project ID? ')
    zone = raw_input('zone? [us-central1-a] ') or 'us-central1-a'
    instance_name = 'mobilevm1'
    package = raw_input('paquete a utilizar ')

    run(project, zone, instance_name, package)


if __name__ == '__main__':
    main()