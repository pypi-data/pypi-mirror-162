# coding=utf-8
# *** WARNING: this file was generated by pulumi-gen-eks. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

from . import _utilities
import typing
# Export this package's modules as members:
from .cluster import *
from .cluster_creation_role_provider import *
from .managed_node_group import *
from .node_group import *
from .node_group_security_group import *
from .provider import *
from .vpc_cni import *
from ._inputs import *
from . import outputs
_utilities.register(
    resource_modules="""
[
 {
  "pkg": "eks",
  "mod": "index",
  "fqn": "pulumi_eks",
  "classes": {
   "eks:index:Cluster": "Cluster",
   "eks:index:ClusterCreationRoleProvider": "ClusterCreationRoleProvider",
   "eks:index:ManagedNodeGroup": "ManagedNodeGroup",
   "eks:index:NodeGroup": "NodeGroup",
   "eks:index:NodeGroupSecurityGroup": "NodeGroupSecurityGroup",
   "eks:index:VpcCni": "VpcCni"
  }
 }
]
""",
    resource_packages="""
[
 {
  "pkg": "eks",
  "token": "pulumi:providers:eks",
  "fqn": "pulumi_eks",
  "class": "Provider"
 }
]
"""
)
