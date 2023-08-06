import pulumi
import pulumi_aws as aws

class Xby2SecurityGroup:

    params = {
        "protocol": "tcp",
        "i_from_port": "0",
        "i_to_port": "65535",
        "e_from_port": "0",
        "e_to_port": "65535",
        "i_cidr": "10.0.0.0/16",
        "e_cidr": "10.0.0.0/16",
        "resource_name": "test-sec-group"
    }

    finalized_params = {}

    def __init__(self, vpc, **kwargs): 
        self.variable_reassignment(**kwargs)
        self.finalized_params["resource_name"] = self.params["resource_name"]
        self.finalized_params["ingress"] = self.create_ingress_rule()
        self.finalized_params["egress"] = self.create_egress_rule()
        self.finalized_params["vpc_id"] = vpc.instance.vpc_id
        self.create_security_group()

    def variable_reassignment(self, **kwargs):
        for key in kwargs:
            if key in self.params:
                self.params[key] = kwargs[key]
            else:
                print("hey this is probably an issue you should address")

    def create_security_group(self):
        return aws.ec2.SecurityGroup(**self.finalized_params)

    def create_ingress_rule(self):
        # do i need to include cidr block???
        return [{'protocol': self.params["protocol"], 'from_port': self.params["i_from_port"], 'to_port': self.params["i_to_port"], 'cidr_blocks': [self.params["i_cidr"]]}]

    def create_egress_rule(self):
        # do i need to include cidr block???
        return [{'protocol': self.params["protocol"], 'from_port': self.params["e_from_port"], 'to_port': self.params["e_to_port"], 'cidr_blocks': [self.params["e_cidr"]]}]