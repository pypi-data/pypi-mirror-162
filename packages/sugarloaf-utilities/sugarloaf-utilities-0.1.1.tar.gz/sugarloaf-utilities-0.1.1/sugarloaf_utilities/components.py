from dataclasses import dataclass, field
from typing import List
from graphlib import TopologicalSorter
from uuid import UUID, uuid4


@dataclass
class InfrastructurePackage:
    """
    Defines a terraform package that should be applied at runtime. The dependency_on
    property builds up a dependency graph of dependencies and applies them such to maximize
    parallelism while respecting the order involved. This allows clients to refactor their
    global terraform packages to be more efficient at the package level (isolation of components
    to decrease terrform plan speeds with roundtrip fetch of resource state).

    """
    name: str
    depends_on: List["InfrastructurePackage"] = field(default_factory=list)

    # Internal identifier
    identifier: UUID = field(default_factory=uuid4)


core_infrastructure = InfrastructurePackage(
    name="core-infrastructure",
)

core_definitions = InfrastructurePackage(
    name="core-definitions",
    depends_on=[core_infrastructure],
)

app_monitoring = InfrastructurePackage(
    name="app-monitoring",
    depends_on=[core_definitions],
)

app_setup = InfrastructurePackage(
    name="app-setup",
    depends_on=[
        # relies on service monitoring definitions to be completed
        core_definitions,
        # relies on the monitoring namespace to already be setup
        app_monitoring
    ],
)

def get_ordered_packages() -> List[InfrastructurePackage]:
    """
    Resolves the DAG Dependency by sniffing the global space for InfrastructurePackages instances.
    This avoids us having to specify a primary list of the packages.

    """
    packages = [item for item in globals().values() if isinstance(item, InfrastructurePackage)]
    package_by_id = {
        package.identifier: package
        for package in packages
    }

    edges = {
        package.identifier: [dependency.identifier for dependency in package.depends_on]
        for package in packages
    }

    sorted = TopologicalSorter(edges)
    return [
        package_by_id[identifier]
        for identifier in sorted.static_order()
    ]
