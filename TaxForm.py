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
        self.initial_URL =(self.base_url + "0" + self.url_snippet2 + self.form_number.replace(" ", "+") + self.url_snippet3);
        
        # set the total results and create all the needed soups for the tax form
        self.create_soup();

    def create_soup(self):

        # opens the connection and downloads html page from url
        u_client = uReq(self.initial_URL);

        # parses html into a soup data structure to traverse html as if it were a json data type.
        page_soup = soup(u_client.read(), "html.parser");
        self.soup_array.append(page_soup);
        u_client.close();
        
        results_element = page_soup.find("th", {"class": "ShowByColumn"});
        
        if (results_element == None):
            return;
        
        else:
            # finds the element on the page that has the total number of results
            results_element_text = page_soup.find("th", {"class": "ShowByColumn"}).get_text();

            # remove line breaks and excess spaces
            arr = results_element_text.strip().split(" ");
            
            # gets the index of the total number of search results and sets it to the object. Format is usually "Results: X - Y of N files", hence the index("files")
            index_of_total_results = arr.index("files") - 1;
            self.total_results = int(arr[index_of_total_results].replace(",",""));

            # default search results per page is set to 200 as given in the base_url above. If there are more than 200 results, we'll need mutliple soups
            if (self.total_results > 200):
                self.create_additional_soups();
            

    # only called if there are more than 200 search results
    def create_additional_soups(self):
        num_of_URLs = (int((self.total_results/200)) + (self.total_results % 200 > 0));
        for x in range(1, num_of_URLs):
            first_row = str(x * 200);
            current_URL = self.base_url + first_row + self.url_snippet2 + self.form_number.replace(" ", "+") + self.url_snippet3;
            u_client = uReq(current_URL);
            page_soup = soup(u_client.read(), "html.parser");
            u_client.close();
            self.soup_array.append(page_soup);

    # only called if the user wants the json data objects
    def scrape_soups(self):
        for each_soup in self.soup_array:
            
            # find rows that match the form number (e.g., "Form W-2" or "Form 1040")
            table_rows = each_soup.find_all("a", text=self.form_number);
            
            # identify the min and max years by reviewing each row and set the title to the latest year's form title
            for each_row in table_rows:
                current_year = int(each_row.parent.parent.find("td",{"class": "EndCellSpacer"}).get_text());
                self.min_year = min(self.min_year, current_year);
        
                if (current_year > self.max_year): 
                    self.max_year = current_year;
                    self.form_title = each_row.parent.parent.find("td", {"class": "MiddleCellSpacer"}).get_text().strip();

        if(hasattr(self,"form_title")):
            return self.get_data();
        else:
            print("\nOne or some of the search terms provided were not found on IRS website.")

    # return an object we will return to the user as a prettified JSON object array
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
        print("\nRequested " + str(num_docs_requested) + " documents for the years: " + str(year1) + "-" + str(year2));
        
        i = 0;
        for each_soup in self.soup_array:
            table_rows = each_soup.find_all("a", text=self.form_number);
            
            for each_row in table_rows:
                current_year = int(each_row.parent.parent.find("td",{"class": "EndCellSpacer"}).get_text());
                
                if (current_year >= year1 and current_year <= year2):
                    pdf_link = each_row["href"];
                    response = requests.get(pdf_link);
                    with open("form/" + self.form_number + ' - ' + str(current_year),"wb") as pdf:
                        pdf.write(response.content);
                    i+=1;
        
        print("Retrieved " + str(i) + " documents out of the " + str(num_docs_requested) + " documents requested.");
        if (i < (num_docs_requested) and i > 0):
            print("Not all years' documents were availabe for the tax form.")
        elif (i == 0):
            raise Exception("This tax form did not have any documents for range of years provided.")

    # only called if user wants to download the file for one year
    def download_file(self, year1):
        print("\nRequested one document for the year: " + str(year1));
        for each_soup in self.soup_array:
            table_rows = each_soup.find_all("a", text=self.form_number);
            
            for each_row in table_rows:
                current_year = int(each_row.parent.parent.find("td",{"class": "EndCellSpacer"}).get_text());
                
                if (current_year == year1):
                    pdf_link = each_row["href"];
                    response = requests.get(pdf_link);
                    with open("form/" + self.form_number + ' - ' + str(current_year),"wb") as pdf:
                        pdf.write(response.content);
                        print("Retrieved the document for the year: " + str(year1));
                    return;
        
        raise Exception("Year not found in IRS database.");