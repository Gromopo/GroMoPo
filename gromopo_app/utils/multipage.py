"""
This file is the framework for generating multiple Streamlit applications 
through an object oriented framework. 
"""

# Adapted from https://github.com/prakharrathi25/data-storyteller MIT License

# Import necessary libraries 
import streamlit as st

# Define the multipage class to manage the multiple apps in our program


class MultiPage: 
    """Framework for combining multiple streamlit applications."""

    def __init__(self) -> None:
        """Constructor class to generate a list which will store all our applications as an instance variable."""
        self.pages = {}
    
    def add_page(self, title, func) -> None: 
        """Class Method to Add pages to the project
        Args:
            title ([str]): The title of page which we are adding to the list of apps 
            
            func: Python function to render this page in Streamlit
        """
        self.pages.update({title:func})
        
    def run(self, menu):
        self.pages[menu]()
