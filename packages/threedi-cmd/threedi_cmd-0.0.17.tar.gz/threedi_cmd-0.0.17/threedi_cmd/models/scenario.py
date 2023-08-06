import asyncio
from functools import cached_property
from pathlib import Path
from typing import Dict, List, Any

from threedi_api_client.openapi.models import Simulation
from threedi_api_client.openapi.models import Schematisation
from threedi_api_client.openapi.api import V3Api
from threedi_api_client.openapi.exceptions import ApiException
from threedi_api_client.threedi_api_client import ThreediApiClient

from .base import SimulationWrapper, ModelWrapper, BaseWrapper
from .base import SchematisationWrapper
from threedi_cmd.console import console
from threedi_cmd.websockets.clients import WebsocketClient
from threedi_cmd.commands.settings import WebSocketSettings
from threedi_cmd.errors import LoadScenarioError


class FailedStep(Exception):
    pass


class ResolveError(Exception):
    pass


class Scenario:
    base_object: Any = None
    steps: Any = []

    # Internal instances administration
    _refs: Dict = None

    def __init__(
        self,
        data: Dict,
        threedi_api_client: ThreediApiClient,
        wrappers: List[BaseWrapper],
        websocket_settings: WebSocketSettings,
        base_path: Path = None,
    ):
        self._refs = {}
        self.wrappers = wrappers
        self.websocket_settings = websocket_settings
        self.threedi_api_client = threedi_api_client
        self._base_path = base_path
        scenario = data.get("scenario")
        if not scenario:
            raise LoadScenarioError("Could not load scenario")
        steps_data = scenario.get("steps", [])
        self.create_base_object(scenario)
        self.steps = self.create_steps(steps_data)

    def create_base_object(self, scenario: Dict):
        pass

    @property
    def instance_kwargs(self):
        raise NotImplementedError("Implement in subclass")

    def cleanup(self):
        raise NotImplementedError("Implement in subclass")

    @property
    def websocket_endpoint_uri(self):
        raise NotImplementedError("Implement in subclass")

    @cached_property
    def websocket_client(self):
        return WebsocketClient(settings=self.websocket_settings)

    def create_steps(self, steps_data: List) -> List[ModelWrapper]:
        """:raises ResolveError if the scenario name can not be found in `steps_data`"""
        steps = []
        if steps_data is None:
            return steps

        for item in steps_data:
            key, data = tuple(item.items())[0]
            found = [x for x in self.wrappers if x.scenario_name == key]

            if not found:
                raise ResolveError(f"Cannot resolve {key} in self.metas")
            wrapper_class = found[0]

            wrapped_instance = wrapper_class(
                data,
                self.threedi_api_client,
                base_path=self._base_path,
                refs=self._refs,
                **self.instance_kwargs,
            )
            steps.append(wrapped_instance)
        return steps

    async def _run(self):
        from threedi_cmd.models.waitfor import WaitForTimeout

        queue = self.websocket_client.queue
        try:
            # 'Execute' step items
            for i, item in enumerate(self.steps, start=1):
                await item.execute(queue)
        except ApiException as e:
            msg = f":collision: Failed step {i}: {item} due to APIException: {e.body}"
            raise FailedStep(msg)
        except WaitForTimeout as e:
            msg = f" :collision: Failed step {i}: {item} due to WaitForTimeout: {e}"
            raise FailedStep(msg)
        except Exception as e:
            msg = f" :collision: Failed step {i}: {item} due to: {e}"
            raise FailedStep(msg)
        finally:
            # Always try to cleanup the simulation
            self.cleanup()

        # Done, close the websocket connection
        try:
            await self.websocket_client.close()
        except Exception as e:
            console.print(e, style="error")

    async def execute(self):
        # Create base object (Simulation or Schematisation)
        if self.base_object.instance.id is None:
            self.base_object.save()

        listen_task = asyncio.create_task(
            self.websocket_client.listen(self.websocket_endpoint_uri)
        )
        try:
            await asyncio.wait_for(self.websocket_client.is_connected(), timeout=10)
        except asyncio.TimeoutError:
            console.print(
                "Could not establish WebSocket connection within 10 seconds",
                style="error",
            )
            listen_task.cancel()
            await asyncio.gather(listen_task)
            return
        run_task = asyncio.create_task(self._run())

        finished, _ = await asyncio.wait(
            [listen_task, run_task], return_when=asyncio.FIRST_EXCEPTION
        )

        for result in finished:
            if not result:
                continue
            if result.exception():
                raise result.exception()


class SimulationScenario(Scenario):
    base_object: Simulation = None

    @property
    def simulation(self):
        return self.base_object

    def cleanup(self):
        try:
            self.shutdown_simulation()
        except Exception:
            pass

    def create_base_object(self, scenario: Dict):
        simulation_data = scenario.get("simulation")
        if "tags" not in simulation_data:
            simulation_data["tags"] = ["automatic-test"]
        elif "automatic-test" not in simulation_data.get("tags", []):
            simulation_data["tags"].append("automatic-test")

        self.base_object = SimulationWrapper(simulation_data, self.threedi_api_client)

    @property
    def websocket_endpoint_uri(self):
        return (
            f"simulations/{self.simulation.instance.id}/?scenario_test_framework=true"
        )

    @property
    def instance_kwargs(self):
        return {"simulation": self.simulation.instance}

    def shutdown_simulation(self):
        console.print("• Requesting simulation shutdown")
        api: V3Api = self.threedi_api_client

        api.simulations_actions_create(
            self.simulation.instance.id, {"name": "shutdown"}
        )


class SchematisationScenario(Scenario):
    base_object: Schematisation = None

    def cleanup(self):
        pass

    @property
    def schematisation(self):
        return self.base_object

    def create_base_object(self, scenario: Dict):
        schematisation_data = scenario.get("schematisation")
        self.base_object = SchematisationWrapper(
            schematisation_data, self.threedi_api_client
        )

    @property
    def websocket_endpoint_uri(self):
        return f"schematisations/{self.schematisation.instance.id}/?scenario_test_framework=true"

    @property
    def instance_kwargs(self):
        return {"schematisation": self.schematisation.instance}
