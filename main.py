from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

main_page_urls = set()
sub_page_urls = set()

driver = webdriver.Chrome()

driver.get("https://scholenopdekaart.nl/middelbare-scholen/")

cookies_accept_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "CybotCookiebotDialogBodyButton"))
)
cookies_accept_button.click()

# Generate a timestamp and create a unique filename
timestamp = datetime.now().strftime("%m-%d-%Y %H-%M")
filename = f"contact_details_{timestamp}.csv"

# w: means it will overwrite any existing changes to previous file
with open(filename, "w", newline="", encoding="utf-8") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["URL", "Phone Number", "Email", "School Name"])

    try:
        li_elements = driver.execute_script(
            'return document.querySelectorAll(".list.list-columns li");'
        )
        for li in li_elements:
            link = driver.execute_script("return arguments[0].querySelector('a');", li)
            if link:
                url = link.get_attribute("href")
                main_page_urls.add(url)

        print("Length of main page URLs:", len(main_page_urls))

        for main_page_url in main_page_urls:  # Limit to first 15
            sub_page_urls.clear()
            print("Visiting:", main_page_url)
            driver.get(main_page_url)

            li_elements = driver.execute_script(
                'return document.querySelectorAll(".list.list-columns li");'
            )
            for li in li_elements:
                link = driver.execute_script(
                    "return arguments[0].querySelector('a');", li
                )
                if link:
                    url = link.get_attribute("href")
                    sub_page_urls.add(url)

            print("Length of sub page URLs:", len(sub_page_urls))

            for sub_page_url in sub_page_urls:
                print("Visiting sub-page:", sub_page_url)
                driver.get(sub_page_url)

                contact_link = driver.execute_script(
                    "return document.querySelector('li a[data-automation-id=\"button-hoofdstuk-contact\"]');"
                )
                if contact_link:
                    contact_url = contact_link.get_attribute("href")
                    print("Navigating to contact page:", contact_url)
                    driver.get(contact_url)

                    phone_element = driver.execute_script(
                        "return document.querySelector('a[href^=\"tel:\"]');"
                    )
                    phone_number = phone_element.text if phone_element else "N/A"

                    email_element = driver.execute_script(
                        "return document.querySelector('a[href^=\"mailto:\"]');"
                    )
                    email = email_element.text if email_element else "N/A"

                    school_name_element = driver.execute_script(
                        "return document.querySelector('h1.school-naam');"
                    )
                    school_name = (
                        school_name_element.text if school_name_element else "N/A"
                    )

                    csvwriter.writerow([sub_page_url, phone_number, email, school_name])

                    print(
                        f"Saved details for {sub_page_url}: {phone_number}, {email}, {school_name}"
                    )

            driver.get("https://scholenopdekaart.nl/middelbare-scholen/")

    finally:
        print("Finished, quitting driver now.")
        driver.quit()
