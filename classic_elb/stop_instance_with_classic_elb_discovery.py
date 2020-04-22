import boto3
import sys, traceback
from datetime import datetime
from time import sleep

def stop_ec2_instances():
    start_time = datetime.now()

    ec2 = boto3.resource('ec2')

    elb = boto3.client('elb')
    lbs = elb.describe_load_balancers()

    try:
        instances = ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]) 

        instanceIds = list()
 
        for instance in instances:
            if instance.tags is not None:
                for tag in instance.tags:
                    if tag['Key'] == 'ScheduledStartStop' and tag['Value'] == 'True':
                        instanceIds.append(instance.id)
                        for lb in lbs['LoadBalancerDescriptions']:
                            lb_name = str(lb['LoadBalancerName'])
                            for lb_instance in lb['Instances']:
                                if lb_instance["InstanceId"] == instance.id:

                                    print("Dettaching instance " + str(instance.id) + " from ELB " + lb_name)

                                    elb.deregister_instances_from_load_balancer(
                                        LoadBalancerName=lb_name,
                                        Instances=[
                                            {
                                                'InstanceId': str(instance.id)
                                            },
                                        ]
                                    )
                          
        if len(instanceIds) > 0 : 
            print("Stopping instances: " + str(instanceIds))
            ec2.instances.filter(InstanceIds=instanceIds).stop()
                     
    except:
        print("not expected error:", traceback.print_exc())

    end_time = datetime.now()
    took_time = end_time - start_time
    print("Total time of execution: " + str(took_time))

def lambda_handler(event, context):
    print('Stopping instances... ')
    stop_ec2_instances()
