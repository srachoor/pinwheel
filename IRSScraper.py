from TaxForm import TaxForm;
import json;

# create an empty list that will hold each tax form's dataset (e.g., the form_number, form_title, min_year, and max_year)
tax_forms = [];

# ask user for input -- first fields: ask for a list of tax forms they want data on
# parse the input into an array of tax-forms to look up
tax_forms_input = input("Please enter the tax forms you would like to search. \nEnsure that you use a comma to separate multiple forms. (e.g., \"Form 1040, Form W-2\")\nIf you want to download a tax form for one or more years, please only enter one form name (e.g., \"Form 1040\").\n")

if (tax_forms_input == ""):
    print("You must provide an input for the program to run.")
    quit()

tax_form_arr = tax_forms_input.split(",")

# if the user inputs only one tax form, then ask them to input years for the files they would like to download. If no years are provided, then send the JSON data back instead of the downloaded files.
try:
    if (len(tax_form_arr) == 1):
        tax_years_input = input("\nPlease enter a range of years you would like to download documents for " + tax_form_arr[0].strip() + ". Please use a hyphen to separate the year range (e.g., \"1999-2000\"). \nLeave blank and press enter if you only want information about each tax form. \nOnly enter one year with no hyphen if you want one year's document downloaded.\n");

        # if no years are entered, then just send the json data requested for the file
        if (tax_years_input == ""):
            newTaxForm = TaxForm(tax_form_arr[0].strip());
            tax_forms.append(newTaxForm.scrape_soups());
            print("\n" + json.dumps(tax_forms, indent=2));

        # if years are entered, then download the relevant documents requested
        else:
            tax_year_arr = tax_years_input.split('-');
            newTaxForm = TaxForm(tax_form_arr[0].strip());
            
            if (len(tax_year_arr) == 1):
                newTaxForm.download_file(int(tax_year_arr[0]));    
            else:
                newTaxForm.download_files(int(tax_year_arr[0]), int(tax_year_arr[1]));

    else:
        for each_form in tax_form_arr:
            newTaxForm = TaxForm(each_form.strip());
            tax_forms.append(newTaxForm.scrape_soups());
        
        print("\n" + json.dumps(tax_forms, indent=2));

except Exception as e:
    print(e);
