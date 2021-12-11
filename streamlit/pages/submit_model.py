import streamlit as st
import json
from utils import helpers as hp


def process_data(data):
	'''
	Processes the input data for review, storage and email etc.
	This is a callback from the submit button of the form
	'''
	print(data)


def app():
	markdown = hp.read_markdown_file("pages/view/submit_page.md")
	st.markdown(markdown, unsafe_allow_html=True)

	st.markdown("MANDATORY QUESTIONS(1 - 2 minutes)")
	st.markdown("In case GroMoPo really liked your recipe (or fell ill after eating it!)"
				" it would like to keep your personal credentials so it can contact you in future,"
				" and reward frequent contributors.")

	# TODO color mandatory *
	t_name = st.text_input("Your name (which may be different than model developer) *", "")
	# Text field to fill in the name – constrain to string datatype only.
	if not t_name:
		st.warning("Can't be empty.")

	t_email = st.text_input("Your E-mail *", "")
	# Text field to fill in the email – constrain to string datatype only,
	# has to contain “@” – check upon clicking the submit button (if possible)

	b_dev = st.radio("Are you the original model developer?", ("Yes", "No"))

	n_year = st.number_input("Model development/publication YEAR *", min_value=1960, max_value=2030, value=2000, step=1)

	t_m_avail = st.selectbox("Model data availability *", ("Report/paper only", "Output publicly available",
														   "Input and output publicly available", "Unsure"))

	b_country = st.radio("Is the model developer's institute located in the same country as the model location?  *",
					 ("Yes", "No", "Unclear"))

	#FIXME this should be cached
	with open('utils/countries.json', 'r') as cs:
		country_data = cs.read()
	countries = json.loads(country_data)["countries"]
	l_countries = [d['name'] for d in countries]
	t_country = st.selectbox("Country of primary model developer or institution  *", l_countries)

#Model developers/authors (e.g.: A. Lastname1, C. Lastname2). If there are no personal credentials provided, please fill in the name of the organization that created the model *
	#One line text field (un-editable) on top and below that a text field (user input) with button next to it
# – so user can add authors one by one and there is no variation in separation by either ‘;’ or ‘,’.
# Once the button is pressed the list of authors gets updated and shown in the upper text field so the user has a visual confirmation?
# Maybe also a remove button? Maybe this is too complicated?

#Model general information (ADDITIONAL INFORMATION)
#GroMoPo can already see the ingredients in the shopping bags! Now it is curious about some general information such as – how many portions will it eat? How old are the ingredients?
#2.1. Model developer primary email
#Text field to fill in the email – constrain to string datatype only, has to contain “@” – check upon clicking the submit button (if possible)

#2.2. Model review
#‘Double-blind peer review journal’, ‘Peer review journal’, ‘Peer reviewed report (includes internal review at governmental agencies like USGS)’, ‘Not peer reviewed’, ‘Not sure’ options.
#2.3. Citation(s) for report, data and/or code (DOI and/or ISBN)
#Two text fields? One for DOI number and one for ISBN?
#2.4. Report, data or code files (Max. file-size: 5mb)
#File upload field.
#2.5. Model scale
#Is it possible to make a slider here with km2? If not, we can go back to the classification in the previous version which was: ‘Global’, ‘Continental’, ‘National’, ‘10 001 - 100 000 km²’, ‘1 001 - 10 000 km²’, ‘101 - 1000 km²’, ‘11 - 100 km²’, ‘< 10 km²’, ‘Other’
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
