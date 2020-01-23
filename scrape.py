from urllib.request import urlopen
from bs4 import BeautifulSoup as soup

car_info = {
    "Price": "no info",
    "Transmission": "no info",
    "Horsepower": "no info",
    "Torque": "no info",
    "Engine liters": "no info",
    "Cylinder configuration": "no info",
    "Drivetrain": "no info",
    "Combined MPG": "no info",
    "Fuel economy city": "no info",
    "Fuel economy highway": "no info",
    "Recommended fuel": "no info",
    "Fuel tank capacity": "no info",
    "Front tires": "no info",
    "Curb weight": "no info",
    "Basic warranty (months/miles)": "no info",
    "Powertrain warranty (months/miles)": "no info"
}

def textfile_to_list(info_to_scrape):
    f = open(info_to_scrape, 'r')
    newlist = [item for item in f.readlines()]
    
    #parse out newline characters
    for i in range(len(newlist)-1):
        newlist[i] = newlist[i][:-1]

    #for l in newlist:
        #print(l)
    return newlist

def scrape_car(car_make, car_model, car_year, info_to_scrape):

    if type(info_to_scrape) is list:
         print("LIST!")
    else:
        info_to_scrape = textfile_to_list(info_to_scrape)

    
    car_info = {info: "no info" for info in info_to_scrape}


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

    #fill in header
    car_file.write("Trims")
    for item in car_info:
        car_file.write("," + item)
    car_file.write("\n")


    #for trim in trim_urls:
        #trim_info = scrape_trim(trim, car_info, car_file)
        #print(trim_info)


    #open url to specific trim
    uClient2 = urlopen("https://www.cars.com" + trim_urls["L"])
    page_html2 = uClient2.read()
    uClient2.close()

    page_soup2 = soup(page_html2, "html.parser")

    #find price
    price_tag = page_soup2.find("div", {"class": "specs-price__value"})
    price = price_tag.text
    car_info["Price"] = price

    #find overview info
    overview_container = page_soup2.find("table", {"class": "overview-table"})
    overview_items = overview_container.tbody.findAll("tr")

    for item in overview_items:
        if item.td.text in car_info:
            car_info[item.td.text] = item.findAll("td")[1].text

    #find specifications container
    specs_container = page_soup2.find("section", {"id": "specifications-section"})

    #divide sections of specifications
    specs_sections = specs_container.div.findAll("table", {"id": "specs-accordion-table"})

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

    for x,y in car_info.items():
        print(x + ": " + y)






    

    car_file.close()

    #uClient2 = urlopen("https://www.cars.com" + new_url)
    #page_html2 = uClient2.read()
    #uClient.close()

    #page_soup2 = soup(page_html2, "html.parser")

    #print(page_soup2.h1)