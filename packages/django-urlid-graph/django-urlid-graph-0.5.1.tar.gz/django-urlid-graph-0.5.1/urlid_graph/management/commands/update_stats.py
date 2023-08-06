import pprint

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone

from urlid_graph.log import AsyncLogger, Step
from urlid_graph.models import ElementConfig, Entity


class DataStats:
    def __init__(self):
        graph_django_connection = connections[settings.GRAPH_DATABASE]
        graph_django_connection.connect()
        self.graph_connection = graph_django_connection.connection

        self._total_objects_per_entity = None
        self._total_relationships_per_type = None

    @property
    def total_objects(self):
        return sum(self.total_objects_per_entity.values())

    @property
    def total_objects_per_entity(self):
        if self._total_objects_per_entity is None:
            self._total_objects_per_entity = {}
            for entity in Entity.objects.all():
                Model = entity.get_model()
                if Model is None:
                    continue
                self._total_objects_per_entity[entity.name] = Model.objects.values("object_uuid").distinct().count()

        return self._total_objects_per_entity

    @property
    def total_relationships(self):
        return sum(self.total_relationships_per_type.values())

    @property
    def total_relationships_per_type(self):
        if self._total_relationships_per_type is None:
            with self.graph_connection.cursor() as cursor:
                cursor.execute("MATCH ()-[r]->() RETURN type(r), COUNT(type(r))")
                data = dict(cursor.fetchall())
                self._total_relationships_per_type = {
                    key.replace('"', "").replace("'", ""): int(value) if value else None for key, value in data.items()
                }
        return self._total_relationships_per_type


class CollectStatsLogger(AsyncLogger):
    name = "update stats"
    steps = [
        Step("object-total", "Count total objects"),
        Step("object-entities", "Count total objects per entity"),
        Step("relationship-total", "Count total relationships"),
        Step("relationship-entities", "Count total relationships per entity"),
    ]


class Command(BaseCommand):
    help = "Update general statistics about imported data"

    def handle(self, *args, **options):
        self.logger = CollectStatsLogger(description="collecting statistics from objects and relationships")
        print(f"Starting job {self.logger.job.id}")

        data = {
            "object": {
                "total": None,
                "entities": {},
            },
            "relationship": {
                "total": None,
                "entities": {},
            },
        }
        stats = DataStats()

        self.logger.start_step("object-total")
        data["object"]["total"] = stats.total_objects
        self.logger.finish_step("object-total", message=f"Found {data['object']['total']}")

        self.logger.start_step("object-entities")
        data["object"]["entities"].update(stats.total_objects_per_entity)
        entity_total = [f"{key}: {value}" for key, value in data["object"]["entities"].items()]
        self.logger.finish_step("object-entities", message=f"Found: {', '.join(entity_total)}")

        self.logger.start_step("relationship-total")
        data["relationship"]["total"] = stats.total_relationships
        self.logger.finish_step("relationship-total", message=f"Found {data['relationship']['total']}")

        self.logger.start_step("relationship-entities")
        data["relationship"]["entities"].update(stats.total_relationships_per_type)
        relationship_total = [f"{key}: {value}" for key, value in data["relationship"]["entities"].items()]
        self.logger.finish_step("relationship-entities", message=f"Found: {', '.join(relationship_total)}")

        data["updated_at"] = str(timezone.now())
        pprint.pprint(data)

        ElementConfig.objects.update_or_create(
            config_type=ElementConfig.STATS_CONFIG,
            name="stats",
            parent_type=None,
            parent_name=None,
            defaults={"label": "stats", "data": data},
        )
        self.logger.finish()
