from kubernetes import client, config
namespace = "test-dev001"

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config('./kube-config')

v1 = client.CoreV1Api()

# create K8s namespace 
ret = v1.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace)))
print("create K8s namespace :"+namespace)

# create K8s service account 
ret = v1.create_namespaced_service_account("account",client.V1ServiceAccount(metadata=client.V1ObjectMeta(name="dev001")))
print("create K8s service account 'dev001'")

# delete K8s service account 
# delete_namespaced_service_account("ServerAccount","Namespace")
ret = v1.delete_namespaced_service_account("dev001","account")
print("delete K8s namespace 'account' / service account 'dev001'")

# create K8s ResourceQuota
resource_quota = client.V1ResourceQuota(
       spec= client.V1ResourceQuotaSpec(
           hard={"cpu": "10", "memory": "10G", "pods":"20", "persistentvolumeclaims": "0", "resourcequotas": "10", "configmaps": "10", "secrets": "10", "services.nodeports": "10"}))
resource_quota.metadata = client.V1ObjectMeta(namespace=namespace,name="user-quota")
ret = v1.create_namespaced_resource_quota(namespace, resource_quota)
print("create ResourceQuota ")

# get Quota
resource_quota = v1.read_namespaced_resource_quota("user-quota",namespace)
# Update Quota
resource_quota.spec.hard['cpu'] = 20
# replace_namespaced_resource_quota(name, namespace, body)
ret = v1.replace_namespaced_resource_quota("user-quota", namespace, resource_quota)
get_quota = v1.read_namespaced_resource_quota("user-quota",namespace)
print("%s\t%s\t%s" % (get_quota.metadata.namespace, get_quota.metadata.name, get_quota.spec))

# create ns Role
rules = [client.V1PolicyRule(["*"], resources=["*"], verbs=["*"], )]
role = client.V1Role(rules=rules)
role.metadata = client.V1ObjectMeta(namespace = namespace, name = "user-role")
rbac = client.RbacAuthorizationV1Api()
rbac.create_namespaced_role(namespace,role)
print("Create Role : " + namespace + "/user-role")

# delete NS Role
rbac.delete_namespaced_role("user-role", namespace)
print("Delete Role : " + namespace + "/user-role")

# create ns RoleBinding
role_binding = client.V1RoleBinding(
        metadata=client.V1ObjectMeta(namespace=namespace,name="dev-role-binding"),
        subjects=[client.V1Subject(namespace="account", name="dev", kind="ServiceAccount")],
        role_ref=client.V1RoleRef(kind="Role", api_group="rbac.authorization.k8s.io", name="user-role",))
rbac = client.RbacAuthorizationV1Api()
rbac.create_namespaced_role_binding(namespace=namespace,body=role_binding)
print("Create RoleBinding : " + namespace + "/dev-role-binding Role : user-role")

# delete NS RoleBinding
rbac.delete_namespaced_role_binding("dev-role-binding", namespace)
print("Delete RoleBinding : " + namespace + "/dev-role-binding Role : user-role")

# delete K8s namespace
ret = v1.delete_namespace(namespace)
print("delete K8s namespace "+namespace)
