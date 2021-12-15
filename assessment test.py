import time
import csv
from concurrent.futures import ThreadPoolExecutor
from lxml import html
import requests

domain = 'https://nces.ed.gov/COLLEGENAVIGATOR/'
#proxie = {'https': 'https://10706:Jq4wtJ@world.nohodo.com:6811', 'http': 'http://10706:Jq4wtJ@world.nohodo.com:6811'}
collages_list =[]

h = {
'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'accept-encoding' : 'gzip, deflate, br',
'accept-language' : 'en-US,en;q=0.9',
'connection' : 'keep-alive',
'sec-ch-ua' : '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
'sec-ch-ua-mobile' : '?0',
'sec-fetch-dest' : 'document',
'sec-fetch-mode' : 'navigate',
'sec-fetch-site' : 'cross-site',
'sec-fetch-user' : '?1',
'upgrade-insecure-requests' : '1',
'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}

#----------------------------------------------------------Collage page scraping function------------------------------------------

def scraping(list_url):

    print("list_url-",list_url)
    for i in range(3):
        list_response = s.get(list_url, headers=h, timeout=30)

        if list_response.status_code == 200:
            break
        else:
            time.sleep(2)
            continue

#----------------------------------------Extracting collage_blocks from list page-----------------------------------------------------

    list_response = html.fromstring(list_response.text)
    collage_blocks = list_response.xpath('*//table[@class="resultsTable"]/tr')

    for collage in collage_blocks:
        collage_1={}

        name = collage.xpath('*//strong/text()')[0]
        url = collage.xpath('*//a/@href')[0]
        url = domain+url

        for j in range(3):
            collage_response = s.get(url, headers=h, timeout=30)

            if collage_response.status_code == 200:
                break
            else:
                time.sleep(2)
                continue

#------------------------------------------------Scraping collage data--------------------------------------------------------------

        collage_response = html.fromstring(collage_response.text)
        address = collage_response.xpath('*//div[@class="collegedash"]/div[2]/span/text()')[0]
        address = str(address).split(',')
        city = address[-2]
        state = address[-1].split(' ')[0]
        if state == '':
            state = address[-1].split(' ')[:-1]
            state = ' '.join(state1 for state1 in state)
            zip = address[-1].split(' ')[-1]
        else:
            zip = address[-1].split(' ')[1]

        street = ''
        try:
            address = address[:-2]
            if len(address) > 1:
                for addre in address:
                    street = street + ' ' + str(addre)
            else:
                street = address[0]
        except:
            pass

        block = collage_response.xpath('*//table[@class="layouttab"]/tr')
        try:
            phone = block[0].xpath('*//text()')[1]
        except:
            phone=''
        try:
            website = collage_response.xpath('*//table[@class="layouttab"]/tr/td/a/@href')[0]
        except:
            website=''
        try:
            type = block[2].xpath('*//text()')[1]
        except:
            type=''
        try:
            awards = block[3].xpath('*//text()')[1:]
            awards = ', '.join(award.replace("\'s", 's') for award in awards)
        except:
            awards=''
        try:
            Campus_setting = block[4].xpath('*//text()')[1]
        except:
            Campus_setting=''
        try:
            campus_housing = block[5].xpath('*//text()')[1]
        except:
            campus_housing=''
        try:
            student_population = block[6].xpath('*//text()')[1]
        except:
            student_population=''
        try:
            Student_to_faculty_ratio = block[7].xpath('*//text()')[1]
        except:
            Student_to_faculty_ratio=''

        collage_1={
            "Name":str(name), "Street":str(street), "City":str(city), "State":str(state), "Zip":str(zip), "Phone":phone,
            "Website":website, "Type":type, "Awards":awards, "Campus_setting":Campus_setting, "Campus_housing":campus_housing,
            "Student_population":student_population, "Student_to_faculty_ratio": Student_to_faculty_ratio
        }

        collages_list.append(collage_1)

#--------------------------------------------------Creating Session------------------------------------------------------------

s = requests.session()
list_pages_url='https://nces.ed.gov/COLLEGENAVIGATOR/?s=all&l=91+92+93+94&ct=1+2+3&ic=1+2+3&pg=1'
list_pages=[]
pages=0

for i in range(3):
    response = s.get(list_pages_url,headers=h, timeout=30)

    if response.status_code == 200:
        break
    else:
        time.sleep(2)
        continue

response = html.fromstring(response.text)

#--------------------------------------------------Creating list page URL--------------------------------------------------------

total_collages = response.xpath('*//div[@id="ctl00_cphCollegeNavBody_ucResultsMain_divMsg"]/text()')[1].replace('+','').replace(' ','')
total_pages = (int(total_collages) / 15)

if total_pages > int(total_pages):
    pages = int(total_pages + 1)
else:
    pages = int(total_pages)

for i in range(pages):
    list_pages.append(list_pages_url.replace('pg=1','pg='+str(i+1)))

#-------------------------------Threading----------------------------------------------------------------------------------------

with ThreadPoolExecutor(max_workers=3) as executor:
    All_collages =executor.map(scraping,list_pages)

#----------------------------------Creating csv file---------------------------------------------------------------------------

with open('Excel_file2.csv', 'w', encoding='utf8',
          newline='') as output_file:
    fc = csv.DictWriter(output_file,
                        fieldnames=collages_list[0].keys(),

                        )
    fc.writeheader()
    fc.writerows(collages_list)
    output_file.close()

