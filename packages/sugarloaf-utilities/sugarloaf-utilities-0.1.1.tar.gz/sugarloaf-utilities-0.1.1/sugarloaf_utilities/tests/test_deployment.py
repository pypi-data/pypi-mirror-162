from re import M
from unittest.mock import patch

import pytest
from kubernetes import client

from sugarloaf_utilities.deployment import REVERSION_KEY, DeploymentError, DeploymentManager

class GenerationUtilities:
    def __init__(
        self,
        app_name: str,
        image_name: str,
        container_name: str,
    ):
        self.app_name = app_name
        self.image_name = image_name
        self.container_name = container_name

    def generate_pod_template(self):
        return client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={
                    "app": self.app_name,
                }
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name=self.container_name,
                        image=self.image_name,
                    )
                ]
            )
        )

    def generate_deployment_spec(self, revision: int):
        return client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name="test-deplyoment",
                namespace="default",
                annotations={
                    REVERSION_KEY: str(revision),
                }
            ),
            spec=client.V1DeploymentSpec(
                template=self.generate_pod_template(),
                selector=client.V1LabelSelector(
                    match_labels={
                        "app": self.app_name,
                    }
                )
            )
        )

    def generate_replica_spec(self, replica_set_name: str, revision: int):
        return client.V1ReplicaSet(
            metadata=client.V1ObjectMeta(
                name=replica_set_name,
                annotations={
                    REVERSION_KEY: str(revision),
                }
            ),
            spec=client.V1ReplicaSetSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={
                        "app": self.app_name,
                    }
                ),
                template=self.generate_pod_template(),
            )
        )

    def generate_pod_spec(self, owner_name: str, ready: bool):
        return client.V1Pod(
            metadata=client.V1ObjectMeta(
                name="test-pod",
                namespace="default",
                labels={
                    "app": self.app_name,
                },
                owner_references=[
                    client.V1OwnerReference(
                        api_version="apps/v1",
                        kind="ReplicaSet",
                        name=owner_name,
                        uid=f"{owner_name}-uid",
                    )
                ]
            ),
            status=client.V1PodStatus(
                container_statuses=[
                    client.V1ContainerStatus(
                        name=self.container_name,
                        ready=ready,
                        image=self.image_name,
                        image_id=f"{self.image_name}-id",
                        restart_count=0,
                    )
                ]
            )
        )

def test_clean_deploy():
    """
    Deploy new payload and pods become healthy immediatey
    """
    manager = DeploymentManager(5)

    image_name="test-image"
    replica_set_name = "test-replica-set"
    spec_generator = GenerationUtilities(
        app_name="test-app",
        image_name=image_name,
        container_name="test-container",
    )

    with (
        patch.object(manager.apps_api, "list_deployment_for_all_namespaces") as list_deployment_mock,
        patch.object(manager.apps_api, "patch_namespaced_deployment") as patch_deployment_mock,
        patch.object(manager.apps_api, "read_namespaced_deployment") as read_namespaced_deployment_mock,
        patch.object(manager.apps_api, "list_replica_set_for_all_namespaces") as list_replica_set_for_all_namespaces_mock,
        patch.object(manager.core_api, "list_namespaced_pod") as list_namespaced_pod_mock,
    ):
        # List an instance of the deployment that has our container image included
        list_deployment_mock.return_value = client.V1DeploymentList(
            items=[
                spec_generator.generate_deployment_spec(revision=1),
            ]
        )

        # No-op for the patch deployment itself
        patch_deployment_mock.return_value = dict()

        # After deploy, should bump the revision number
        read_namespaced_deployment_mock.return_value = spec_generator.generate_deployment_spec(revision=2)

        # Find the replica set that backs the new deployment
        list_replica_set_for_all_namespaces_mock.return_value = client.V1ReplicaSetList(
            items=[
                spec_generator.generate_replica_spec(replica_set_name, revision=2),
            ]
        )

        # Pods are ready immediately
        list_namespaced_pod_mock.return_value = client.V1PodList(
            items=[
                spec_generator.generate_pod_spec(replica_set_name, ready=True),
            ]
        )

        manager(image_name, "new-tag")

def test_erroring_deploy():
    """
    Deploy new payload and pods stay unhealthy
    """
    manager = DeploymentManager(5)

    image_name="test-image"
    replica_set_name = "test-replica-set"
    spec_generator = GenerationUtilities(
        app_name="test-app",
        image_name=image_name,
        container_name="test-container",
    )

    with (
        patch.object(manager.apps_api, "list_deployment_for_all_namespaces") as list_deployment_mock,
        patch.object(manager.apps_api, "patch_namespaced_deployment") as patch_deployment_mock,
        patch.object(manager.apps_api, "read_namespaced_deployment") as read_namespaced_deployment_mock,
        patch.object(manager.apps_api, "list_replica_set_for_all_namespaces") as list_replica_set_for_all_namespaces_mock,
        patch.object(manager.core_api, "list_namespaced_pod") as list_namespaced_pod_mock,
    ):
        # List an instance of the deployment that has our container image included
        list_deployment_mock.return_value = client.V1DeploymentList(
            items=[
                spec_generator.generate_deployment_spec(revision=1),
            ]
        )

        # No-op for the patch deployment itself
        patch_deployment_mock.return_value = dict()

        # After deploy, should bump the revision number
        read_namespaced_deployment_mock.return_value = spec_generator.generate_deployment_spec(revision=2)

        # Find the replica set that backs both deployments, since we'll have to revert
        # to the old spec
        list_replica_set_for_all_namespaces_mock.return_value = client.V1ReplicaSetList(
            items=[
                spec_generator.generate_replica_spec(replica_set_name, revision=1),
                spec_generator.generate_replica_spec(replica_set_name, revision=2),
            ]
        )

        # Pods are ready immediately
        list_namespaced_pod_mock.return_value = client.V1PodList(
            items=[
                spec_generator.generate_pod_spec(replica_set_name, ready=False),
            ]
        )

        with pytest.raises(DeploymentError):
            manager(image_name, "new-tag")
