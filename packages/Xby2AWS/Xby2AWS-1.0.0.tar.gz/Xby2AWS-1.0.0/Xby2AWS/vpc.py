"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
import json
import random


class Xby2VPC:

    params = {
        "cidr_block": "full",
        "az": 2,
        "public_mask": 22,
        "private_mask": 20,
        "private_subnets": 1,
        "public_subnets": 1,
        "nat_gateways": "ONE_PER_AZ",
        "resource_name": "test-vpc"
    }

    def __init__(self, **kwargs): 
        self.variable_reassignment(**kwargs)
        self.instance = self.create_vpc([])

            
    # # giving up on this function for now - perhaps one day it shall be mine.
    # def cidr_dividr(self, availability_zones, private, public, cidr_block): #(dicidr?)
    #     # figure out number of availability zones
    #     addresses_per_az = cidr_block / availability_zones
    #     # iterate through zones, divide up based on public/private percentages
    #     # maybe set it up so it's divided into four azs?? idk i feel like this is dumb
    #     private_blocks = addresses_per_az * private
    #     public_blocks = addresses_per_az * public
    #     #return a list of masks ????

    def variable_reassignment(self, **kwargs):
        for key in kwargs:
            if key in self.params:
                self.params[key] = kwargs[key]
            else:
                print("hey this is probably an issue you should address")
                

    def cidr_selector(self):
        # determine cidr block
        if self.params["cidr_block"] == "partial":
            cidr = "172.31.0.0/16"
        elif self.params["cidr_block"] == "full":
            cidr = "10.0.0.0/16"
        else:
            cidr = "192.168.0.0/16"
        return cidr

    def subnet_specifier(self, subnet_type):
        if subnet_type == "public":
            return awsx.ec2.SubnetSpecArgs(
                name='public' + str(random.random()),
                type=awsx.ec2.SubnetType.PUBLIC,
                cidr_mask=self.params["public_mask"],
            )
        elif subnet_type == "private":
            return awsx.ec2.SubnetSpecArgs(
                name='private' + str(random.random()),
                type=awsx.ec2.SubnetType.PRIVATE,
                cidr_mask=self.params["private_mask"],
            )

    def nat_gateways(self):
        # determine nat gateways; default is one per availability zone
        if self.params["nat_gateways"] == "ONE_PER_AZ":
            return awsx.ec2.NatGatewayConfigurationArgs(strategy=awsx.ec2.NatGatewayStrategy.ONE_PER_AZ)
        elif self.params["nat_gateways"] == "SINGLE":
            return awsx.ec2.NatGatewayConfigurationArgs(strategy=awsx.ec2.NatGatewayStrategy.SINGLE)
        else:
            return awsx.ec2.NatGatewayConfigurationArgs(strategy=awsx.ec2.NatGatewayStrategy.NONE)

    def subnet_specs(self):
        subnet_specs = []
        pub_sub = int(self.params["public_subnets"])
        priv_sub = int(self.params["private_subnets"])
        while pub_sub > 0:
            subnet_specs.append(self.subnet_specifier("public"))
            pub_sub -= 1
        while priv_sub > 0:
            subnet_specs.append(self.subnet_specifier("private"))
            priv_sub -= 1
        return subnet_specs


    def create_vpc(self, security_groups):
        
        finalized_params = {
            "resource_name": self.params["resource_name"],
            "cidr_block": self.cidr_selector(),
            "number_of_availability_zones": self.params["az"],
            "subnet_specs": self.subnet_specs(),
            "nat_gateways": self.nat_gateways()
        }

        # Create an AWS resource (vpc)
        main = awsx.ec2.Vpc(**finalized_params)

        write_to = open("manifest.txt", 'a')
        vpc_id = main.vpc_id.apply(
            lambda vpc_id: json.dump({"vpc": vpc_id}, write_to)
        )

        return main

