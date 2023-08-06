"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import json

class Xby2RDS:

    params = {
        "instance_class": "db.t4g.micro",
        "allocated_storage": 8,
        "engine": "PostgreSQL",
        "password": "password",
        "username": "username",
        "resource_name": "test-rds"
    }

    def __init__(self, vpc, **kwargs): 
        self.variable_reassignment(**kwargs)
        self.params["db_subnet_group_name"] = vpc.instance.private_subnet_ids.apply(lambda id: id[0])
        self.create_rds()

    def variable_reassignment(self, **kwargs):
        for key in kwargs:
            if key in self.params:
                self.params[key] = kwargs[key]
            else:
                print("hey this is probably an issue you should address")

    def create_rds(self):
        # Create an AWS resource (rds)
        # main = aws.rds.Instance(resource_name=self.params["resource_name"], db_subnet_group_name=vpc.instance.private_subnet_ids.apply(lambda id: id[0]), instance_class=self.params["rds_instance_class"], allocated_storage=self.params["allocated_storage"], engine=self.params["engine"], username=self.params["username"], password=self.params["password"])
        main = aws.rds.Instance(**self.params)
        write_to = open("manifest.txt", 'a')
        arn = main.arn.apply(
            lambda arn: json.dump({"rds": arn}, write_to)
        )