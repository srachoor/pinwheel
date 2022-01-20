This is a short program that is used to scrape the IRS website for tax documents, allowing users to either retrieve information about a given tax form in JSON format or automatically download said tax documents. Please refer to the project prompt in the pdf filed named "Pinwheel__SWE__Integrations_Take_Home_Exercise.pdf" in the directory to better understand the purpose of this project.

As an FYI, I was not familiar with python prior to this exercise. I learned it in the last 48 hours so please excuse any departures from standard syntax and styling convention. Thank you!

<h2>Steps to start the program:</h2>

1. Clone or download the "pinwheel" folder to your computer locally
2. Open and use your terminal or command-line tool to navigate to the "pinwheel" folder using cd <folderpath>
3. Download the necessary modules using pip package manager (for instructions on installing pip or python, see below). This can be done by running the following commands:
  
    `pip3 install -r requirements.txt`

4. Once the modules have been installed using pip, run the program with the following command:

    `python3 IRSScraper.py`

5. Enter a form or multiple forms as they would exactly appear on the IRS website (https://apps.irs.gov/app/picklist/list/priorFormPublication.html). If any of the search terms provided by the user does not exactly match the name of a tax form on the IRS website, the program will return an error. See below for further details on functionality of the program.

<h2>Steps to download python / pip:</h2>
The python version used for this project is **Python 3.9.10** and **pip 21.3.1**

1. Please download python3 from here: https://www.python.org/downloads/
2. Please download pip for python3 by following these instructions: https://pip.pypa.io/en/stable/installation/

<h2>Thoughts on methodology / assumptions:</h2>

This was set up for two functionalities --

**Functionality 1:** Allow a user to input a list of tax form names (exactly as each tax form would appear on the IRS website) and return a JSON object with key details (form_number, form_title, min_year, and max_year) for each tax form.

**Functionality 2:** Allow a user to input a single tax form name (exactly as it would appear on the IRS website) and a range of years and download each year's version of the tax form requested.

These two functionalities were accomplished by using the `input()` method where the user must enter their information in the terminal.
1. First, the program will prompt the user and ask what tax forms they would like to search for. If the user enters multiple tax forms, it will automatically retrieve the relevant key details and return a JSON of the object array.
2. Second, if the user enters only one tax form, then the program will prompt the user to provide a range of years. 
    - If the year range is left blank, the program assumes that the user doesn't want to download any files and returns the key details in JSON format
    - If the year range is one year or multiple years, the program fetches and downloads the documents to the "form" subfolder and it communicates how many of the requested documents were downloaded.

**Everything should be run on the terminal/commandline and the JSON output will be printed in the terminal output.**

**<h3>Assumptions:</h3>**

- I assumed that the `form_title` should be the title of the latest year's tax document. Sometimes a form might have multiple `form_title` fields so I had to chose one title to return to the user
- I made an assumption to be conservative in my search for documents. I search every `page_soup` to see if the form requested is in that page. In a realistic case, the program could stop once it finds the last instance of the tax form it was searching for. IRS search results are organized in a way that keeps every form with the exact same name together.
- If the user provides a form_number that doesn't exist (e.g., Form XKCD), I made the decision to send a null object in its place so that the user can tell which item did not return. For example, if the user inputs ("Form W-2, Form XKCD, Form 1040"), the program will return the following output:

<pre>
[
  {
    "form_number": "Form W-2",
    "form_title": "Wage and Tax Statement (Info Copy Only)",
    "min_year": 1954,
    "max_year": 2022
  },
  null,
  {
    "form_number": "Form 1040",
    "form_title": "U.S. Individual Income Tax Return",
    "min_year": 1864,
    "max_year": 2021
  }
]
</pre>