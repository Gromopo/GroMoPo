import streamlit as st
import streamlit_tags as stt
import json
import re
from datetime import datetime
from utils import helpers as hp

# from https://stackabuse.com/python-validate-email-address-with-regular-expressions-regex/
regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")


def save_data_to_storage(data):
	'''
	Save data as pickled geopandas frame to storage with unique ID
	-> How do we update a common data-base after submission?
	Will there be a merge script?
	'''
	pass


def send_email_to(name, info):
	pass


def process_data(data):
	'''
	Processes the input data for review, storage and email etc.
	This is a callback from the submit button of the form
	'''
	print(data)
	save_data_to_storage(data)
	send_email_to("name of reviewer", "info")
	send_email_to("name of model dev", "info")


def is_valid(email):
	if re.fullmatch(regex, email):
		return True
	else:
		return False


def app():
	markdown = hp.read_markdown_file("pages/view/submit_page.md")
	st.markdown(markdown, unsafe_allow_html=True)

	st.markdown("MANDATORY QUESTIONS(1 - 2 minutes)")
	st.markdown("In case GroMoPo really liked your recipe (or fell ill after eating it!)"
				" it would like to keep your personal credentials so it can contact you in future,"
				" and reward frequent contributors.")

	# collect all answers in this dict -> we can easily use this as json to sent it via mail
	# and append it to one pandas data frame.
	data = {}

	# TODO color mandatory *
	# This is possible but not very flexible -> more efficient to check when submit is pressed.
	# if not t_name:
	#	st.warning("Can't be empty.")

	t_name = st.text_input("Your name (which may be different than model developer) *", "")
	# Text field to fill in the name – constrain to string datatype only.
	data["SubmittedName"] = t_name

	t_email = st.text_input("Your E-mail *", "")
	data["SubmittedEmail"] = t_email

	b_dev = st.radio("Are you the original model developer?", ("Yes", "No"))
	data["OriginalDev"] = b_dev

	n_year = st.slider("Model development/publication YEAR *", min_value=datetime(1970, 1, 1, 9, 30), max_value=datetime(2030, 1, 1, 9, 30), value=datetime(2020, 1, 1, 9, 30), format="MM/DD/YY")
	data["ModelYear"] = n_year

	t_m_avail = st.selectbox("Model data availability *", ("Report/paper only", "Output publicly available",
														   "Input and output publicly available", "Unsure"))
	data["DataAvail"] = t_m_avail

	b_country = st.radio("Is the model developer's institute located in the same country as the model location?  *",
					 ("Yes", "No", "Unclear"))
	data["SameCountry"] = b_country

	#FIXME this should be cached
	with open('utils/countries.json', 'r') as cs:
		country_data = cs.read()
	countries = json.loads(country_data)["countries"]
	l_countries = [d['name'] for d in countries]
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

	t_email_dev = st.text_input("Model developer primary email *", "")
	data["DevEmail"] = t_email_dev

	b_review = st.radio("Model review",
						 ("Double-blind peer review journal",
						  "Peer review journal",
						  "Peer reviewed report (includes internal review at governmental agencies like USGS)",
						  "Not peer reviewed",
						  "Not sure"))
	data["ModelReview"] = b_review

	t_cite = st.text_input("Citation(s) for report, data and/or code (DOI or ISBN)", "")
	data["Cite"] = t_cite
	# TODO check if valid?

	#TODO
	#2.4. Report, data or code files (Max. file-size: 5mb)
	#File upload field.

	scale_r = st.radio("Model Scale", ("Global", "Continental", "other->slider"))

	n_scale = None
	if scale_r == "other->slider":
		n_scale = st.slider("Model scale km²", min_value=1, max_value=100000, value=2000, step=100)
	if n_scale is not None:
		data["ModelScale"] = n_scale
	else:
		data["ModelScale"] = scale_r

#2.6. Model extent (upload zipfile; optional, don't spend time looking for it if not easily available), if model shapefile unavailable please specify the model location as Lat | Lon (e.g., 36.069 ; -94.172), ideally center of domain. This can be easily achieved through e.g. google maps where you can right

#click on a point in the map and then click on the coordinates it automatically shows. Then you can simply copy those in the fields below.
#Two fields (float numbers) with Latitude and Longitude coordinate input.
#2.7. Number of (model) layers in model domain
#‘1 layer’, ‘2-5 layers’, ‘6-10 layers’, ‘11-15 layers’, ‘16-20 layers’, ‘>20 layers’ options.
#2.8. Maximum depth of model below ground surface (m)
#Field with numerical value – integer. OR should we provide ranges like in question 3.3.? Might be easier for the user to fill in.
#2.9. Time range of model (or SS for steady-state)
#Field with range for years (XXXX - YYYY) or SS.

#3. Model technical information (ADDITIONAL INFORMATION)
#GroMoPo can already smell the ingredients being cooked in the pot and knows that now is the time to add some spices. Tease his taste buds by answering the questions below!
#3.1. Model code
#‘MODFLOW’, ‘GSFLOW’, ‘Feflow’, ‘Parflow’, ‘Hydrogeosphere’, ‘GMS’, ‘HYDRUS’, ‘VS2D’, ‘Bespoke’, ‘Unknown’, ‘Other’ options, make the ‘Other’ option also a text field (string).
#3.2. Model purpose
#Current options – ‘groundwater resources’, ‘groundwater contamination’, ‘scientific investigation’ (not related to applied problem), ‘Subsidence’, ‘climate change’, ‘salt water intrusion’, ‘streamflow depletion’, ‘agricultural growth’, ‘decision support’, ‘Other:’.
#3.3. Integration or coupling with other types of models
#‘Surface water’, ‘Water use’, ‘Land surface model’, ‘Water management’, ‘Ecosystem health’, ‘Agent-based model’, ‘Economic’, ‘Solute transport’, ‘Geomechanical’, ‘None of the above’, ‘Other:’ options.
#3.4. Model evaluation or calibration
#Current options are ‘static water levels’, ‘dynamic water levels’, ‘baseflow’, ‘groundwater chemistry’, ‘contaminant concentrations’, ‘-Not sure’, ‘Other:’
#3.5. Model Description (additional information)
#	Text field where users can write any other information that they deem necessary.

#4. Geological information (ADDITIONAL INFORMATION)
#GroMoPo doesn’t like to eat rocks but sometimes when times are hard and nobody gives him yummy groundwater models to eat it comes back and tries to sift through the leftovers and crumbs.
#4.1. Dominant geologic material (that model focuses on)
#‘Unconsolidated sediments’, ‘Siliciclastic sedimentary (sandstones, shales)’, ‘Carbonate (including karst)’, ‘Crystalline’, ‘Volcanic’, ‘Model focuses on multiple geologic materials’, ‘Unsure’, ‘Other:’ options.
#4.2. Geological input data available
#‘Yes’, ‘No’ and ‘Unsure’ options.

#5. Feedback
#GroMoPo would love to know about your experience in its kitchen and hopes you enjoyed spending time cooking here!
#5.1. How long did it take to fill out this form?
#‘1 Minute’, ‘1-5 Minutes’, ‘5-10 Minutes’, ‘10-15 Minutes’, ‘15 or more’ options.
#5.2. Did you encounter any troubles while filling the form? Or do you have anything else you would like to share with GroMoPo?
#Text field where the user can complain or share their thoughts.


	#Slider example
	#s = st.slider("pick", min_value=1, max_value=100, value=50, step=1)
	#st.write(s)

	data = None

	# This will trigger a message to the user that the data has been saved or if data is malformed/missing
	st.button("Submit", help="Submit the form", on_click=process_data, args=data)
	#TODO loop over all fields and tell the user which fields did not pass the consistency test
