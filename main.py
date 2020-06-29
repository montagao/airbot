import time

from getpass import getpass

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

def main():
    airBot = AirBot()
    airBot.setup()
    listing_urls = airBot.getListings()

    for listing in listing_urls:
        airBot.editListingDescription(listing)


class AirBot():
    def setup(self):
        """ Start WebDriver """
        ## self.getCreds() (use commandline arguments or a creds file)
        self.email = ""
        self.pw = ""
        self.dry_run = True

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("user-data-dir=selenium")
        chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

        ## only needs to be called once per session
        self.driver.implicitly_wait(5)
        #self.driver.fullscreen_window()

    def getListings(self):
        self.driver.get('https://www.airbnb.ca/hosting/listings')
        print('Fetching listings...')

        listing_elements = self.driver.find_elements_by_xpath("//a[contains(@href, 'manage-your-space')]")

        listing_urls = set()
        attempts = 0
        while attempts < 2:
            try:
                for v in listing_elements:
                    url = v.get_attribute("href")
                    print(url)
                    listing_urls.add(url)
                print(listing_urls)
                break
            except StaleElementReferenceException as e:
                # ty again
                print('Warning: Page updated.. trying again')
                listing_elements = self.driver.find_elements_by_xpath("//a[contains(@href, 'manage-your-space')]")
                attempts += 1

        return listing_urls


    def editListingDescription(self, listing_url):
        description_url = listing_url + '/details/description'
        self.driver.get(description_url)
        time.sleep(3)
        listingName = self.driver.find_element_by_name("listingNickname")
        print('Editing listing: ' + listingName.get_attribute("value") + ' : ' + description_url )

        access_summary = self.driver.find_element_by_id("listingdAccessInput")

        print('Found guest access info: \n```\n' + access_summary.text + ' \n```')

        # add a dot if there is none. remove a dot otherwise
        if (access_summary.text[-1] == '.'):
            print('removing "." at the end...')
            updated_access_summary = access_summary.text[:-1]
        else:
            print('adding "." to the end...')
            updated_access_summary = access_summary.text + '.'


        access_summary.clear()
        access_summary.send_keys(updated_access_summary)

        print('Updated guest access info: \n```\n' + access_summary.text + ' \n```')

        save_button = self.driver.find_element_by_xpath('//button[@type="submit" and not(@disabled)]')

        print('found save button')
        #TODO: Fix sleeps
        if (self.dry_run):
            print('DRY-RUN: Saving updated changes...')
        else:
            print('Saving updated changes...')
            save_button.click()

        time.sleep(3)

    def tearDown(self):
        """ Stop Web Driver """
        return

    def getCreds(self):
        print("Please enter your email:")
        self.email = input()
        self.pw = getpass()

    def login(self):
        self.driver.get("https://www.airbnb.ca/login?redirect_url=%2Fhosting")
        email_login_button = self.driver.find_element_by_class_name('_bema73j')
        email_login_button.click()

        print(self.email)

        email_form = self.driver.find_element_by_name('email')
        email_form.send_keys(self.email)


        pw_form = self.driver.find_element_by_name('password')
        pw_form.send_keys(self.pw)


        pw_form.submit()





if __name__ == "__main__":
    main()

