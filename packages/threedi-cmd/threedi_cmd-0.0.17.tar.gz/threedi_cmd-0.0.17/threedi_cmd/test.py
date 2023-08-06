import asyncio
import logging
from uuid import uuid4
from datetime import datetime
from threedi_api_client.threedi_api_client import ThreediApiClient
from threedi_cmd.parser import ScenarioParser

logging.basicConfig(level=logging.INFO)


async def main():
    organisation = "61f5a464c35044c19bc7d4b42d7f58cb"
    threedimodel_id = 14
    simulation_name = "run_" + uuid4().hex

    context = {
        "threedimodel_id": threedimodel_id,
        "organisation_uuid": organisation,
        "simulation_name": simulation_name,
        "datetime_now": datetime.utcnow().isoformat(),
    }

    file_path = "scenarios/livesite_constant_rain_default.yaml"
    file_path = "scenarios/livesite_rain_timeseries.yaml"
    file_path = "scenarios/livesite_lateral.yaml"
    file_path = "scenarios/start_shutdown.yaml"
    # file_path = 'scenarios/start_pause.yaml'

    config = {
        "API_HOST": "http://localhost:8000/v3.0",
        "API_USERNAME": "root",
        "API_PASSWORD": "root2",
    }

    client = ThreediApiClient(config=config)
    parser = ScenarioParser(file_path, context)
    scenario = parser.parse(client)

    # Save simulation before using it in the websocket
    scenario.simulation.save()

    await scenario.execute()


if __name__ == "__main__":
    asyncio.run(main())
