import boto3
import sys, traceback
from datetime import datetime
from time import sleep

def stop_ec2_instances():
    start_time = datetime.now()

    ec2 = boto3.resource('ec2')
    elb = boto3.client('elbv2')

    try:
        instances = ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

        for instance in instances:
            tempInstanceId = ''
            tempTargetGroupArn = ''

            if instance.tags is not None:
                for tag in instance.tags:

                    if tag['Key'] == 'ScheduledStartStop' and tag['Value'] == 'True':
                        tempInstanceId = instance.id
                    if tag['Key'] == 'TargetGroupArn':
                        tempTargetGroupArn = tag['Value']

            if tempInstanceId != '' and tempTargetGroupArn  != '': 


                print("Dettaching instance " + tempInstanceId + " from ELB " + tempTargetGroupArn)

                elb.deregister_targets(
                    TargetGroupArn=tempTargetGroupArn,
                    Targets=[
                        {
                            'Id': str(tempInstanceId)
                        },
                    ]
                )


                print("Stopping instances: " +tempInstanceId)
                ec2.instances.filter(InstanceIds=[tempInstanceId]).stop()

                     
    except:
        print("not expected error:", traceback.print_exc())

    end_time = datetime.now()
    took_time = end_time - start_time
    print("Total time of execution: " + str(took_time))

def lambda_handler(event, context):
    print('Stopping instances... ')
    stop_ec2_instances()
