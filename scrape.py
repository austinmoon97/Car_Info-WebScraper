from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import re


# PARAMETER(S):
#     info_to_scrape (.TXT FILE) = contains desired info to be scraped
#
# FUNCTION: 
#     parses text file by line, removes \n characters, returns list of info to scrape
#
def textfile_to_list(info_to_scrape):
    f = open(info_to_scrape, 'r')
    newlist = [item for item in f.readlines()]
    
    #parse out newline characters
    for i in range(len(newlist)-1):
        newlist[i] = newlist[i][:-1]

    return newlist

# PARAMETER(S): 
#     trim (STRING) = trim level of car to be scraped
#     trim_url (STRING) = url to trim info
#     car_info (DICT) = holds scraped info
#     all_trims_soup (BS4 OBJ) = parsable html of https://www.cars.com/research/make-model-year/trims/
#
# FUNCTION:
#     scrapes info for a specific trim, returns populated dictionary
#
def scrape_trim(trim, trim_url, car_info, all_trims_soup):

    #open url to specific trim
    uClient = urlopen("https://www.cars.com" + trim_url)
    page_html = uClient.read()
    uClient.close()

    #construct beautiful object
    page_soup = soup(page_html, "html.parser")

    #find overview info
    overview_container = page_soup.find("table", {"class": "overview-table"})
    overview_items = overview_container.tbody.findAll("tr")

    for item in overview_items:
        if item.td.text in car_info:
            if len(item.findAll("td")[1].text) > 0:
                car_info[item.td.text] = item.findAll("td")[1].text

    #find specifications container
    specs_container = page_soup.find("section", {"id": "specifications-section"})

    #divide sections of specifications
    specs_sections = specs_container.div.findAll("table", {"id": "specs-accordion-table"})

    ########################################################


    for section in specs_sections:
        specs = section.find("tbody").findAll("tr")
        for spec in specs:
            if spec.td.text in car_info:
                car_info[spec.td.text] = spec.find("td",{"class":"data"}).text


    #######################################################
    """
    #find engine specs
    engine_specs = specs_sections[3].find("tbody").findAll("tr")
    
    for spec in engine_specs:
        if spec.td.text in car_info:
            car_info[spec.td.text] = spec.findAll("td")[1].text

    #find suspension/handling specs
    suspension_specs = specs_sections[6].find("tbody").findAll("tr")

    for spec in suspension_specs:
        if spec.td.text in car_info:
            car_info[spec.td.text] = spec.find("td",{"class":"data"}).text

    #find standard specs
    standard_specs = specs_sections[12].find("tbody").findAll("tr")

    for spec in standard_specs:
        if spec.td.text in car_info:
            car_info[spec.td.text] = spec.find("td",{"class":"data"}).text

    #find warranty specs
    warranty_specs = specs_sections[13].find("tbody").findAll("tr")

    for spec in warranty_specs:
        if spec.td.text in car_info:
            car_info[spec.td.text] = spec.find("td",{"class":"data"}).text
    """

    #find price and drivetrain (not available on the same html page)
    #use bs4 object corresponding to https://www.cars.com/research/make-model-year/trims/
    trim_containers = all_trims_soup.findAll("div", {"class":"cui-accordion-section"})[:-3]

    #find container of the correct trim
    for container in trim_containers:
        if container.label.h3.text[6:] == trim:
            
            #find divs containing price and drivetrain
            target_divs = container.findAll("div", {"class":"cell cell-bg"})

            #extract price/drivetrain
            price = re.sub("[a-z A-Z]", "", target_divs[0].text)
            drivetrain = target_divs[1].text

            car_info["Price"] = price
            car_info["Drivetrain"] = drivetrain
            

    for x,y in car_info.items():
        print(x + ": " + y)

    return car_info

# PARAMETER(S):
#     car_make (STRING) = make of car
#     car_model (STRING) = model of car
#     car_year (STRING) = year of car
#     info_to_scrape (.TXT FILE or LIST) = what info to scrape
#
# FUNCTION:
#     Initial function to be called.
#     Creates and saves csv file with car info in current directory
#
def scrape_car(car_make, car_model, car_year, info_to_scrape):

    if type(info_to_scrape) is list:
         print("LIST!")
    else:
        info_to_scrape = textfile_to_list(info_to_scrape)


    #construct car url from make, model, year parameters
    CAR_URL = f"https://www.cars.com/research/{car_make}-{car_model}-{car_year}/trims/"

    #open the url, load it into trim_page_html
    uClient = urlopen(CAR_URL)
    trim_page_html = uClient.read()    #page containing all trims of specified car

    #close the url
    uClient.close()

    #call BeautifulSoup constructor, creates parsable html
    trim_page_soup = soup(trim_page_html, "html.parser")

    #find all divs containing trim info
    #exclude last 3, those don't contain trim info
    trim_containers = trim_page_soup.findAll("div", {"class":"cui-accordion-section"})[:-3]

    trim_urls = {}      #trim_urls["trim"] = url to that trim

    for container in trim_containers:
        trim_name = container.label.h3.text[6:]     #parse out first 6 chars from "Trim: label"
        trim_url = container.find("div", {"class":"cell cell-border-bottom"}).a["href"]
        trim_urls[trim_name] = trim_url
    
    #create csv for car info and open for writing
    filename = f"{car_make}_{car_model}_{car_year}_info.csv"
    car_file = open(filename, "w")

    #fill in csv header
    car_file.write("Trims")
    for item in info_to_scrape:
        car_file.write("," + item)
    car_file.write("\n")

    #fetch info for every trim level
    for trim in trim_urls:
        #initialize dictionary of car info to scrape
        car_info = {info: "no info" for info in info_to_scrape}
        
        #populates car_info
        trim_info = scrape_trim(trim, trim_urls[trim], car_info, trim_page_soup)

        #write trim info to csv
        car_file.write(trim)
        for info in car_info.values():
            #remove commas from info, confuses with csv delimiter
            if "," in info:
                info = info.replace(",", "")
            car_file.write("," + info)
        car_file.write("\n")

        print(trim)
        print(trim_info)


    car_file.close()        #close csv file