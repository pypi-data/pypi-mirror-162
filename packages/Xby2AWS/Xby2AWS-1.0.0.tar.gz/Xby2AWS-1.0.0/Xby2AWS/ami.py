"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import json

class Xby2AMI:

    params = {
        "most_recent": True,
        "owners": ["amazon"],
        "filter_params": [
            {"name": "description", "values": ["Amazon Linux 2 *"]}
        ]
    }

    def __init__(self, **kwargs):
        self.variable_reassignment(**kwargs)
        self.params["filters"] = self.create_filters()
        self.params.pop("filter_params") 
        self.ami = self.create_ami()

    def variable_reassignment(self, **kwargs):
        for key in kwargs:
            if key in self.params:
                self.params[key] = kwargs[key]
            else:
                print("hey this is probably an issue you should address")

    def create_filters(self):
        filters = []
        for filter in self.params["filter_params"]:
            filters.append(aws.ec2.GetAmiFilterArgs(name=filter["name"], values=filter["values"]))
        return filters

    def create_ami(self):
        # Create an AWS resource (ami)
        main = aws.ec2.get_ami(**self.params)
        return main