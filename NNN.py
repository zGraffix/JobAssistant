import time
import os
import PyPDF2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Function to extract text from a PDF file
def extract_pdf_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error reading the PDF: {e}")
        return None

# Function to create a text file with extracted data
def create_text_file(extracted_text):
    try:
        with open("resume_data.txt", "w") as f:
            f.write(extracted_text)
        print("Resume data saved to resume_data.txt")
    except Exception as e:
        print(f"Error creating text file: {e}")

# Prompt the user for information
location = input("Enter your location: ")
industry = input("Enter your industry (e.g., software engineer, marketing, etc.): ")
hourly_rate = input("Enter your desired hourly rate: ")

# Ask for PDF resume upload
resume_path = input("Enter the path to your resume PDF: ")

# Extract data from the PDF resume
extracted_text = extract_pdf_text(resume_path)

if extracted_text:
    create_text_file(extracted_text)

# Setup the Selenium WebDriver with Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Construct Indeed search URL with the job field (industry), location, and hourly rate
search_url = f'https://www.indeed.com/jobs?q={industry.replace(" ", "+")}&l={location.replace(" ", "+")}&salary={hourly_rate}'

# Open the Indeed search results page
driver.get(search_url)

# Wait until the first job listing is visible and clickable
try:
    # Wait for the job listings to load by checking for the first listing to appear
    first_job = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a.jcs-JobTitle'))
    )
    print("First job listing found. Attempting to click...")
    
    # Click the first job listing
    first_job.click()  # Click the first job listing
    
    # Wait a little for the page to transition
    time.sleep(5)  # Adjust this delay as needed

    # Check if the current window is still open and if a new window opened
    if len(driver.window_handles) > 1:
        # Switch to the new window if it's open
        new_window = driver.window_handles[1]
        driver.switch_to.window(new_window)
        print("Switched to the new job details window.")
        
        # Wait for the job details page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))  # Wait until the body is loaded on the new page
        )
        print("Job details page loaded.")
    else:
        print("No new window opened. The job listing page might have loaded in the same window.")
    
except Exception as e:
    print(f"Error selecting the first job listing: {e}")

# Debugging: keep both windows open for inspection
print("Both job listing and details pages are open. Inspect them.")
time.sleep(30)  # Keep both windows open for 30 seconds to inspect the result

# Close the browser after inspection (you can remove this if you want to keep the windows open longer)
# driver.quit()  # Comment this out to keep the browser open
