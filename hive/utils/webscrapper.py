from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
import time


def scrape_website_text(url):
    # Automatically download and install EdgeDriver
    s = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=s)

    # Open the webpage
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)

    # Scrape the page title
    page_title = driver.title

    try:
        # Get the entire page source
        page_source = driver.page_source

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all <p> tags
        p_tags = soup.find_all('p')

        # Initialize an empty string to store all the text
        all_text = ""

        # Loop through the list of <p> tags and get their text
        for p in p_tags:
            all_text += p.text + "\n"

        # Show the first 100 characters of the scraped text
        print(f"Scraped Text: {all_text}")

    except Exception as e:
        print(f"An error occurred: {e}")

    # Close the browser after a short pause
    time.sleep(5)
    driver.quit()

    print(f"Page Title: {page_title}")


# Example usage
scrape_website_text("https://www.indeed.com/career-advice/career-development/target-demographic")


