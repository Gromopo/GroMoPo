import streamlit as st
import json
from utils import helpers as hp


def process_data(data):
	'''
	Processes the input data for review, storage and email etc.
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



	t_n = st.text_area("blabla")

	t_number = st.number_input("enter", min_value=0, max_value=99, value=50, step=1)

	s = st.slider("pick", min_value=1, max_value=100, value=50, step=1)
	st.write(s)

	select = st.selectbox("pick", ("item 1", "item2", "item3"))

	data = None

	st.button("Submit", help="Submit the form", on_click=process_data, args=data)
