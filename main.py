from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time

LOGIN     = ""            #Email or phone number
PASSWORD  = ""            #Password
CITY      = "Odessa"      #City to search
DATE_FROM = "3"           #FORMAT : DAY.MONTH
DATE_TO   = "5"           #FORMAT : DAY.MONTH
GENDER    = "Male"        #Male or Female (Empty for both)
SYMBOL    = "а"

SCROLL_AMOUNT = 10    #Amount of jumps to bottom
TIMEOUT = 0.1         #Seconds per scrolling

MONTHS = {
    "January":   1,
    "February":  2,      
    "March":     3,
    "April":     4,
    "May":       5,
    "June":      6,
    "July":      7,
    "August":    8,
    "September": 9,
    "October":   10,
    "November":  11,
    "December":  12
}

driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get("https://facebook.com")


class Authorization:
    def __init__(self, email, passwd):
        print("Authorization...")
        self.email = email
        self.passwd = passwd

    def auth(self):
        email_field = driver.find_element_by_id("email")
        passwd_field = driver.find_element_by_id("pass")

        email_field.send_keys(self.email)
        passwd_field.send_keys(self.passwd)
        passwd_field.send_keys(Keys.ENTER)

        time.sleep(1)


class Interaction:
    def __init__(self):
        print("Interacting...")

    def set_city(self, city):
        city_inp = driver.find_element_by_css_selector("._1u6r")

        actions = ActionChains(driver)
        actions.move_to_element(city_inp)
        actions.click(city_inp)
        actions.click(city_inp)
        actions.perform()

        city_fld = driver.find_element_by_css_selector("#u_ps_0_0_d")
        city_fld.send_keys(city)

        city_btn = driver.find_element_by_css_selector("li.page")

        actions = ActionChains(driver)
        actions.move_to_element(city_btn)
        actions.click(city_btn)
        actions.perform()

    def get_source(self):
        return driver.page_source

    def scroll_down(self, iterations):
        for i in range(iterations):
            driver.find_element_by_tag_name('body').send_keys(Keys.END)
            time.sleep(TIMEOUT)


class Parsing:
    def __init__(self):
        self.links = []
        self.users = []

    def find_users(self):
        self.elements = driver.find_elements_by_css_selector("._32mo")

        for l in self.elements:
            dirty_link = l.get_attribute("href")
            link = dirty_link.split("&")[0]
            try:
                link = link.split("?ref")[0]
            except: 
                pass

            self.links.append(link)
            print(link)

    def get_info(self): #/about?section=contact-info
        for i in range(len(self.links)):
            link = self.links[i]

            if link.find("profile.php") != -1:
                url = link + "&sk=about&section=contact-info"
                friends_url = link + "&sk=friends"
            else:
                url = link + "/about?section=contact-info"
                friends_url = link + "/friends"
            
            driver.get(url)
            
            try:
                driver.find_element_by_css_selector("._50f4")
                driver.find_element_by_css_selector("._5kx5")

                fields = driver.find_elements_by_css_selector("._50f4")

                bday_exists = False
                bday_index  = 0
                gndr_exists = False
                gndr_index  = 0

                index = 0

                for f in fields:
                    if f.text == "Birthday":
                        bday_exists = True
                        bday_index  = index
                    elif f.text == "Gender":
                        gndr_exists = True
                        gndr_index  = index
                    #Check for empty fields
                    if f.text.find("No contact info to show") == -1\
                        and f.text.find("To see what she shares with friends") == -1\
                        and f.text.find("Followers") == -1:
                        index += 1

                if bday_exists:
                    info = driver.find_elements_by_css_selector("div._pt5 > div.clearfix > div > span._2iem")

                    bday = info[bday_index]
                    if gndr_exists:
                        gender = info[gndr_index]
                    else:
                        gender = ""

                    name_info = driver.find_element_by_css_selector("._2nlw")
                    name = name_info.text

                    friends = self.get_friends(friends_url)

                    print("==============================")
                    print("NAME: %s" % name)
                    print("URL : %s" % link)
                    print("BDAY: %s" % bday.text)
                    print("GEND: %s" % gender.text)

                    user = {
                        "name": name,
                        "url": link,
                        "birthday": bday.text,
                        "gender": gender.text,
                        "friends": friends
                    }

                    if self.check_data(user):
                        print("SUCCESS!")
                        self.users.append(user)
            
            except:
                pass

            time.sleep(0.1)

    def get_friends(self, url):
        friends = []
        driver.get(url)

        info = driver.find_elements_by_css_selector(".fsl > a")

        for i in info:
            link = i.get_attribute("href")
            friends.append(link.split("&href")[0])
            print(link)

        return friends

    def check_data(self, user):
        if user["gender"] != GENDER and user["gender"] != "" and GENDER != "":
            return False

        if user["birthday"].find(",") != -1:
            bday = user["birthday"].split(",")[0]
        else:
            bday = user["birthday"]

        month = MONTHS[bday.split(" ")[0]]
        day   = int(bday.split(" ")[1])

        if DATE_FROM.find(".") != -1 and DATE_TO.find(".") != -1:
            DAY_FROM = int(DATE_FROM.split(".")[0])
            MONTH_FROM = int(DATE_FROM.split(".")[1])

            DAY_TO = int(DATE_TO.split(".")[0])
            MONTH_TO = int(DATE_TO.split(".")[1])

            required_months = self.get_required_months(MONTH_FROM, MONTH_TO)

            if month in required_months:
                if month == MONTH_FROM and day < DAY_FROM:
                    return False
                elif month == MONTH_TO and day > DAY_TO:
                    return False
                else:
                    return True 

        else:  
            required_months = self.get_required_months(int(DATE_FROM), int(DATE_TO))

            if month in required_months:
                return True
            else:
                return False

    def get_required_months(self, month_from, month_to):
        if month_from < month_to:
            required_months = [i for i in range(month_from, month_to+1)]
        else:
            required_months = [i for i in range(month_from, 13)] + [i for i in range(1, month_to+1)]

        return required_months


if __name__ == "__main__":
    #Authoriztion to FB
    bot = Authorization(LOGIN, PASSWORD)
    bot.auth()

    #Go to page with list of people
    driver.get("https://facebook.com/search/people/?q=" + SYMBOL + "&ref=eyJzaWQiOiIiLCJyZWYiOiJ0b3BfZmlsdGVyIn0%3D&epa=SERP_TAB")

    #Interactions with FB 
    action = Interaction()
    action.set_city(CITY)
    time.sleep(1)
    action.scroll_down(SCROLL_AMOUNT)

    parse = Parsing()
    parse.find_users()
    parse.get_info()




