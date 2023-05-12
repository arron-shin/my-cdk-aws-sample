#!/usr/bin/env python3
import os
import aws_cdk as cdk

from network.stacks import MyVpcStack, MySecurityGroupStack, MyALBStack

app = cdk.App()
my_vpc_stack = MyVpcStack(app, "MyVpcStack")
my_sg_stack = MySecurityGroupStack(app, "MySecurityGroupStack", vpc=my_vpc_stack.vpc)
MyALBStack(app, "MyALBStack", vpc=my_vpc_stack.vpc, security_group=my_sg_stack.my_alb_sg)

app.synth()
