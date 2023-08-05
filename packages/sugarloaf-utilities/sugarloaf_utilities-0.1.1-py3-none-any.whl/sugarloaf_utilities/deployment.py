from dataclasses import dataclass, replace, field
from re import match
from time import sleep, time
from typing import List, Optional

from click import option, secho
from kubernetes import client


class DeploymentError(Exception):
    pass


@dataclass
class ParsedDockerImage:
    """
    Component of a docker image URL. There are a few different forms that these
    URLs can take:
    - postgres:latest
    - postgres
    - docker.pkg.dev/postgres:latest

    """
    image: str

    repository: Optional[str] = None
    tag: Optional[str] = None

    @classmethod
    def from_url(cls, url):
        # optional parse repository, force parse image, optional tag
        parsed_image = match(r"(.*\/)?([a-zA-Z0-9-]*)(:[a-zA-Z0-9-]+)?", url)
        repository = parsed_image.group(1)
        tag = parsed_image.group(3)

        return cls(
            repository=repository.strip("/") if repository else None,
            image=parsed_image.group(2),
            tag=tag.strip(":") if tag else None,
        )

    @property
    def url(self):
        """
        Return the full docker image URL
        """
        url = ""
        url += f"{self.repository}/" if self.repository else ""
        url += self.image
        url += f":{self.tag}" if self.tag else ""
        return url


@dataclass
class UpdatedPod:
    name: str
    ready: bool = False


@dataclass
class UpdatedDeployment:
    """
    Capture the metadata around a deployment that was updated as part
    of this revision process

    """
    namespace: str
    name: str
    # `app` label used by pods to group themselves
    app_name: str
    # index of the previously/currently deployed replicaset
    previous_revision: int
    current_revision: int
    # the replica name that backs the current revision
    current_replica_name: str
    current_pods: Optional[List[UpdatedPod]] = None

    @property
    def is_stabilized(self) -> bool:
        """
        :param: true if all pod deployments have stabilized

        """
        # Client callers have not yet populated the pods, therefore we don't
        # know whether we have a stable deployment
        if self.current_pods is None:
            return False
        if not self.current_pods:
            return True
        return all(pod.ready for pod in self.current_pods)


REVERSION_KEY = "deployment.kubernetes.io/revision"
CHANGE_CAUSE_KEY = "kubernetes.io/change-cause"


class DeploymentManager:
    def __init__(self, stabilization_limit: int):
        self.apps_api = client.AppsV1Api()
        self.core_api = client.CoreV1Api()
        self.stabilization_limit = stabilization_limit

    def __call__(self, image: str, new_sha: str, commit_description: Optional[str] = None):
        updated_deployments = self.update_deployments_with_image(image=image, new_sha=new_sha, commit_description=commit_description)
        failed_stabilization = self.get_failed_stabilization(updated_deployments)

        if not failed_stabilization:
            secho("All deployments succeeded", fg="green")
            return

        # Now rollback the changes that didn't succeed
        secho("Will rollback changes", fg="red")
        self.rollback_deployments(failed_stabilization)
        secho("Rollback complete", fg="green")

        # Report failure at the CI level
        raise DeploymentError()

    def update_deployments_with_image(self, image, new_sha, commit_description) -> List[UpdatedDeployment]:
        """
        Update deployments that reference the given image - updating the sha and pushing
        a new revision into the cluster.

        """
        result = self.apps_api.list_deployment_for_all_namespaces()

        updated_deployments: List[UpdatedDeployment] = []

        for item in result.items:
            for container in item.spec.template.spec.containers:
                parsed = ParsedDockerImage.from_url(container.image)
                if parsed.image != image:
                    continue

                previous_revision = int(item.metadata.annotations.get(REVERSION_KEY))
                app_name = item.spec.template.metadata.labels.get("app")

                secho(f"Updating {item.metadata.name}", fg="yellow")

                new_image = replace(parsed, tag=new_sha)
                container.image = new_image.url

                # Limit the current git commit description to the first 200 chars to make it more readable in
                # the change logs
                if commit_description:
                    item.metadata.annotations[CHANGE_CAUSE_KEY] = self.get_trimmed_string(commit_description, 200)

                # kubernetes.io/change-cause=
                self.apps_api.patch_namespaced_deployment(
                    name=item.metadata.name,
                    namespace=item.metadata.namespace,
                    body=item,
                )

                # get the latest revision
                deployment = self.apps_api.read_namespaced_deployment(item.metadata.name, item.metadata.namespace)
                current_revision = int(deployment.metadata.annotations.get(REVERSION_KEY))

                # If it's the same as the previous one, we didn't actually update anything
                # (which is unusual but we should handle this case gracefully)
                if previous_revision == current_revision:
                    secho(f"Revisions equal for `{item.metadata.name}` - skipping stabilization check", fg="yellow")
                    continue

                new_deployed_replica = self.get_replica_for_revision(app_name, current_revision)
                new_replica_name = new_deployed_replica.metadata.name

                updated_deployments.append(
                    UpdatedDeployment(
                        namespace=item.metadata.namespace,
                        name=item.metadata.name,
                        app_name=app_name,
                        previous_revision=previous_revision,
                        current_revision=current_revision,
                        current_replica_name=new_replica_name,
                    )
                )

        return updated_deployments

    def get_failed_stabilization(self, updated_deployments):
        """
        :returns deployments that could not reach a healthy state:
        """
        start_timer = time()

        while (
            pending_stabilization := [
                deployment
                for deployment in updated_deployments
                if not deployment.is_stabilized
            ]
        ):
            if time() - start_timer > self.stabilization_limit:
                formatted_failures = "\n".join([f"- {current_deployment.name} [{current_deployment.current_pods}]" for current_deployment in pending_stabilization])
                secho(f"Failed to stabilize deployments:\n{formatted_failures}", fg="red")
                break

            for updated_deployment in pending_stabilization:
                updated_deployment.current_pods = []

                pods = self.core_api.list_namespaced_pod(
                    namespace=updated_deployment.namespace,
                    label_selector=f"app={updated_deployment.app_name}"
                )
                for pod in pods.items:
                    is_new_replica = any(
                        [
                            owner.name == updated_deployment.current_replica_name
                            for owner in pod.metadata.owner_references
                        ]
                    )

                    # This pod is part of the new rollout group, which we care about monitoring
                    # for stability. Get the current status.
                    if is_new_replica:
                        is_ready = all([
                            status.ready for status in (pod.status.container_statuses or [])
                        ])
                        updated_deployment.current_pods.append(
                            UpdatedPod(
                                name=pod.metadata.name,
                                ready=is_ready,
                            )
                        )

                # If all are ready we are stable
                if updated_deployment.is_stabilized:
                    secho(f"Deployment has stabilized: `{updated_deployment.name}`", fg="green")

            sleep(1)

        return pending_stabilization

    def rollback_deployments(self, rollback_deployments):
        for updated_deployment in rollback_deployments:
            deployment = self.apps_api.read_namespaced_deployment(updated_deployment.name, updated_deployment.namespace)
            matching_set = self.get_replica_for_revision(updated_deployment.app_name, updated_deployment.previous_revision)

            # Update the spec
            deployment.spec.template = matching_set.spec.template

            secho(f"Bumping revision `{updated_deployment.namespace}/{updated_deployment.name}`: {updated_deployment.current_revision} -> {updated_deployment.current_revision+1}", fg="yellow")
            self.apps_api.patch_namespaced_deployment(
                name=updated_deployment.name,
                namespace=updated_deployment.namespace,
                body=client.V1Deployment(
                    spec=deployment.spec,
                    metadata=client.V1ObjectMeta(
                        annotations={REVERSION_KEY: str(updated_deployment.current_revision+1)}
                    )
                ),
            )

    def get_replica_for_revision(self, app_name: str, revision: int):
        """
        Return the replicaset definition for a given app revision
        """
        replica_sets = self.apps_api.list_replica_set_for_all_namespaces(
            label_selector=f"app={app_name}",
        )

        # Find the one that was present right before our upgrade
        matching_set = [
            replica_set
            for replica_set in replica_sets.items
            if int(replica_set.metadata.annotations.get(REVERSION_KEY)) == int(revision)
        ]

        if not matching_set:
            raise ValueError("No matching revision")

        return matching_set[0]

    @staticmethod
    def get_trimmed_string(string, max_length):
        if len(string) > max_length:
            return string[:max_length] + "..."
        return string


@option("--image", required=True)
@option("--new-sha", required=True)
@option("--commit-description")
@option("--stabilization-limit", default=30)
def update_image(image, new_sha, commit_description, stabilization_limit):
    """
    Scans through currently deployed definitions and determines which ones contain
    references to the `image` artifact and therefore need to be updated with the
    given sha.

    :param stabilization_limit: The seconds to wait for the deployment health to stabilize

    """
    manager = DeploymentManager(stabilization_limit)
    manager(image, new_sha, commit_description)
