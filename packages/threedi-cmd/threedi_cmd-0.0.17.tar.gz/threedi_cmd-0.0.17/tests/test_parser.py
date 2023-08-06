
from uuid import uuid4
from datetime import datetime
from threedi_api_client.api import ThreediApi
from threedi_cmd.parser import ScenarioParser


def test_parser():
    # Note: smoke test parser (including jinja2-time template rendering)
    organisation = "61f5a464c35044c19bc7d4b42d7f58cb"
    threedimodel_id = 14
    simulation_name = "run_" + uuid4().hex

    context = {
        "threedimodel_id": threedimodel_id,
        "organisation_uuid": organisation,
        "simulation_name": simulation_name,
        "datetime_now": datetime.utcnow().isoformat(),
    }

    file_path = "threedi_cmd/test_data/start_shutdown.yaml"

    config = {
        "THREEDI_API_HOST": "http://localhost:8000/",
        "THREEDI_API_USERNAME": "root",
        "THREEDI_API_PASSWORD": "notused",
    }

    client = ThreediApi(config=config)
    parser = ScenarioParser(file_path)
    parser.parse(client, None, "scenarios/", context)
