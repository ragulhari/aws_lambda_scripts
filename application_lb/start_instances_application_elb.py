import boto3
import sys, traceback
from datetime import datetime
from time import sleep

class InstancesTargetGroups:

    def __init__(self, targetGroupArn):
        self.instances = list()
        self.targetGroupArn = targetGroupArn

    def appendInstance(self, instanceId):
        self.instances.append(instanceId)

    def getArn(self):
        return self.targetGroupArn

    def getInstances(self):
        return self.instances


def start_ec2_instances():
    start_time = datetime.now()

    ec2 = boto3.resource('ec2')
    elb = boto3.client('elbv2')
    waiter = boto3.client('ec2').get_waiter('instance_running')

    targetGroups = {}


    try:
        instances = ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]) 

        for instance in instances:
            
            blnHasTagForStart = False
            tempTargetGroupArn = ''

            if instance.tags is not None:
                for tag in instance.tags:

                    if tag['Key'] == 'ScheduledStartStop' and tag['Value'] == 'True':
                        blnHasTagForStart = True

                    if tag['Key'] == 'TargetGroupArn':
                        tempTargetGroupArn = tag['Value']

            if blnHasTagForStart and tempTargetGroupArn != '':

                if tempTargetGroupArn not in targetGroups.keys():
                    targetGroups[tempTargetGroupArn] = InstancesTargetGroups(tempTargetGroupArn)

                targetGroups.get(tempTargetGroupArn).appendInstance(instance.id)

        for _ , tgroup in targetGroups.items():

            tmpInstanceList = tgroup.getInstances()

            print("Starting instances from Target Group: " + tgroup.getArn())
            ec2.instances.filter(InstanceIds=tmpInstanceList).start()

            waiter.wait(InstanceIds=tmpInstanceList)

            for tmpInstance in tmpInstanceList:
                print("Register instance " +tmpInstance + " in ELB " + tgroup.getArn())

                elb.register_targets(
                    TargetGroupArn=tgroup.getArn(),
                    Targets=[
                        {
                            'Id': tmpInstance,
                        }]
                )


                     
    except:
        print("not expected error:", traceback.print_exc())

    end_time = datetime.now()
    took_time = end_time - start_time
    print("Total time of execution: " + str(took_time))

def lambda_handler(event, context):
    print('Starting instances... ')
    start_ec2_instances()
