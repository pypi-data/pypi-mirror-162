import yaml
from jinja2 import Environment
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from threedi_api_client.threedi_api_client import ThreediApiClient

from threedi_cmd.models import WRAPPERS
from threedi_cmd.models.scenario import (
    Scenario,
    SimulationScenario,
    SchematisationScenario,
)
from threedi_cmd.commands.settings import WebSocketSettings


class ScenarioParser:
    """
    Parses a YAML file into a Scenario object
    """

    _simulation_scenario = None
    _data = None

    def __init__(self, filepath: str):
        """
        :param filepath: The filepath to the YAML file
        :param context: The context to use for rendering the YAML (Jinja2) file
        """
        self.filepath = Path(filepath)

    def load(self):
        if self._data is None:
            with open(self.filepath.as_posix()) as f:
                self._data = f.read()
        return self._data

    def _render_template(self, context: Dict) -> str:
        """
        Render the template using the given context
        """
        # Inject default params
        context.update(
            {
                "simulation_name": "run_" + uuid4().hex,
                "schematisation_name": "schematisation_" + uuid4().hex,
                "datetime_now": datetime.utcnow().isoformat(),
            }
        )
        data = self.load()

        env = Environment(extensions=["threedi_cmd.jinja2_time.TimeExtension"])
        env.datetime_format = "%Y-%m-%dT%H:%M:%S"
        return yaml.load(env.from_string(data).render(context), Loader=yaml.FullLoader)

    @property
    def is_simulation_scenario(self):
        if self._simulation_scenario is None:
            data = yaml.load(self.load(), Loader=yaml.FullLoader)
            self._simulation_scenario = (
                "schematisation" not in data.get("scenario", {}).keys()
            )
        return self._simulation_scenario

    def parse(
        self,
        threedi_api_client: ThreediApiClient,
        websocket_settings: WebSocketSettings,
        base_path: Optional[Path] = None,
        context: Dict = None,
    ) -> Scenario:
        """
        Parse the YAML file.

        :param threedi_api_client: Injected into the Scenario,
                                   allowing to execute API calls.

        :returns: Scenario instance
        """
        if context is None:
            context = {}

        data = self._render_template(context)

        scenario_klass = SimulationScenario
        if not self.is_simulation_scenario:
            scenario_klass = SchematisationScenario

        return scenario_klass(
            data=data,
            threedi_api_client=threedi_api_client,
            wrappers=WRAPPERS,
            websocket_settings=websocket_settings,
            base_path=base_path,
        )
