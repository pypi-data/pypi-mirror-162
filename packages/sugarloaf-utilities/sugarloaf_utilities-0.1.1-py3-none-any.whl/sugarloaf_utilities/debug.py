from time import sleep

from click import option, secho
from kubernetes import client


@option("--metric-name", required=True)
def get_external_metric_value(metric_name):
    api = client.CustomObjectsApi()
    resource = api.list_namespaced_custom_object(group="external.metrics.k8s.io", version="v1beta1", namespace="default", plural=metric_name)
    for item in resource["items"]:
        secho(f"Value: {item['value']} - {item['timestamp']}")


@option("--namespace", default="default")
def launch_google_cli_pod(namespace):
    """
    Launch a simple pod with the google cloud CLI pre-installed in order
    to engage with the cluster in a remote shell.

    If you want to test artifact repository permissions, do one of:
    ```
    gcloud auth list
    gcloud auth configure-docker us-central1-docker.pkg.dev
    docker manifest inspect {package}
    ```

    """
    name = "google-cli-pod"
    body = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": name,
        },
        "spec": {
            "containers": [
                {
                    "image": "google/cloud-sdk:latest",
                    "name": name,
                    "command": ["sleep","infinity"]
                }
            ],
            "nodeSelector": {
                "iam.gke.io/gke-metadata-server-enabled": "true"
            }
        }
    }

    api = client.CoreV1Api()
    api.create_namespaced_pod(body=body, namespace=namespace)

    try:
        secho(f"Launched pod.\nAccess with: `kubectl exec -it {name} --namespace {namespace} -- /bin/bash`", fg="green")
        while True:
            sleep(1)
    except KeyboardInterrupt:
        secho("Shutting down gracefully...")

        api.delete_namespaced_pod(
            namespace=namespace,
            name=name,
        )
