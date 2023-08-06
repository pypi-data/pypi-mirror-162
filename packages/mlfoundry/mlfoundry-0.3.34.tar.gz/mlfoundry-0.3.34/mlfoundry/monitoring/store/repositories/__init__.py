from mlfoundry.monitoring.store.repositories.rest_monitoring_store import (
    RestMonitoringStore,
)


def get_monitoring_store(host_uri: str):
    # For now we have only one repo
    return RestMonitoringStore(host_uri=host_uri)
