(MUST HAVE UP TO DATE PYTHON VERSION! [3.13.1])

1. Press 'windows key + R' and type 'cmd' - Press enter
	Run this command: pip install selenium webdriver-manager beautifulsoup4 pymupdf tqdm python-docx openai

2. Launch Chrome in a command prompt or terminal using this command: "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
	This opens Chrome in a debug window, which allows bypass of CAPTCHa 30 mins at a time.

3. Download a .pdf version of your resume, available on LinkedIn.
	Visit LinkedIn.com and click on 'view profile' on the top of the screen.
	Under your bio and connections, click the tab labeled 'Resources'.
	Click save as PDF, remember the file's save location as you will need it in step 3.
	
4. Run ApplicationAssistant.py and fill out prompts.
	Location - A 25 mile radius of where you want to look for work. Ex. Los Angeles
	Industry - What field do you want to apply to? Ex. Marketing
	Salary - Yearly pay. If you are looking for an hourly job, try typing 100000.
	Resume file path - This is where you paste the location of your resume PDF. Ex. "C:\Users\[user]\Desktop\resume.pdf"
	Headshot - (Not Required) If you would like an image of yourself included in the resume, paste the file path here the same way as you did the resume.

5. A new tab should open in chrome with the indeed search requirements filled out.
	From here, right click on the job you wish to create a tailered resume/cover letter for and click 'copy link address'
	(If you ever run into a CAPTCHa request, open Indeed.com in a new tab and complete the test. Then refresh the original window that was opened by ApplicationAssistant. It is important you stay in this tab!)
	Paste the link into the hotbar in THE SAME TAB.
	From here watch for errors in the console, and the finished resume will be exported into the folder where 'ApplicationAssistant.py' is located.

(NOTICE: THIS VERSION PROM<PTS USERS FOR OPENAI API KEY AND ORG ID, I IMPLEMENT IT DIRECTLY INTO THE CODE, IF YOUD LIKE TO DO THE SAME, HERE YOU GO.)








------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


[Replace [YOUR OPENAI API KEY] & [YOUR OPENAI ORG ID] with your unique data.]



import time
import logging
import random
import json
import openai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import fitz  # PyMuPDF for PDF text extraction
from tqdm import tqdm
import os
from docx import Document
from docx.shared import Pt, Inches

# Set up logging to log errors into a file
logging.basicConfig(filename='error_handling.txt', level=logging.ERROR)

# Set your API Key and Organization ID
openai.api_key = "[YOUR OPENAI API KEY]"
openai.organization = "[YOUR OPENAI ORG ID]"

def open_chrome_and_go_to_url(location, industry, preferred_salary):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Construct search URL with salary filter
        salary_query = f"&salary={preferred_salary}" if preferred_salary else ""
        search_url = f"https://www.indeed.com/jobs?q={industry}&l={location}{salary_query}"
        driver.get(search_url)

        time.sleep(random.uniform(3, 5))  # Delay to simulate user interaction
        print(f"Navigating to the URL: {search_url}")
        return driver, search_url
    except Exception as e:
        logging.error(f"Error navigating to the URL: {str(e)}")
        return None, None

def extract_pdf_text(pdf_path, output_file="raw_resume.txt"):
    try:
        with fitz.open(pdf_path) as pdf:
            text = ""
            for page in pdf:
                text += page.get_text()

        # Save extracted text to a file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(text.strip())
        print(f"Resume text extracted and saved to '{output_file}'.")
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        print("Failed to extract text from the provided PDF. Please check the file and try again.")

def extract_job_data(driver, output_file="job_details.txt"):
    try:
        # Get page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Locate the <script type="application/ld+json">
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            job_data = json.loads(script_tag.string)

            # Extract relevant data
            title = job_data.get("title", "No Title Found")
            description = BeautifulSoup(job_data.get("description", ""), 'html.parser').text.strip()
            salary = job_data.get("baseSalary", {}).get("value", {}).get("unitText", "Not Provided")
            min_salary = job_data.get("baseSalary", {}).get("value", {}).get("minValue", "Not Provided")
            max_salary = job_data.get("baseSalary", {}).get("value", {}).get("maxValue", "Not Provided")

            # Extract company name
            company_name = (
                soup.find('meta', attrs={"property": "og:description"}).get("content", "No Company Name Found")
                if soup.find('meta', attrs={"property": "og:description"})
                else "No Company Name Found"
            )

            # Fallback: Check visible text patterns if meta tag is unavailable
            if company_name == "No Company Name Found":
                company_texts = [
                    div.get_text(strip=True) for div in soup.find_all('div') if "Jobs at" in div.get_text(strip=True)
                ]
                if company_texts:
                    company_name = company_texts[0].split("Jobs at")[-1].strip()

            # Prepare output content
            output = (
                f"\nJob Title: {title}\n"
                f"Company: {company_name}\n"
                f"Salary Range: ${min_salary} - ${max_salary} ({salary})\n"
                f"Job Description:\n{description}\n"
            )

            # Print to console
            print(output)

            # Save to file
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(output)
            print(f"Job details saved to '{output_file}'.")
    except Exception as e:
        logging.error(f"Error extracting job data: {str(e)}")

def generate_personalized_resume(raw_resume_file, job_details_file, headshot_path=None):
    try:
        # Read the raw resume text
        with open(raw_resume_file, 'r', encoding='utf-8') as file:
            resume_text = file.read()

        # Read the job details text
        with open(job_details_file, 'r', encoding='utf-8') as file:
            job_details = file.read()

        # Prepare the prompt
        prompt = f"""
        You are an AI assistant specializing in creating resumes. Below is a user's current resume and a job description for which they are applying. Modify the resume to emphasize relevant skills and experience that align with the job description.

        Current Resume:
        {resume_text}

        Job Description:
        {job_details}

        Please provide a personalized version of the resume tailored to this job. Include a 5 sentence description under the contact section for the employer that demonstrates the applicant's knowledge for the industry the application relates to. Do not use specific job titles or company names, as it is supposed to appear as if the applicant 'just so happens' to be best fit for the job. Use keywords from the resume. Make sure to include the job title and company names for education and experience. 
        """

        # Progress bar to simulate processing
        for _ in tqdm(range(100), desc="Generating resume...", ncols=75):
            time.sleep(0.02)  # Simulate delay during API call

        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume-writing assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        # Get the generated resume
        personalized_resume = response.choices[0].message['content'].strip()

        # Extract company name from job details
        with open(job_details_file, 'r', encoding='utf-8') as job_file:
            job_data = job_file.read()
            company_name = "Unknown_Company"
            for line in job_data.splitlines():
                if line.startswith("Company:"):
                    company_name = line.split(":", 1)[1].strip()
                    break

        # Create a new Word document
        doc = Document()

        # Add contact info at the top
        contact_info = (
            "Evan Garaway\n"
            "Dallas & Boise | Real Estate | Marketing Professional | Boise State Alumni Class of ‘24 | 100M+ Views Across Social Media\n"
            "Dallas, Texas, United States\n"
        )
        header = doc.add_paragraph()
        header.add_run(contact_info).bold = True
        header.alignment = 1  # Center align the header

        # Add spacing
        doc.add_paragraph()  # Empty line for better separation

        # Add the headshot to the top-right corner if provided
        if headshot_path and os.path.exists(headshot_path):
            table = doc.add_table(rows=1, cols=2)
            table.autofit = False
            cell_left, cell_right = table.rows[0].cells
            cell_left.width = Inches(5.5)
            cell_right.width = Inches(1.5)

            run = cell_right.paragraphs[0].add_run()
            run.add_picture(headshot_path, width=Inches(1.5))

            # Add resume content to the left cell
            cell_left.text = personalized_resume
        else:
            doc.add_paragraph(personalized_resume)

        # Save the Word document
        output_path = f"C:\\Users\\farsi\\Desktop\\scrips\\{company_name}_resume.docx"
        doc.save(output_path)
        print(f"Resume successfully saved as: {output_path}")

        # Delete temporary files
        if os.path.exists(raw_resume_file):
            os.remove(raw_resume_file)
        if os.path.exists(job_details_file):
            os.remove(job_details_file)
    except Exception as e:
        logging.error(f"Error generating personalized resume: {str(e)}")
        print("Failed to generate a personalized resume.")

def main():
    try:
        # Get user input
        location = input("Enter location: ")
        industry = input("Enter industry: ")
        preferred_salary = input("Enter your preferred salary or hourly rate: ")
        resume_path = input("Enter the path to your resume (PDF format): ")
        headshot_path = input("Enter the path to your headshot image (optional, press Enter to skip): ")
        if not headshot_path.strip():
            headshot_path = None

        # Extract text from the resume
        extract_pdf_text(resume_path)

        # Open Chrome and navigate to the search URL
        driver, search_url = open_chrome_and_go_to_url(location, industry, preferred_salary)

        if driver:
            print("Please manually click on a job listing from the search results.")
            input("Press Enter after you have clicked on a job to view details...")

            # Extract job data from the selected job page
            extract_job_data(driver)

            # Generate a personalized resume
            generate_personalized_resume("raw_resume.txt", "job_details.txt", headshot_path=headshot_path)

            # Redirect back to the Indeed search page
            driver.get(search_url)
            print("Redirected back to the search results page.")
    except Exception as e:
        logging.error(f"General error in main function: {str(e)}")

if __name__ == "__main__":
    main()
