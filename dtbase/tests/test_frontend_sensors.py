"""
Test that the DTBase sensors pages load
"""
from urllib.parse import urlencode

import requests_mock
from flask.testing import FlaskClient

MOCK_SENSOR_TYPES = [
    {
        "name": "sensorType1",
        "measures": [
            {"name": "Temperature", "units": "degrees C", "datatype": "float"},
            {"name": "Humidity", "units": "percent", "datatype": "float"},
        ],
    }
]

MOCK_SENSORS = [
    {
        "id": 1,
        "name": "aSensor",
        "sensor_type_name": "sensorType1",
        "unique_identifier": "sensor1",
    },
]

MOCK_SENSOR_READINGS = [
    {"timestamp": "2023-01-01T00:00:00", "value": 23.4},
    {"timestamp": "2023-01-01T00:10:00", "value": 24.5},
    {"timestamp": "2023-01-01T00:20:00", "value": 25.6},
    {"timestamp": "2023-01-01T00:30:00", "value": 26.7},
    {"timestamp": "2023-01-01T00:40:00", "value": 27.8},
]


def test_sensors_timeseries_backend(auth_frontend_client: FlaskClient) -> None:
    with auth_frontend_client as client:
        response = client.get("/sensors/time-series-plots", follow_redirects=True)
        assert response.status_code == 200
        html_content = response.data.decode("utf-8")
        assert "Choose sensors and time period" in html_content


def test_sensors_timeseries_no_sensor_types_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get("http://localhost:5000/sensor/list-sensor-types", json=[])
            response = client.get("/sensors/time-series-plots")
            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            assert "Choose sensors and time period" in html_content


def test_sensors_timeseries_dummy_sensor_types_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get(
                "http://localhost:5000/sensor/list-sensor-types",
                json=[{"name": "dummyType1"}, {"name": "dummyType2"}],
            )
            # also mock the responses to getting the sensors of each type
            m.get("http://localhost:5000/sensor/list-sensors", json=[])
            response = client.get("/sensors/time-series-plots")
            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            assert 'value="dummyType1"' in html_content
            assert 'value="dummyType2"' in html_content


def test_sensors_timeseries_no_sensor_data_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get(
                "http://localhost:5000/sensor/list-sensor-types",
                json=[{"name": "sensorType1"}],
            )
            # also mock the responses to getting the sensors of each type
            m.get("http://localhost:5000/sensor/list-sensors", json=MOCK_SENSORS)
            response = client.get("/sensors/time-series-plots")
            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            assert 'value="sensor1"' in html_content


def test_sensors_timeseries_with_data_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get(
                "http://localhost:5000/sensor/list-sensor-types", json=MOCK_SENSOR_TYPES
            )
            # also mock the responses to getting the sensors of each type
            m.get("http://localhost:5000/sensor/list-sensors", json=MOCK_SENSORS)
            m.get(
                "http://localhost:5000/sensor/sensor-readings",
                json=MOCK_SENSOR_READINGS,
            )
            # URL will now include startDate, endDate, sensorIds etc
            response = client.get(
                "/sensors/time-series-plots?startDate=2023-01-01&endDate=2023-02-01&sensorIds=sensor1&sensorType=sensorType1"
            )
            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            # check that it draws canvases for the plots
            assert '<canvas id="TemperatureCanvas"></canvas>' in html_content
            assert '<canvas id="HumidityCanvas"></canvas>' in html_content


def test_sensors_readings_backend(auth_frontend_client: FlaskClient) -> None:
    with auth_frontend_client as client:
        response = client.get("/sensors/readings", follow_redirects=True)
        assert response.status_code == 200
        html_content = response.data.decode("utf-8")
        assert "Time period" in html_content


def test_sensors_readings_initial_get_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get("http://localhost:5000/sensor/list-sensor-types", json=[])
            response = client.get("/sensors/readings")
            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            assert "Time period" in html_content


def test_sensors_readings_post_time_period_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get("http://localhost:5000/sensor/list-sensor-types", json=[])
            response = client.post(
                "/sensors/readings",
                data={"startDate": "2023-01-01", "endDate": "2023-02-01"},
            )
            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            assert "Sensor Type" in html_content


def test_sensors_readings_post_sensor_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get(
                "http://localhost:5000/sensor/list-sensor-types", json=MOCK_SENSOR_TYPES
            )
            m.get("http://localhost:5000/sensor/list-sensors", json=MOCK_SENSORS)
            m.get(
                "http://localhost:5000/sensor/sensor-readings",
                json=MOCK_SENSOR_READINGS,
            )
            response = client.post(
                "/sensors/readings",
                data={
                    "startDate": "2023-01-01",
                    "endDate": "2023-02-01",
                    "sensor_type": "sensorType1",
                    "sensor": "sensor1",
                },
            )
            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            assert "Uploaded sensorType1 Sensor Data for sensor1" in html_content
            # column headings for Timestamp and each measure
            assert "<th>Timestamp</th>" in html_content
            assert "<th>Temperature</th>" in html_content
            assert "<th>Humidity</th>" in html_content
            # 5 rows of data plus the header row
            assert html_content.count("<tr>") == 6


def test_add_sensor_type_backend(auth_frontend_client: FlaskClient) -> None:
    with auth_frontend_client as client:
        response = client.get("/sensors/add-sensor-type", follow_redirects=True)
        assert response.status_code == 200
        html_content = response.data.decode("utf-8")
        assert "Enter New Sensor Type" in html_content


def test_add_sensor_type_no_existing_measures_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get("http://localhost:5000/sensor/list-measures", json=[])
            response = client.get("/sensors/add-sensor-type")
            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            assert "Enter New Sensor Type" in html_content
            assert "SensorType Name:" in html_content
            assert "Description" in html_content
            assert "Select existing measure" in html_content


def test_add_sensor_type_submit_empty_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get("http://localhost:5000/sensor/list-measures", json=[])
            m.get("http://localhost:5000/sensor/list-sensor-types", json=[])
            m.post("http://localhost:5000/sensor/insert-sensor-type", json=[])
            response = client.post("/sensors/add-sensor-type", data={})
            with client.session_transaction() as session:
                flash_message = dict(session["_flashes"])
            assert response.status_code == 302
            assert (
                flash_message["error"]
                == "An error occurred while adding the sensor type: <Response [200]>"
            )


def test_add_sensor_type_submit_duplicate_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get("http://localhost:5000/sensor/list-measures", json=[])
            m.get(
                "http://localhost:5000/sensor/list-sensor-types",
                json=[{"name": "testname"}],
            )
            m.post(
                "http://localhost:5000/sensor/insert-sensor-type",
                json=[],
            )
            response = client.post(
                "/sensors/add-sensor-type",
                data={
                    "name": "testname",
                    "description": "nothing",
                    "measure_name[]": "x",
                    "measure_units[]": "m",
                    "measure_datatype[]": "float",
                },
            )

            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            assert "The sensor type &#39;testname&#39; already exists" in html_content


def test_add_sensor_type_submit_ok_mock(mock_auth_frontend_client: FlaskClient) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get("http://localhost:5000/sensor/list-measures", json=[])
            m.get("http://localhost:5000/sensor/list-sensor-types", json=[])
            m.post(
                "http://localhost:5000/sensor/insert-sensor-type",
                json=[],
                status_code=201,
            )
            client.post(
                "/sensors/add-sensor-type",
                data={
                    "name": "testname",
                    "description": "nothing",
                    "measure_name[]": "x",
                    "measure_units[]": "m",
                    "measure_datatype[]": "float",
                },
            )
            with client.session_transaction() as session:
                flash_message = dict(session["_flashes"])
                print(f"FLASH MESSAGE {flash_message}")
                assert flash_message["success"] == "Sensor type added successfully"


def test_add_sensor_backend(auth_frontend_client: FlaskClient) -> None:
    with auth_frontend_client as client:
        response = client.get("/sensors/add-sensor", follow_redirects=True)
        assert response.status_code == 200
        html_content = response.data.decode("utf-8")
        assert "Add New Sensor" in html_content


def test_add_sensor_no_sensor_types_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get("http://localhost:5000/sensor/list-sensor-types", json=[])
            response = client.get("/sensors/add-sensor", follow_redirects=True)
            html_content = response.data.decode("utf-8")
            assert "Add New Sensor" in html_content


def test_add_sensor_ok_mock(mock_auth_frontend_client: FlaskClient) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get(
                "http://localhost:5000/sensor/list-sensor-types",
                json=[{"name": "testtype"}],
            )
            m.get("http://localhost:5000/sensor/list-sensors", json=[])
            m.post("http://localhost:5000/sensor/insert-sensor", status_code=201)
            client.post(
                "/sensors/add-sensor",
                data={
                    "name": "testsensor",
                    "unique_identifier": "testsensor1",
                    "sensor_type": "testtype",
                    "notes": "humm",
                },
            )
            with client.session_transaction() as session:
                flash_message = dict(session["_flashes"])
                assert flash_message["success"] == "Sensor added successfully"


def test_sensor_list_backend(auth_frontend_client: FlaskClient) -> None:
    with auth_frontend_client as client:
        response = client.get("/sensors/sensor-list", follow_redirects=True)
        assert response.status_code == 200
        html_content = response.data.decode("utf-8")
        assert "Select a sensor type" in html_content


def test_sensor_list_no_sensor_types_mock(
    mock_auth_frontend_client: FlaskClient,
) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get("http://localhost:5000/sensor/list-sensor-types", json=[])
            response = client.get("/sensors/sensor-list", follow_redirects=True)
            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            assert "Select a sensor type" in html_content


def test_sensor_list_ok_mock(mock_auth_frontend_client: FlaskClient) -> None:
    with mock_auth_frontend_client as client:
        with requests_mock.Mocker() as m:
            m.get("http://localhost:5000/sensor/list-sensor-types", json=[])
            m.get(
                "http://localhost:5000/sensor/list-sensors",
                json=[
                    {
                        "name": "sensor1",
                        "notes": "",
                        "sensor_type": "testtype",
                        "unique_identifier": "sensor1",
                    },
                    {
                        "name": "sensor2",
                        "notes": "some notes",
                        "sensor_type": "testtype",
                        "unique_identifier": "sensor2",
                    },
                ],
            )
            response = client.get("/sensors/sensor-list", follow_redirects=True)
            assert response.status_code == 200
            html_content = response.data.decode("utf-8")
            assert '<div id="sensorTableWrapper"></div>' in html_content


def test_edit_sensor_backend(auth_frontend_client: FlaskClient) -> None:
    with auth_frontend_client as client:
        query_args = {
            "name": "Name",
            "notes": "Notes",
            "sensor_type_id": "1",
            "sensor_type_name": "Sensor type",
            "unique_identifier": "Unique identifier",
        }
        url = "/sensors/sensor-edit-form?" + urlencode(query_args)
        response = client.get(url, follow_redirects=True)
        assert response.status_code == 200
        html_content = response.data.decode("utf-8")
        for key, value in query_args.items():
            assert f"{key}: {value}" in html_content
        for test_string in (
            "Edit Sensor",
            ">Submit</button>",
            ">Cancel</button>",
            ">Delete</button>",
        ):
            assert test_string in html_content
