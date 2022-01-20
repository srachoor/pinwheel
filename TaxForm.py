from bs4 import BeautifulSoup as soup;
from urllib.request import urlopen as uReq;
import requests;

class TaxForm:

    # class variables
    soup_array = [];
    min_year = 3000; # setting a year that hasn't occured yet.
    max_year = 0;
    base_url = "https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow=";
    url_snippet2 = "&criteria=formNumber&value=";
    url_snippet3 = "&isDescending=false";

    # constructor populates the soup_array to have all the beautifulSoup elements that need to be parsed for the given tax form
    # we need multiple BeautifulSoup elements because the results that we search can be on multiple webpages
    def __init__(self, form_number):
        
        # create the first URL to identify the total number of results
        self.form_number = form_number;
        self.initialURL =(self.base_url + "0" + self.url_snippet2 + self.form_number.replace(" ", "+") + self.url_snippet3);
        
        # set the total results and create all the needed soups for the tax form
        self.create_soup();

    def create_soup(self):

        # opens the connection and downloads html page from url
        uClient = uReq(self.initialURL);

        # parses html into a soup data structure to traverse html as if it were a json data type.
        page_soup = soup(uClient.read(), "html.parser");
        self.soup_array.append(page_soup);
        uClient.close();
        
        resultsElement = page_soup.find("th", {"class": "ShowByColumn"});
        if (resultsElement == None):
            raise Exception("One or some of the search terms provided were not found on IRS website.")
        
        else:
            # finds the element on the page that has the total number of results
            resultsElementText = page_soup.find("th", {"class": "ShowByColumn"}).get_text();

            # remove line breaks and excess spaces
            arr = resultsElementText.strip().split(" ");
            
            # gets the index of the total number of search results and sets it to the object. Format is usually "Results: X - Y of N files", hence the index("files")
            indexOfTotalResults = arr.index("files") - 1;
            self.totalResults = int(arr[indexOfTotalResults].replace(",",""));

            # default search results per page is set to 200 as given in the base_url above. If there are more than 200 results, we'll need mutliple soups
            if (self.totalResults > 200):
                self.create_additional_soups();
            

    # only called if there are more than 200 search results
    def create_additional_soups(self):
        numOfURLs = (int((self.totalResults/200)) + (self.totalResults % 200 > 0));
        for x in range(1, numOfURLs):
            firstRow = str(x * 200);
            currentURL = self.base_url + firstRow + self.url_snippet2 + self.form_number.replace(" ", "+") + self.url_snippet3;
            uClient = uReq(currentURL);
            page_soup = soup(uClient.read(), "html.parser");
            uClient.close();
            self.soup_array.append(page_soup);

    # only called if the user wants the json data objects
    def scrape_soups(self):
        for each_soup in self.soup_array:
            table_rows = each_soup.findAll("tr", {"class": ["odd", "even"]});
            for each_row in table_rows:
                form_number = each_row.a.get_text();
                if (form_number == self.form_number):
                    current_year = int(each_row.find("td",{"class": "EndCellSpacer"}).get_text());
                    self.min_year = min(self.min_year, current_year);
            
                    if (current_year > self.max_year): 
                        self.max_year = current_year;
                        self.form_title = each_row.find("td", {"class": "MiddleCellSpacer"}).get_text().strip();                    

        return self.get_data();

    def get_data(self):
        x = {
            "form_number": self.form_number,
            "form_title": self.form_title,
            "min_year": self.min_year,
            "max_year": self.max_year,
        };
        return x;

    # only called if user wants to download the files
    def download_files(self, year1, year2):
        num_docs_requested = (year2 - year1 + 1);
        print("Requested " + str(num_docs_requested) + " documents for the years: " + str(year1) + "-" + str(year2));
        i = 0;
        for each_soup in self.soup_array:
            table_rows = each_soup.findAll("tr", {"class": ["odd", "even"]});
            for each_row in table_rows:
                form_number = each_row.a.get_text();
                current_year = int(each_row.find("td",{"class": "EndCellSpacer"}).get_text());
                if (form_number == self.form_number and (current_year >= year1 and current_year <= year2)):
                    pdfLink = each_row.find("td",{"class": "LeftCellSpacer"}).a["href"];
                    response = requests.get(pdfLink);
                    with open("form/" + form_number + ' - ' + str(current_year),"wb") as pdf:
                        pdf.write(response.content);
                    i+=1;
        
        print("Retrieved " + str(i) + " documents out of the " + str(num_docs_requested) + " documents requested.");
        if (i < (num_docs_requested) and i > 0):
            print("Not all years' documents were availabe for the tax form.")
        elif (i == 0):
            raise Exception("This tax form did not have any documents for range of years provided.")

    # only called if user wants to download the file for one year
    def download_file(self, year1):
        print("Requested one document for the year: " + str(year1));
        for each_soup in self.soup_array:
            table_rows = each_soup.findAll("tr", {"class": ["odd", "even"]});
            for each_row in table_rows:
                form_number = each_row.a.get_text();
                current_year = int(each_row.find("td",{"class": "EndCellSpacer"}).get_text());
                if (form_number == self.form_number and (current_year == year1)):
                    pdfLink = each_row.find("td",{"class": "LeftCellSpacer"}).a["href"];
                    response = requests.get(pdfLink);
                    with open("form/" + form_number + ' - ' + str(current_year),"wb") as pdf:
                        pdf.write(response.content);
                        print("Retrieved the document for the year: " + str(year1));
                    return;
        
        raise Exception("Year not found in IRS database.");