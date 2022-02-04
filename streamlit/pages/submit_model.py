import streamlit as st
import streamlit_tags as stt
import streamlit.components.v1 as components

import re
from datetime import datetime, timezone
from utils import helpers as hp
from pathlib import Path
import platform
from hsclient import HydroShare
from hsmodels.schemas.fields import Creator
import json

# from https://stackabuse.com/python-validate-email-address-with-regular-expressions-regex/
regex_mail = re.compile(
    r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
regex_doi = re.compile(
    r"/^10.\d{4,9}/[-._;()/:A-Z0-9]+$/i")  # thanks to https://www.crossref.org/blog/dois-and-matching-regular-expressions/
regex_isbn = re.compile(r"/^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$/")


def send_email_to(name, info):
    pass


def save_uploadedfile(uploadedfile):
    path = main_path.joinpath("tempDir")
    try:
        path.mkdir(parents=True)
    except OSError:
        pass
    file_p = path.joinpath(uploadedfile.name)
    with open(file_p, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return str(file_p)


def check_requirements(df):
    '''
    This is a dict of requirement checks for each field.
    They are automatically applied to all fields in the form.
    We can assume that streamlit is only providing strings back in textfield
    cases so e just have to check if they are not empty or malformed.

    Return value is True if check is passed.
    '''

    def is_valid_string(x):
        return not len(x) == 0 and not x.isspace()

    def is_valid_mail(email):
        if re.fullmatch(regex_mail, email):
            return True
        else:
            return False

    def is_valid_ref(x):
        if re.fullmatch(regex_doi, x):
            return True
        elif re.fullmatch(regex_isbn, x):
            return True
        else:
            return False

    def is_valid_lat(x):
        return True

    def is_valid_lon(x):
        return True

    reqs = {
        "SubmittedName": (lambda x: is_valid_string(x)),
        "SubmittedEmail": (lambda x: is_valid_mail(x)),
        "ModelCountry": (lambda x: is_valid_string(x)),
        "ModelAuthors": (lambda x: not len(x) == 0),  # assumes that author list can't be empty
        "DevEmail": (lambda x: is_valid_mail(x)),
        # "Cite": (lambda x: is_valid_ref(x)), # FIXME currently this regex is not working
        "Lat": (lambda x: is_valid_lat(x)),
        "Lon": (lambda x: is_valid_lon(x))
    }
    failed = []
    for var, fun in reqs.items():
        if not fun(df[var]):
            failed.append(var)
    return len(failed) == 0, failed


def push_to_hydroshare(data):
    '''
    Authenticate with the hydroshare services to store data.
    Limitations
    1: Currently through username and password
    -> should be exchanged by token based access.
    2: Hydroshare does not support to access collection at this time.
    -> we store all resources in a group without using collections.
    '''
    # TODO the configuration should be read in in a central place and also contain other settings
    f = open(main_path.joinpath('config.json'))
    config = json.load(f)
    # TODO can we avoid login in again every time?
    hs = HydroShare(username=config["hydroshare"]["username"], password=config["hydroshare"]["password"])

    new_resource = hs.create()
    resIdentifier = new_resource.resource_id
    new_resource.metadata.title = data["SubmittedName"]
    # email=data["SubmittedEmail"]
    new_resource.metadata.creators.append(Creator(name=data["SubmittedName"]))

    new_resource.file_upload(data["files"][0])

    for file in data["files"]:
        p = Path(file)
        if p.is_file():
            new_resource.file_upload(file)
        else:
            st.error("Something went wrong caching the uploaded file: {}".format(p))

    # We could unpack this automatically but this provides an easy possibility to rename fields
    # Also all fields in the metadata need to be strings
    new_resource.metadata.additional_metadata = {
        "IsVerified": "False",
        "OriginalDev": data["OriginalDev"],
        "ModelYear": str(data["ModelYear"]),
        "DataAvail": data["DataAvail"],
        "SameCountry": data["SameCountry"],
        "ModelCountry": data["ModelCountry"],
        "ModelAuthors": ' '.join(data["ModelAuthors"]),
        "DevEmail": data["DevEmail"],
        "ModelReview": data["ModelReview"],
        "Cite": data["Cite"],
        "ModelScale": data["ModelScale"],
        "Lat": data["Lat"],
        "Lon": data["Lon"],
        "Layers": data["Layers"],
        "Depth": data["Depth"],
        "ModelTime": str(data["ModelTime"]),
        "ModelCode": data["ModelCode"],
        "ModelPurpose": data["ModelPurpose"],
        "ModelEval": data["ModelEval"],
        "ModelAddtional": data["ModelAddtional"],
        "ModelGeo": data["ModelGeo"],
        "GeoAvail": data["GeoAvail"],
        "TimeToFillOut": data["TimeToFillOut"],
        "Additonal": data["Additonal"]
    }
    new_resource.save()


def process_data(data: dict):
    '''
    Processes the input data for review, storage and email etc.
    This is a callback from the submit button of the form
    '''

    passed, loffields = check_requirements(data)

    if not passed:
        st.warning("The following fields contain malformed data: {}".format(loffields))
        return

    # FIXME ST spinner seems to be budy at the moment possibly this needs to be executed in a different task threat
    with st.spinner('Data is being processed ...'):
        push_to_hydroshare(data)

    # bring user to the top of the page
    if "counter" not in st.session_state:
        st.session_state.counter = 1
    st.session_state.counter += 1
    st.success('Your data was successfully submitted')

    send_email_to("name of reviewer", "info")
    send_email_to("name of model dev", "info")


# Apparently processor should be empty on streamlit.io
if platform.system() == 'Windows':
    main_path = Path(".")
else:
    main_path = Path("streamlit")


@st.cache
def get_countries():
    with open(main_path.joinpath('utils', 'countries.json'), 'r') as cs:
        country_data = cs.read()
    countries = json.loads(country_data)["countries"]
    l_countries = [d['name'] for d in countries]
    return l_countries


def app():
    if "counter" not in st.session_state:
        st.session_state.counter = 1
    components.html(
        f"""
            <p>{st.session_state.counter}</p>
            <script>
                window.parent.document.querySelector('section.main').scrollTo(0, 0);
            </script>
        """,
        height=0
    )
    markdown = hp.read_markdown_file(str(main_path.joinpath('pages', 'view', 'submit_page.md')))
    st.markdown(markdown, unsafe_allow_html=True)

    m_mark = "<font color='red' font-size='large'>*</font>"
    with st.form(key='my_form'):
        st.markdown("# MANDATORY QUESTIONS(1 - 2 minutes)", unsafe_allow_html=True)
        st.markdown("In case GroMoPo really liked your recipe (or fell ill after eating it!)"
                    " it would like to keep your personal credentials so it can contact you in future,"
                    " and reward frequent contributors.")

        # collect all answers in this dict -> we can easily use this as json to sent it via mail
        data = {}

        t_name = st.text_input("Your name (which may be different than model developer)", "Guy McGuy")
        # Text field to fill in the name – constrain to string datatype only.
        data["SubmittedName"] = t_name

        t_email = st.text_input("Your E-mail *", "mail@mail.com")
        data["SubmittedEmail"] = t_email

        b_dev = st.radio("Are you the original model developer?", ("Yes", "No"))
        data["OriginalDev"] = b_dev

        n_year = st.slider("Model development/publication YEAR *", min_value=datetime(1960, 1, 2, tzinfo=timezone.utc),
                           max_value=datetime(2050, 1, 1, 9, 30, tzinfo=timezone.utc),
                           value=datetime(2020, 1, 2, tzinfo=timezone.utc), format="YYYY")
        data["ModelYear"] = n_year

        t_m_avail = st.selectbox("Model data availability *", ("Report/paper only", "Output publicly available",
                                                               "Input and output publicly available", "Unsure"))
        data["DataAvail"] = t_m_avail

        b_country = st.radio("Is the model developer's institute located in the same country as the model location?  *",
                             ("Yes", "No", "Unclear"))
        data["SameCountry"] = b_country

        l_countries = get_countries()
        t_country = st.selectbox("Country of primary model developer or institution  *", l_countries)
        data["ModelCountry"] = t_country

        l_names = stt.st_tags(
            label='Model developers/authors (e.g.: A. Lastname1 C. Lastname2). Max = 6'
                  ' If there are no personal credentials provided, please fill in the name of the organization that created the model *',
            text='Press enter to add more',
            value=['T. Test'],
            suggestions=['FirstName LastName'],
            maxtags=6,
            key='1')

        data["ModelAuthors"] = l_names

        st.markdown("# Model general information (ADDITIONAL INFORMATION)")
        st.markdown("GroMoPo can already see the ingredients in the shopping bags! "
                    "Now it is curious about some general information such as – how many portions will it eat?"
                    " How old are the ingredients?")

        t_email_dev = st.text_input("Model developer primary email *", "mail@mail.com")
        data["DevEmail"] = t_email_dev

        b_review = st.radio("Model review",
                            ("Double-blind peer review journal",
                             "Peer review journal",
                             "Peer reviewed report (includes internal review at governmental agencies like USGS)",
                             "Not peer reviewed",
                             "Not sure"))
        data["ModelReview"] = b_review

        t_cite = st.text_input("Citation for report, data and/or code (DOI or ISBN). Only one main reference.", "")
        data["Cite"] = t_cite

        uploaded_files = st.file_uploader("Report, data or code files (Max. file-size: 5mb, shapefiles only)",
                                          accept_multiple_files=True, type="shp", key="upload")
        files = []
        if uploaded_files:
            for f in uploaded_files:
                files.append(save_uploadedfile(f))
        data["files"] = files
        # FIXME this is always empty!!!

        scale_r = st.radio("Model Scale", ("Global", "Continental", "other-> select with a slider"))

        n_scale = None
        if scale_r == "other-> select with a slider":
            n_scale = st.slider("Model scale km²", min_value=1, max_value=100000, value=2000, step=100)
        if n_scale is not None:
            data["ModelScale"] = n_scale
        else:
            data["ModelScale"] = scale_r

        st.markdown("Model extent (upload zipfile; optional, don't spend time looking for it if not easily available),"
                    " if model shapefile unavailable please specify the model location as Lat | Lon (e.g., 36.069 ; -94.172),"
                    " ideally center of domain. This can be easily achieved through e.g. google maps where you can right"
                    " click on a point in the map and then click on the coordinates it automatically shows."
                    " Then you can simply copy those in the fields below.")
        t_lat = st.text_input("Lat", "36.069")
        t_lon = st.text_input("Lon", "-94.172")
        data["Lat"] = t_lat
        data["Lon"] = t_lon

        n_layers = st.radio("Model Layers",
                            ("1 layer", "2-5 layers", "6-10 layers", "11-15 layers", "16-20 layers", ">20 layers"))
        data["Layers"] = n_layers

        n_depth = st.number_input("Maximum depth of model below ground surface (m)", min_value=1, max_value=10000)
        data["Depth"] = n_depth

        time_r = st.radio("Is the model only simulating steady state?", ("Yes", "No"))

        n_time = None
        if time_r == "No":
            n_time = st.slider("Model time frame", min_value=datetime(1970, 1, 1, 9, 30),
                               max_value=datetime(2030, 1, 1, 9, 30), value=datetime(2020, 1, 1, 9, 30),
                               format="MM/DD/YY")
        if n_time is not None:
            data["ModelTime"] = n_time
        else:
            data["ModelTime"] = "SS"

        st.markdown("# Model technical information (ADDITIONAL INFORMATION)")
        st.markdown(
            "GroMoPo can already smell the ingredients being cooked in the pot and knows that now is the time to add some spices."
            " Tease his taste buds by answering the questions below!")

        code_r = st.radio("Model code?", ("MODFLOW", "GSFLOW", "Feflow", "Parflow", "Hydrogeosphere",
                                          "GMS", "HYDRUS", "VS2D", "Bespoke", "Unknown", "Other"))
        if code_r == "Other":
            c = st.text_input("Enter model framework name:", "")
            data["ModelCode"] = c
        else:
            data["ModelCode"] = code_r

        purpose_r = st.radio("Model purpose?", ("groundwater resources", "groundwater contamination",
                                                "scientific investigation (not related to applied problem)",
                                                "Subsidence", "climate change", "salt water intrusion",
                                                "streamflow depletion", "agricultural growth", "decision support",
                                                "Other:"))
        if purpose_r == "Other":
            c = st.text_input("Enter model purpose:", "")
            data["ModelPurpose"] = c
        else:
            data["ModelPurpose"] = purpose_r

        eval_r = st.radio("Model evaluation or calibration?",
                          ("static water levels", "dynamic water levels", "baseflow",
                           "groundwater chemistry", "contaminant concentrations",
                           "Not sure", "Other"))

        if eval_r == "Other":
            c = st.text_input("Enter model evaluation scheme:", "")
            data["ModelEval"] = c
        else:
            data["ModelEval"] = eval_r

        t_additonal = st.text_area("Model Description (additional information)",
                                   "What additional information would be helpful?")
        data["ModelAddtional"] = t_additonal

        st.markdown("# Geological information (ADDITIONAL INFORMATION)")
        st.markdown("GroMoPo doesn’t like to eat rocks but sometimes when times are hard and nobody gives him yummy"
                    " groundwater models to eat it comes back and tries to sift through the leftovers and crumbs.")

        geo_r = st.radio("Dominant geologic material (that model focuses on)", ("Unconsolidated sediments",
                                                                                "Siliciclastic sedimentary (sandstones, shales)",
                                                                                "Carbonate (including karst)",
                                                                                "Crystalline", "Volcanic",
                                                                                "Model focuses on multiple geologic materials",
                                                                                "Unsure",
                                                                                "Other"))

        if geo_r == "Other":
            c = st.text_input("Enter other geo:", "")
            data["ModelGeo"] = c
        else:
            data["ModelGeo"] = geo_r

        geo_avial_r = st.radio("Is the data available?", ("Yes", "No", "Unsure"))
        data["GeoAvail"] = geo_avial_r

        st.markdown("# Feedback")
        st.markdown(
            "GroMoPo would love to know about your experience in its kitchen and hopes you enjoyed spending time cooking here!")

        time_r = st.radio("How long did it take to fill out this form?", ("1 Minute", "1-5 Minutes", "5-10 Minutes",
                                                                          "10-15 Minutes", "15 or more"))
        data["TimeToFillOut"] = time_r

        t_additonal = st.text_area(
            "Did you encounter any troubles while filling the form? Or do you have anything else you would like to share with GroMoPo?",
            "Complains or thoughts")
        data["Additonal"] = t_additonal
        if st.form_submit_button(label='Submit', help="Submit the form", on_click=process_data, args=(data,)):
            st.session_state.counter += 1
            # This will trigger a message to the user that the data has been saved or if data is malformed/missing
