from click import group
from kubernetes import config

from sugarloaf_utilities.debug import get_external_metric_value, launch_google_cli_pod
from sugarloaf_utilities.deployment import update_image
from sugarloaf_utilities.terraform import chain_apply, chain_destroy


config.load_kube_config()

@group()
def main():
    pass

main.command()(update_image)
main.command()(get_external_metric_value)
main.command()(launch_google_cli_pod)
main.command("apply")(chain_apply)
main.command("destroy")(chain_destroy)
