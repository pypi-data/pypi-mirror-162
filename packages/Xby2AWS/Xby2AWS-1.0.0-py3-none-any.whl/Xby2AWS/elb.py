"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import json

class Xby2ELB:

    params = {
        "resource_name": "test-lb"
    }

    def __init__(self, vpc, **kwargs): 
        self.variable_reassignment(**kwargs)
        self.params["subnets"] = vpc.instance.public_subnet_ids
        self.create_elb()

    def variable_reassignment(self, **kwargs):
        for key in kwargs:
            if key in self.params:
                self.params[key] = kwargs[key]
            else:
                print("hey this is probably an issue you should address")

    def create_elb(self):
        # Create an AWS resource (ec2)
        main = aws.lb.LoadBalancer(**self.params)
        write_to = open("manifest.txt", 'a')
        urn = main.urn.apply(
            lambda urn: json.dump({"elb": urn}, write_to)
        )