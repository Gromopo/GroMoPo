import streamlit as st
import streamlit_tags as stt

import streamlit.components.v1 as components

import re, json, itertools, platform, tempfile
from datetime import datetime
from pathlib import Path
from hsclient import HydroShare
from hsmodels.schemas.fields import Creator, BoxCoverage, PointCoverage
from os import remove

# from https://stackabuse.com/python-validate-email-address-with-regular-expressions-regex/
regex_mail = re.compile(
    r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
regex_doi = re.compile(
    r"/^10.\d{4,9}/[-._;()/:A-Z0-9]+$/i")  # thanks to https://www.crossref.org/blog/dois-and-matching-regular-expressions/
regex_isbn = re.compile(r"/^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$/")


def emailNotification(resourceID, gmp_form_time, gmp_feedback, msg=''):

    emailList = ['robert.reinecke@uni-potsdam.de', 'd.zamrsky@uu.nl',
                  'kmbefus@uark.edu', 'samzipper@ku.edu']
    
    url = r"https://www.hydroshare.org/resource/" + resourceID
    
    message = "A new GroMoPo resource has been submitted. Please view at " + url
    if gmp_form_time != "":
        message += "\nTime to fill out form: " + gmp_form_time
    if gmp_feedback not in ("", "Problems, comments, or suggestions"):
        message += "\nForm Feedback: " + gmp_feedback
    if msg != "":
        message += "\n" + msg
    subject = "New GroMoPo Resource Submitted"
    
    send_mail(emailList, subject, message)


def errorNotification(msg, dataDict, HS_ID='', prettyPrint=True):
    email = "kristen.kgs@ku.edu"

    subject = "Issue with GroMoPo Form Submission"

    if HS_ID != '':
        subject += ": " + HS_ID

    message = msg + "\n"

    if prettyPrint:
        message += prettyDict(dataDict)
    else:
        message += str(dataDict)

    send_mail(email, subject, message)

    
def send_mail(to, SUBJECT, TEXT):
    import smtplib  

    FROM = 'gromopo@ku.edu'
    
    if isinstance(to, list):
        TO = to
    else:
        TO = [to] # must be a list

    # Send the mail
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

    server = smtplib.SMTP('smtp.ku.edu')
    server.sendmail(FROM, TO, message)
    server.quit()  


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


def make_upload_file(content):
    
    b_content = content.encode('utf-8')
    
    # create temp file
    textFile = tempfile.NamedTemporaryFile()
    
    # write file
    textFile.write(b_content)
    textFile.close()
    
    return textFile.name


def check_requirements(df):
    '''
    This is a dict of requirement checks for each field.
    They are automatically applied to all fields in the form.
    We can assume that streamlit is only providing strings back in textfield
    cases so we just have to check if they are not empty or malformed.

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
        #"un": (lambda x: is_valid_string(x)),
        #"pw": (lambda x: is_valid_string(x)),
        "PubTitle": (lambda x: is_valid_string(x)),
        #"ModelName": (lambda x: is_valid_string(x)),
        "Abstract": (lambda x: is_valid_string(x)),
        #"ModelCountry": (lambda x: is_valid_string(x)),
        "ModelAuthors": (lambda x: not len(x) == 0),  # assumes that author list can't be empty
        "DevEmail": (lambda x: is_valid_mail(x)),
        # "DOI": (lambda x: is_valid_ref(x)), # FIXME currently this regex is not working
        "North": (lambda x: is_valid_lat(x)),
        "South": (lambda x: is_valid_lat(x)),
        "East": (lambda x: is_valid_lon(x)),
        "West": (lambda x: is_valid_lon(x))
    }
    failed = []
    for var, fun in reqs.items():
        if not fun(df[var]):
            failed.append(var)
    return len(failed) == 0, failed

def getTrueValue(term, method, data):

    # get original value
    if method == "webform":
        val = st.session_state[term]
        
        # see if it's set to "Unknown or ""Other"
        if val in ("Unknown", "Other") and st.session_state[term+"2"] != "":
            val = st.session_state[term+"2"]  
    else:
        val = data[term]

    # if it's blank, set to "Unknown"
    if val in ([], ''):
        val = "Unknown"
        
    return val


def prettyDict(uglyDict):
     
    # Pretty Print JSON
    prettyDict = json.dumps(uglyDict, indent=4)
    return prettyDict


def prettyList(term):

    # get origial list
    a_list = st.session_state[term]
    strList = ", ".join(a_list)

    return strList


def remove_items(test_list, item):

    # using list comprehension to perform the task
    res = [i for i in test_list if i != item]

    return res

def push_to_hydroshare(data, method="webform"):

    # set dictionary equal to session state object
    if method == "webform":
        st_data = st.session_state
    elif method == "csv":
        st_data = data

    # read settings and configs
    try:
        f = open(main_path.joinpath('config.json'))
        config = json.load(f)
    except:
        pass
    
    try:
    # if 1==1:
        hs = HydroShare(st_data["t_un"], st_data["t_pw"])
    
        # add basic HydroShare components
        new_resource = hs.create()
        resIdentifier = new_resource.resource_id
        new_resource.metadata.title = "GroMoPo Metadata for " + st_data["ModelName"].strip()
        new_resource.metadata.abstract = st_data["Abstract"]
        new_resource.metadata.creators.append(Creator(name=st_data["SubmittedName"]))
        
        # save the resource
        new_resource.save()
    
        # set up file upload
        uploaded_file = st_data["files"]
        chkUnzip = False
        tryBox = False
        setPublic = False
        
        # see if a zip file was uploaded        
        if method == "webform":
            if uploaded_file != '':
                try:
                    # attempt to upload additional files
                    # This is the url where the post is happening
                    hsapi_path = f'{new_resource._hsapi_path}/files/' 
                    new_resource._hs_session.upload_file(hsapi_path, 
                                      files={'file': uploaded_file}, status_code=201)
                    
                    # edit flags
                    setPublic = True
                    chkUnzip = True
                    
                except:
                    print("file upload failed")
                    tryBox = True
            else:
                tryBox = True

        # or upload a file
        elif uploaded_file != '' and method == "csv":
            # First create a new folder
            new_resource.folder_create('GroMoPoUpload')
            
            # Upload one or more files to a specific folder within a resource
            new_resource.file_upload(st_data['files'], destination_path='GroMoPoUpload')
    
            # edit flags
            tryBox = True
            
        if tryBox:
            
            if method == "webform":
                # create temp file
                textFile = tempfile.NamedTemporaryFile(mode="w+t", suffix=".txt", delete=False)
                
                textFile.write("info")
                
                # create a new folder in HydroShare
                new_resource.folder_create('GroMoPoUpload')
                
                # Upload one or more files to a specific folder within a resource
                new_resource.file_upload(textFile.name, destination_path='GroMoPoUpload')
                
                # close & remove temp text file
                textFile.close()
            
            # edit flags
            setPublic = True
            chkUnzip = False
            
            # if needed, turn ModelCountry into a string instead of a list
            if type(st_data["ModelCountry"]) is list:
                lstCountries = st_data["ModelCountry"]
                strCountries = ", ".join(lstCountries)
            else:
                strCountries = st_data["ModelCountry"]
                        
            # add spatial coverage as a box if no shapefile
            if st_data["North"] != "0.0" and st_data["East"] != "0.0" and st_data["South"] != "0.0" and st_data["West"] != "0.0":
                new_resource.metadata.spatial_coverage = BoxCoverage(name=strCountries,
                                                                      northlimit=st_data["North"],
                                                                      eastlimit=st_data["East"],
                                                                      southlimit=st_data["South"],
                                                                      westlimit=st_data["West"],
                                                                      projection='WGS 84 EPSG:4326',
                                                                      type='box',
                                                                      units='Decimal degrees')
                
            else:
                new_resource.metadata.spatial_coverage = PointCoverage(name="Global",
                                                                      north=1.0,
                                                                      east=1.0,                                                                      
                                                                      projection='WGS 84 EPSG:4326',
                                                                      type='point',
                                                                      units='Decimal degrees')
        
        # add keywords as subjects
        # add authors as keywords
        subjects = st_data["subjects"]
        
        # loop through authors and add as subjects if not testing names
        for a_name in st_data["ModelAuthors"]:
            if a_name not in ("T. Test", "Guy McGuy", ""):
                subjects.append(a_name.strip())
                
        # get all model codes
        m_codes, subjects = combine_multi_and_tags(st_data["ModelCode"], 
                                                    st_data["ModelCode2"], subjects)
        
        # get all model purposes
        m_purpose, subjects = combine_multi_and_tags(st_data["ModelPurpose"], 
                                                          st_data["ModelPurpose2"], subjects)
        
        # get all integrations
        m_integ, subjects = combine_multi_and_tags(st_data["ModelIntegration"], 
                                                          st_data["ModelIntegration2"], subjects)
                
        # get all evaluations
        m_eval, subjects = combine_multi_and_tags(st_data["ModelEval"], 
                                                  st_data["ModelEval2"], subjects)
    
        # make sure no unhelpful subjects get included
        for subj in ["None of the above", []]:
            if subj in subjects:
                subjects.remove(subj)
    
        # set subjects/tags in HydroShare
        new_resource.metadata.subjects = subjects
        
        # save resource in HydroShare
        new_resource.save()
    
        # see if a file was uploaded
        if chkUnzip and method == "webform":
            # # unzip the file
            file = new_resource.files()[0]
            upload_name = file.path
            new_resource.file_unzip(path=upload_name, overwrite=True, ingest_metadata=False)
    
        # logic to get various variables
        # model scale
        m_scale = getTrueValue("ModelScale", method, st_data)
        # geology
        m_geo = getTrueValue("ModelGeo", method, st_data)    
    
        # additional information
        m_add_info = ""
        if st_data["ModelAdditional"] != "What additional information about this model should be included?":
            m_add_info = st_data["ModelAdditional"]
            
        # depth
        if st_data["Depth"] != '': 
            depth = str(st_data["Depth"]) + " meters"
        else:
            depth = ''
            
        # verification
        isVerified = "False"
        if method == "csv":
            isVerified = "True"
            
        # create dictionary of additional metadata
        addl_metadata = {
            "IsVerified": isVerified,
            "Publication Title": st_data["PubTitle"],
            "Original Developer": st_data["OriginalDev"],
            "Model Year": str(st_data["ModelYear"]),
            "Data Available": st_data["DataAvail"],
            #"SameCountry": st_data["SameCountry"],
            "Developer Country": st_data["DevCountry"],
            "Model Country": strCountries,
            #"Model Authors": ', '.join(st_data["ModelAuthors"]),
            "Model Link": st_data["ModelLink"],
            "Developer Email": st_data["DevEmail"],
            #"Model Review": st_data["ModelReview"],
            "DOI": st_data["DOI"],
            "Scale": m_scale,
            "Layers": st_data["Layers"],
            "Depth": depth,
            "Dominant Geology": m_geo,
            "Geologic Data Availability": st_data["GeoAvail"],
            "Model Time": str(st_data["ModelTime"]),
            "Model Code": ', '.join(m_codes),
            "Purpose": ', '.join(m_purpose),
            "Integration or Coupling": ', '.join(m_integ),
            "Evaluation or Calibration": ', '.join(m_eval),
            "Additional Information": m_add_info,
            "Creator Email": st_data["SubmittedEmail"]
        }
        
        # loop through additional metadata, and if any values are blank, add not available
        for key in addl_metadata:
            val = addl_metadata[key]
            
            if val in ('', []):
                addl_metadata[key] = "N/A"
    
        new_resource.metadata.additional_metadata = addl_metadata
        
        # add terms as needed
        for term in ["GroMoPo_ID", "ModelReview"]:
            if term in st_data:
                new_resource.metadata.additional_metadata[term] = st_data[term]
            
        # save additional metadata in HydroShare
        new_resource.save()
        
        # see if the resource should be public
        if setPublic:
            # set sharing to public 
            try:
                new_resource.set_sharing_status(public=True)
                
                try:
                    # add GroMoPo_admin as a co-owner
                    hsapi_path_access = f'{new_resource._hsapi_path}/access/'
                    user_id = 18677
                    user_info = {"privilege": 2, "user_id": user_id, "resource": resIdentifier}
                    new_resource._hs_session.put(hsapi_path_access, data=user_info, status_code=202)
                except:
                    print("Could not add GroMoPo as co-owner")
            except:
                print("Could not add as public resource")
                
        emailNotification(resIdentifier, st_data["TimeToFillOut"], st_data["Additional"])
        
    except Exception as e:
        try:
            print("Error with data upload for record " + resIdentifier + ". The issue is being recorded.")
            errorNotification(str(e), st_data, resIdentifier)
        except:
            errorNotification(str(e), st_data, resIdentifier, prettyPrint=False)
    

def process_data(data:dict):
    '''
    Processes the input data for review, storage and email etc.
    This is a callback from the submit button of the form
    '''

    passed, loffields = check_requirements(data)

    if not passed:
        st.warning("The following fields contain malformed data: {}".format(loffields))
        return

    # FIXME ST spinner seems to be buggy at the moment possibly this needs to be executed in a different task threat
    with st.spinner('Data is being processed ...'):
        push_to_hydroshare(data)

    # bring user to the top of the page
    if "counter" not in st.session_state:
        st.session_state.counter = 1
    st.session_state.counter += 1
    st.success('Your data was successfully submitted')


def combine_multi_and_tags(group1, group2, subjects):
    
    list_codes = list(itertools.chain.from_iterable([group1, group2]))
    for a_code in list_codes:
        if a_code not in subjects:
            subjects.append(a_code)
            
    return list_codes, subjects


# Apparently processor should be empty on streamlit.io
if platform.system() == 'Windows':
    main_path = Path(".")
else:
    main_path = Path("streamlit")


if platform.system() == 'Windows':
    main_path = Path(".")
else:
    main_path = Path("streamlit")

@st.cache
def get_countries():
    # open countries file
    with open(main_path.joinpath('utils', 'countries.json'), 'r') as cs:
        country_data = cs.read()

    # create list of countries to use in dropdown
    countries = json.loads(country_data)["countries"]
    l_countries = [d['name'] for d in countries]
    return l_countries


def app():
    from utils import helpers as hp
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

    # start displaying form
    markdown = hp.read_markdown_file(str(main_path.joinpath('pages', 'view', 'submit_page.md')))
    st.markdown(markdown, unsafe_allow_html=True)

    m_mark = "<font color='red' font-size='large'>*</font>"

    with st.form(key='my_form'):
        st.markdown("# MANDATORY QUESTIONS(1 - 2 minutes)", unsafe_allow_html=True)
        st.markdown("In case GroMoPo really liked your recipe (or fell ill after eating it!)"
                    " it would like to keep your personal credentials so it can contact you in future,"
                    " and reward frequent contributors.")

        # collect all answers in this dict 
        data = {}

        # KJK- create variable for tags in HydroShare (called subjects in HS API)
        # automatically add GroMoPo tag
        subjects = ["GroMoPo"]

        # 1.1 SUBMITTER NAME
        t_name = st.text_input(label="Your name (which may be different than model developer)",
                            value="GroMoPo User", key="SubmittedName")
        # Text field to fill in the name – constrain to string datatype only.
        data["SubmittedName"] = t_name

        # 1.2 SUBMITTER EMAIL
        t_email = st.text_input(label="Your E-mail *", value="mail@mail.com", key="SubmittedEmail")
        data["SubmittedEmail"] = t_email

        # 1.25 HYDROSHARE CREDENTIALS
        st.markdown("HydroShare credentials for upload. Passwords are not saved.")

        t_un = st.text_input(label="HydroShare Username *", key="t_un")
        t_pw = st.text_input(label="HydroShare Password *", type="password", key="t_pw")
        data["un"] = st.session_state["t_un"]
        data["pw"] = st.session_state["t_pw"]

        # 1.4 PUBLICATION TITLE
        t_pub_title = st.text_input(label="Publication Title *", value="Model Publication Name", key="PubTitle")
        data["PubTitle"] = t_pub_title

        # 1.45 PUBLICATION/MODEL ABSTRACT
        t_abstract = st.text_input(label="Publication/Model Abstract *", value="Please paste abstract here.", key="Abstract")
        data["Abstract"] = t_abstract
        
        # DESCRIPTIVE MODEL NAME       
        model_name = st.text_input(label="Brief Descriptive Model Name (i.e., Edwards Aquifer model) *", value="", key="ModelName")
        data["ModelName"] = model_name
        
        # 1.46 MODEL LINK
        t_model_link = st.text_input(label="Link to paper, report, or model *", value="", key="ModelLink")
        data["ModelLink"] = t_model_link

        # 1.5 MODEL YEAR
        yearVal = datetime.now().date().year
        n_year = st.slider(label="Year of model development/publication *", min_value=1960,
                           max_value=2024,
                           value=yearVal, key="ModelYear")
        data["ModelYear"] = n_year
        subjects.append(str(n_year)[0:4])

        # 1.6 DOI/CITATION
        t_doi = st.text_input(label="DOI (Digital Object Identifier) for model.",
                            value="", key="DOI")
        data["DOI"] = t_doi
        
        # 1.8 MODEL AVAILABILITY
        t_m_avail = st.radio(label="Model data availability *", options=("Report/paper only", "Output publicly available",
                                                               "Input and output publicly available", "Unsure"), key="DataAvail")
        data["DataAvail"] = t_m_avail
        
        # 1.3 IS SUBMITTER SAME AS DEVELOPER?
        b_dev = st.radio(label="Are you the original model developer?", options=("Yes", "No"), key="OriginalDev")
        data["OriginalDev"] = b_dev

        # if original developer, add name as subject
        if b_dev == "Yes":
            subjects.append(st.session_state["SubmittedName"])

        # 1.7 MODEL DEVELOPERS
        l_names = stt.st_tags(
            label='Model developers/authors (e.g.: A. Lastname1 C. Lastname2). Max = 6'
                  ' If there are no personal credentials provided, please fill in the name of the organization that created the model *',
            text='Press enter to add more',
            value=['T. Test'],
            suggestions=['FirstName LastName'],
            maxtags=6,
            key='ModelAuthors')

        data["ModelAuthors"] = l_names
        
        # 2.1 MODEL DEVELOPER EMAIL
        t_email_dev = st.text_input(label="Model developer primary email", value="mail@mail.com", key="DevEmail")
        data["DevEmail"] = t_email_dev

        # 1.10 COUNTRY OF INSTITUTE OR DEVELOPER
        l_countries = get_countries()
        t_country = st.selectbox(label="Country of primary model developer or institution *",
                                options=l_countries, key="DevCountry")
        data["DevCountry"] = t_country
        
        # 1.9 MODEL INSTITUTE COUNTRY vs. MODEL LOCATION
        b_country = st.radio(label="Is the model developer's institute located in the same country as the model location?",
                             options=("Yes", "No", "Unclear"), key="SameCountry")
        data["SameCountry"] = b_country
        
        st.markdown("# Model File Attachment")
        st.markdown("Please upload spatial geometry files associated with the model as a zip file (e.g., shapefile of model boundary or extent).")
        
        # 2.6.1 UPLOAD FILE
        uploaded_files = st.file_uploader(label="Zipped files, max size 5 MB - please use HydroShare.org or another data repository for publishing other model files",
                                          accept_multiple_files=False, type="zip", key="files")
            
        
        # 2.6 MODEL EXTENT
        c_country = st.multiselect(label="Model country (can select multiple)",
                            options=l_countries, key="ModelCountry")
        # c_country = st.text_input(label="Model country or countries", value="", key="ModelCountry")
        data["ModelCountry"] = c_country
        
        st.markdown("# Model Extent and Scale")
        st.markdown("Please enter bounding box coordinates for model extent.")
        st.markdown("The bounding box coordinates can be easily achieved through e.g. google maps where you can right"
                    " click on a point in the map and then click on the coordinates it automatically shows."
                    " Then you can simply copy those in the fields below.")

        # 2.6.2 CENTROID
        st.markdown("Top left coordinate")
        # note- these are text input since streamlit input limited decimals to 3 places
        t_north = st.text_input(label="Top Left Latitude/Y Value (ex. 37.023) *", 
                            value="0.0", key="North")
        t_west = st.text_input(label="Top Left Longitude/X Value (ex. -103.025) *", 
                            value="0.0", key="West")

        st.markdown("Bottom right coordinate")
        # note- these are text input since streamlit input limited decimals to 3 places
        t_south = st.text_input(label="Bottom Right Latitude/Y Value (ex. 33.764) *", 
                            value="0.0", key="South")
        t_east = st.text_input(label="Bottom Right Longitude/X Value (ex. -94.544) *", 
                            value="0.0", key="East")
        data["North"] = t_north
        data["East"] = t_east
        data["South"] = t_south
        data["West"] = t_west
        
        # 2.5 MODEL SCALE
        scale_r = st.multiselect(label="Model Scale (can choose multiple)", options=("Unknown", "Global", "Continental", "National", ">100 000 km²",
                                "10 001 - 100 000 km²", "1 001 - 10 000 km²", "101 - 1 000 km²",
                                "11 - 101 km²", "< 10 km²", "Other"), key="ModelScale")

        scale_r_2 = st.text_input(label="If Other, enter scale:", value="", key="ModelScale2")

        if "Other" in st.session_state.ModelScale and st.session_state.ModelScale2 != "":
            data["ModelScale"].append(st.session_state.ModelScale2)
        else:
            data["ModelScale"] = st.session_state.ModelScale
        subjects.append(data["ModelScale"])
        
        st.markdown("# Geological Information")

        # 4.1 GEOLOGIC FOCUS
        geo_r = st.radio(label="Dominant geologic material (that model focuses on)", options=("Unknown","Unconsolidated sediments",
                            "Siliciclastic sedimentary (sandstones, shales)",
                            "Carbonate (including karst)",
                            "Crystalline", "Volcanic",
                            "Model focuses on multiple geologic materials",
                            "Other"), key="ModelGeo")

        geo_r_2 = st.text_input(label="If Other, enter dominant geologic material:", value="", key="ModelGeo2")

        if st.session_state.ModelGeo == "Other" and st.session_state.ModelGeo2 != "":
            data["ModelGeo"] = st.session_state.ModelGeo2
        else:
            data["ModelGeo"] = st.session_state.ModelGeo
        subjects.append(data["ModelGeo"])

        # 4.2 GEOLOGIC DATA AVAILABILITY
        geo_avial_r = st.radio(label="Is the geologic data available?", options=("Unknown", "Yes", "No"), key="GeoAvail")
        data["GeoAvail"] = geo_avial_r
        

        st.markdown("# Model General Information")

        # 2.7 NUMBER OF LAYERS
        n_layers = st.number_input(label="Number of (model) layers in model domain", 
                                   min_value=0, max_value=500, step=1, key="Layers")
        data["Layers"] = n_layers

        # 2.8 MAXIMUM DEPTH
        n_depth = st.number_input(label="Maximum depth of model below ground surface in meters", 
                          min_value=1, max_value=10000, step=10, key="Depth")
        data["Depth"] = n_depth

        # 2.9 TIME RANGE
        t_time_range = st.text_input(label="Time range of the model or SS for steady state", key="ModelTime")
        data["ModelTime"] = t_time_range

        st.markdown("# Model Technical Information")

        # 3.1 MODEL CODE
        code_r = st.multiselect(label="Model code(s). Select all applicable.", options=("MODFLOW", "SEAWAT", "GSFLOW", "Feflow", "Parflow", "Hydrogeosphere",
                                          "GMS", "HYDRUS", "VS2D", "Bespoke"), key="ModelCode")

        code_r_2 = stt.st_tags(
            label='Enter additional model code(s)',
            text='Press enter to add more',
            value=[],
            suggestions=[],
            maxtags=6,
            key='ModelCode2')

        # 3.2 MODEL PURPOSE
        purpose_r = st.multiselect(label="Model Purpose(s). Select all applicable.", options=("Groundwater resources", "Groundwater contamination",
                                                "Scientific investigation (not related to applied problem)",
                                                "Subsidence", "Climate change", "Salt water intrusion",
                                                "Streamflow depletion", "Agricultural growth", "Decision support"),
                                                key="ModelPurpose")

        purpose_r_2 = stt.st_tags(
            label='Enter additional model purpose(s)',
            text='Press enter to add more',
            value=[],
            suggestions=[],
            maxtags=6,
            key='ModelPurpose2')

        # 3.3 INTEGRATION
        integration_r = st.multiselect(label="Integration or coupling with other types of models. Select all applicable.", options=("Surface water",
                                "Water use", "Land surface model", "Water management", "Ecosystem health",
                                "Agent-based model", "Economic", "Solute transport", "Geochemical"), key="ModelIntegration")

        integration_r_2 = stt.st_tags(
            label='Enter additional model integration(s)',
            text='Press enter to add more',
            value=[],
            suggestions=[],
            maxtags=6,
            key='ModelIntegration2')

        # 3.4 EVALUATION
        eval_r = st.multiselect(label="Model evaluation or calibration. Select all applicable.",
                          options=("Static water levels", "Dynamic water levels", "Baseflow",
                           "Groundwater chemistry", "Contaminant concentrations", "Other (list below)"), key="ModelEval")

        eval_r_2 = stt.st_tags(
            label='Enter additional model evaluation(s)',
            text='Press enter to add more',
            value=[],
            suggestions=[],
            maxtags=6,
            key='ModelEval2')

        # 3.5 ADDITONAL INFO
        t_additonal = st.text_area(label="Additional Model Information",
                                   value="What additional information about this model should be included?",
                                   key="ModelAdditional")
        data["ModelAdditional"] = t_additonal


        st.markdown("# Feedback")

        # 5.1 FORM FILL TIME
        time_r = st.radio(label="How long did it take to fill out this form?", options=("1 Minute", "1-5 Minutes",
                        "5-10 Minutes", "10-15 Minutes", "15 or more"), key="TimeToFillOut")
        data["TimeToFillOut"] = time_r

        # 5.2 GroMoPo FEEDBACK
        t_additional = st.text_area(
            label="Did you encounter any troubles while filling the form? Or do you have anything else you would like to share with GroMoPo?",
            value="Problems, comments, or suggestions", key="Additional")
        data["Additional"] = t_additional

        # KJK- add subjects/tags, but remove certain tags
        remove_tags = ["Unknown", "Other", "Guy McGuy", "", "T. Test", "GroMoPo User"]

        for tag in remove_tags:
            subjects = remove_items(subjects, tag)

        data["subjects"] = subjects
        st.session_state["subjects"] = subjects

        if st.form_submit_button(label='Submit', help="Submit the form", 
                                 on_click=process_data, 
                                 args=(data,)):
            st.session_state.counter += 1
            # This will trigger a message to the user that the data has been saved or if data is malformed/missing

        st.markdown("Any issues? [Report them on GitHub](https://github.com/Gromopo/GroMoPo/issues).")
