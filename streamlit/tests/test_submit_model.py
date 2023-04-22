from datetime import datetime
import pytest
from pages import submit_model
from hsclient import HydroShare
import json
from pathlib import Path
import tempfile


@pytest.fixture
def submitted_data():
    return {
        "SubmittedName": "Molly Model",
        "SubmittedEmail": "molly@awesome.com",
        "IsVerified": "False",
        "OriginalDev": "Yes",
        "ModelYear": 1990,
        "DataAvail": "Report/paper only",
        "SameCountry": "Yes",
        "ModelCountry": "Germany",
        "ModelAuthors": ["Peter Test", "Tom Harald"],
        "DevEmail": "pert@test.de",
        "ModelReview": "Peer review journal",
        "Cite": "10.1002/2013WR014988",
        "ModelScale": "Continental",  # TODO test with slider -> int value
        "Lat": "0",  # TODO test with different formats of lat and lon
        "Lon": "0",
        "Layers": "6-10 layers",
        "Depth": 100,
        "ModelTime": datetime(1970, 1, 1, 9, 30),
        "ModelCode": "MODFLOW",
        "ModelPurpose": "groundwater resources",
        "ModelEval": "dynamic water levels",
        "ModelAddtional": "The developer is a really cool guy.",
        "ModelGeo": "Unconsolidated sediments",
        "GeoAvail": "Yes",
        "TimeToFillOut": "1-5 Minutes",
        "Additonal": "This project is awesome!"
    }


@pytest.fixture
def login_hydroshare():
    main_path = Path("..")
    f = open(main_path.joinpath('config.json'))
    config = json.load(f)
    hs = HydroShare(username=config["hydroshare"]["username"], password=config["hydroshare"]["password"])

    new_resource = hs.create()
    resIdentifier = new_resource.resource_id
    return new_resource, hs


def test_check_requirements_success(submitted_data):
    s, l = submit_model.check_requirements(submitted_data)
    assert l == []
    assert s == True


def test_check_requirements_fail(submitted_data):
    df = submitted_data

    df["SubmittedName"] = ""
    df["SubmittedEmail"] = "wrong@.de"
    df["ModelCountry"] = ""
    df["ModelAuthors"] = []
    df["DevEmail"] = "@web.de"
    # TODO add doi fail test

    s, l = submit_model.check_requirements(df)
    assert s == False
    assert l == ["SubmittedName", "SubmittedEmail", "ModelCountry", "ModelAuthors", "DevEmail"]


def test_process_data(submitted_data):
    # submit_model.process_data(submitted_data)
    pass


def test_push_to_hydroshare_file_upload(login_hydroshare):
    res, hy = login_hydroshare
    res.file_upload("assets/north_america.shp")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(res.file_download(res.files()[0], save_path=tmp))
        assert path.is_file() == True
    res.delete()


def test_save_uploadedfile():
    pass


def test_send_email_to():
    pass


def test_regex_mail():
    pass


def test_regex_doi():
    pass


def test_regex_isbn():
    pass
