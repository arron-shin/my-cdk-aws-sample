from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct

class MyVpcStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC with specified CIDR and AZs
        self.vpc = ec2.Vpc(
            self, "my-vpc",
            cidr="10.0.0.0/16",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
            ],
            nat_gateways=1,
        )

class MySecurityGroupStack(Stack):

    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the my-alb-sg security group
        self.my_alb_sg = ec2.SecurityGroup(
            self, 
            "my-alb-sg",
            vpc=vpc,
            security_group_name="my-alb-sg",
            description="Security group for the application load balancer"
        )

        # Add inbound rule to my-alb-sg
        self.my_alb_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow inbound HTTP 80"
        )

        # Create the my-ecs-cluster-sg security group
        self.my_ecs_cluster_sg = ec2.SecurityGroup(
            self, 
            "my-ecs-cluster-sg",
            vpc=vpc,
            security_group_name="my-ecs-cluster-sg",
            description="Security group for the ECS cluster"
        )

        # Add inbound rule to my-ecs-cluster-sg
        self.my_ecs_cluster_sg.add_ingress_rule(
            peer=self.my_alb_sg,
            connection=ec2.Port.all_traffic(),
            description="Allow all traffic from ALB security group"
        )

class MyALBStack(Stack):

    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, security_group: ec2.SecurityGroup, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Select public subnets
        subnet_selection = ec2.SubnetSelection(
            subnets=vpc.public_subnets
        )

        # Create the my-alb load balancer
        my_alb = elbv2.ApplicationLoadBalancer(
            self, 
            "my-alb",
            vpc=vpc,
            security_group=security_group,
            load_balancer_name="my-alb",
            internet_facing=True,
            vpc_subnets=subnet_selection
        )

        # Add a front target group
        front_target_group = elbv2.ApplicationTargetGroup(
            self,
            "front-target-group",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.INSTANCE,
            vpc=vpc,
            target_group_name="front"
        )

        # Add a listener on port 80
        listener = my_alb.add_listener(
            "Listener",
            port=80,
            open=True,
            default_target_groups=[front_target_group]
        )
