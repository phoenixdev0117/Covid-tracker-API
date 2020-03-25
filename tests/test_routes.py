import app
import unittest
from fastapi.testclient import TestClient
import json
from unittest import mock
from app import services
from app.main import APP

from .test_jhu import mocked_requests_get, mocked_strptime_isoformat, DATETIME_STRING

@mock.patch('app.services.location.jhu.datetime')
@mock.patch('app.services.location.jhu.requests.get', side_effect=mocked_requests_get)
class FlaskRoutesTest(unittest.TestCase):
    """
    Need to mock some objects to control testing data locally
    Routes are hard to test regarding singleton app.
    Store all integration testcases in one class to ensure app context
    """

    #load app context only once.
    app = app.create_app()

    def setUp(self):
        self.client = FlaskRoutesTest.app.test_client()
        self.asgi_client = TestClient(APP)
        self.date = DATETIME_STRING

    def read_file_v1(self, state):
        filepath = "tests/expected_output/v1_{state}.json".format(state=state)
        with open(filepath, "r") as file:
            expected_json_output = file.read()
        return expected_json_output

    def test_root_api(self, mock_request_get, mock_datetime):
        """Validate that / returns a 200 and is not a redirect."""
        response = self.asgi_client.get("/")

        assert response.status_code == 200
        assert not response.is_redirect 

    def test_v1_confirmed(self, mock_request_get, mock_datetime):
        mock_datetime.utcnow.return_value.isoformat.return_value = self.date
        mock_datetime.strptime.side_effect = mocked_strptime_isoformat
        state = "confirmed"
        expected_json_output = self.read_file_v1(state=state)
        return_data = self.client.get("/{}".format(state)).data.decode()

        assert return_data == expected_json_output

    def test_v1_deaths(self, mock_request_get, mock_datetime):
        mock_datetime.utcnow.return_value.isoformat.return_value = self.date
        mock_datetime.strptime.side_effect = mocked_strptime_isoformat
        state = "deaths"
        expected_json_output = self.read_file_v1(state=state)
        return_data = self.client.get("/{}".format(state)).data.decode()

        assert return_data == expected_json_output

    def test_v1_recovered(self, mock_request_get, mock_datetime):
        mock_datetime.utcnow.return_value.isoformat.return_value = self.date
        mock_datetime.strptime.side_effect = mocked_strptime_isoformat
        state = "recovered"
        expected_json_output = self.read_file_v1(state=state)
        return_data = self.client.get("/{}".format(state)).data.decode()

        assert return_data == expected_json_output

    def test_v1_all(self, mock_request_get, mock_datetime):
        mock_datetime.utcnow.return_value.isoformat.return_value = self.date
        mock_datetime.strptime.side_effect = mocked_strptime_isoformat
        state = "all"
        expected_json_output = self.read_file_v1(state=state)
        return_data = self.client.get("/{}".format(state)).data.decode()
        #print(return_data)
        assert return_data == expected_json_output

    def test_v2_latest(self, mock_request_get, mock_datetime):
        mock_datetime.utcnow.return_value.isoformat.return_value = DATETIME_STRING
        mock_datetime.strptime.side_effect = mocked_strptime_isoformat
        state = "latest"
        return_data = self.asgi_client.get(f"/v2/{state}").json()

        check_dict = {
            'latest': {
                'confirmed': 1940,
                'deaths': 1940,
                'recovered': 0
            }
        }

        assert return_data == check_dict

    def test_v2_locations(self, mock_request_get, mock_datetime):
        mock_datetime.utcnow.return_value.isoformat.return_value = DATETIME_STRING
        mock_datetime.strptime.side_effect = mocked_strptime_isoformat
        state = "locations"
        return_data = self.asgi_client.get("/v2/{}".format(state)).json()

        filepath = "tests/expected_output/v2_{state}.json".format(state=state)
        with open(filepath, "r") as file:
            expected_json_output = file.read()

        # assert return_data == json.loads(expected_json_output)

    def test_v2_locations_id(self, mock_request_get, mock_datetime):
        mock_datetime.utcnow.return_value.isoformat.return_value = DATETIME_STRING
        mock_datetime.strptime.side_effect = mocked_strptime_isoformat

        state = "locations"
        test_id = 1
        return_data = self.asgi_client.get("/v2/{}/{}".format(state, test_id)).json()

        filepath = "tests/expected_output/v2_{state}_id_{test_id}.json".format(state=state, test_id=test_id)
        with open(filepath, "r") as file:
            expected_json_output = file.read()

        #assert return_data == expected_json_output

    def tearDown(self):
        pass


@pytest.mark.parametrize(
    "query_params",
    [
        {"source": "csbs"},
        {"source": "jhu"},
        {"timelines": True},
        {"timelines": "true"},
        {"source": "jhu", "timelines": True},
    ],
)
def test_locations_status_code(api_client, query_params):
    response = api_client.get("/v2/locations", params=query_params)
    print(f"GET {response.url}\n{response}")
    assert response.status_code == 200
