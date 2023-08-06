from .base import SimulationChildWrapper
from threedi_api_client.openapi.models import Action
from .waitfor import WaitForStatusWrapper, WaitForTimeWrapper

from rich.live import Live

from threedi_cmd.console import console


class ActionWrapper(SimulationChildWrapper):
    model = Action
    api_path: str = "actions"
    scenario_name = "action"

    def create(self):
        with Live(console=console) as live:
            live.update(f"Creating {self.model.__name__}...")
            func = getattr(self.api, f"{self.base_path}{self.api_path}_create")

            data = self.instance.to_dict()
            data = {key: item for key, item in data.items() if item is not None}

            res = func(self.simulation.id, data)
            live.update(
                f":heavy_check_mark: [bold spring_green4] Created {self.model.__name__}"
            )
        console.print(self._data)
        return res

    @property
    def extra_steps(self):
        extra_steps = []
        name = self.instance.name
        if name == "initialize":
            data = {"name": "initialized", "paused": True}
        elif name == "start":
            data = {"name": "initialized", "paused": False}
        elif name == "pause":
            data = {"name": "initialized", "paused": True}
        elif name == "shutdown":
            data = {"name": "finished"}
        elif name == "queue":
            msg = "'queue' step is not yet implemented"
            raise NotImplementedError(msg)
        else:
            msg = f"Unknown name {name}"
            raise ValueError(msg)

        extra = {}
        if "waitfor_timeout" in self._data:
            extra["timeout"] = self._data["waitfor_timeout"]

        wait_for_status = WaitForStatusWrapper(
            data={**data, **extra},
            api_client=self._api_client,
            simulation=self.simulation,
        )
        extra_steps.append(wait_for_status)

        if self.instance.duration is not None:
            extra_steps.append(
                WaitForStatusWrapper(
                    data={"name": "initialized", "paused": True, **extra},
                    api_client=self._api_client,
                    simulation=self.simulation,
                )
            )
            extra_steps.append(
                WaitForTimeWrapper(
                    data={"time": self.instance.duration, **extra},
                    api_client=self._api_client,
                    simulation=self.simulation,
                )
            )
        return extra_steps
