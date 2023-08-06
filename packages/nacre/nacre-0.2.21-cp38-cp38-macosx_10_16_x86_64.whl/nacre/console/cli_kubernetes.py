import importlib
import os
import sys
from typing import Dict, List

import fire
import yaml
from nautilus_trader.live.node import TradingNode

from nacre.config.nodes import TradingNodeConfig


def run():
    fire.Fire(run_live_node)


def run_live_node(config: str):
    with open(config, "r") as stream:
        node_cfg = yaml.safe_load(stream)

    # Insert search path
    insert_path(node_cfg.pop("paths", None))

    # Insert actors
    insert_actors(node_cfg)

    # Insert API KEY/SECRET
    insert_credential(node_cfg)

    cfg = TradingNodeConfig.parse_obj(node_cfg)
    node = TradingNode(cfg)

    # Insert Data/Exec factories
    insert_factories(node, node_cfg)

    node.build()
    try:
        node.start()
    finally:
        node.dispose()


def insert_actors(node_cfg):
    actors = build_auxiliary_actors()
    if "actors" in node_cfg:
        node_cfg["actors"].extend(actors)
    else:
        node_cfg["actors"] = actors


# Load api key/secret from ENV variable from API_KEY_{venue}_{id}
# eg: API_KEY_BINANCE_001, API_SECRET_BINANCE_001
def insert_credential(node_cfg):
    for id, item in node_cfg["exec_clients"].items():
        if "-" not in id:
            continue
        venue, _, account_id = id.partition("-")
        api_key = os.getenv(f"API_KEY_{venue.upper()}_{account_id.upper()}")
        api_secret = os.getenv(f"API_SECRET_{venue.upper()}_{account_id.upper()}")

        if "api_key" not in item["config"] and api_key is not None:
            node_cfg["exec_clients"][id]["config"]["api_key"] = api_key
            node_cfg["data_clients"][venue]["config"]["api_key"] = api_key
        if "api_secret" not in item["config"] and api_secret is not None:
            node_cfg["exec_clients"][id]["config"]["api_secret"] = api_secret
            node_cfg["data_clients"][venue]["config"]["api_secret"] = api_secret


def insert_factories(node, node_cfg):
    for venue, item in node_cfg["data_clients"].items():
        node.add_data_client_factory(venue, _import_cls(item["factory_path"]))
    for id, item in node_cfg["exec_clients"].items():
        if "-" in id:
            id = id.split("-")[0]
        node.add_exec_client_factory(id, _import_cls(item["factory_path"]))


def insert_path(paths) -> None:
    if paths and isinstance(paths, list):
        for path in paths:
            sys.path.insert(0, path)


def build_auxiliary_actors() -> List[Dict]:
    actors = []
    exposer_port = os.getenv("METRICS_PORT")
    if exposer_port:
        actors.append(
            {
                "actor_path": "nacre.actors.exposer:Exposer",
                "config_path": "nacre.config.actors:ExposerConfig",
                "config": {
                    "host": "0.0.0.0",  # noqa: S104
                    "port": exposer_port,
                },
            }
        )

    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    schema_registry = os.getenv("SCHEMA_REGISTRY")
    if kafka_bootstrap_servers and schema_registry:
        topic_filters = os.getenv("TOPIC_FILTERS")
        if topic_filters is None:
            filters = ["events.snapshot*"]
        else:
            filters = topic_filters.split(",")

        actors.append(
            {
                "actor_path": "nacre.infrastructure.kafka:KafkaPubSub",
                "config_path": "nacre.config.actors:KafkaConfig",
                "config": {
                    "bootstrap_servers": kafka_bootstrap_servers,
                    "schema_registry": schema_registry,
                    "topic_filters": filters,
                },
            }
        )

    return actors


def _import_cls(path: str):
    assert path
    assert ":" in path

    module, cls = path.rsplit(":")
    mod = importlib.import_module(module)
    return getattr(mod, cls)


if __name__ == "__main__":
    run()
