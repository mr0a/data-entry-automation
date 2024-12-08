import pdfplumber
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import logging
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='data_entry_automation.log'
)

class DataEntryAutomation:
    def __init__(self, pdf_path, website_url):
        self.pdf_path = pdf_path
        self.website_url = website_url
        self.driver = None
        self.data = []
    
    def extract_data_from_pdf(self):
        """
        Extract data from PDF file.
        Modify the extraction logic based on your PDF structure.
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    # Extract tables from the page
                    tables = page.extract_tables()
                    
                    for table in tables:
                        # Skip header row if present
                        for row in table[1:]:  # Modify slice based on your PDF structure
                            # Clean and validate data
                            cleaned_row = [str(cell).strip() if cell else '' for cell in row]
                            if any(cleaned_row):  # Skip empty rows
                                self.data.append(cleaned_row)
            
            logging.info(f"Successfully extracted {len(self.data)} rows from PDF")
            return True
            
        except Exception as e:
            logging.error(f"Error extracting data from PDF: {str(e)}")
            return False
    
    def setup_browser(self):
        """
        Initialize the web browser with appropriate settings
        """
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-notifications')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.get(self.website_url)
            logging.info("Browser setup successful")
            return True
            
        except Exception as e:
            logging.error(f"Error setting up browser: {str(e)}")
            return False
    
    def login_to_website(self, username, password):
        """
        Login to the website. Modify selectors based on the website structure.
        """
        try:
            # Wait for username field and enter credentials
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(username)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.ID, "login-button")
            login_button.click()
            
            # Wait for successful login
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "dashboard"))  # Modify selector
            )
            
            logging.info("Successfully logged into the website")
            return True
            
        except TimeoutException:
            logging.error("Timeout while trying to log in")
            return False
        except Exception as e:
            logging.error(f"Error during login: {str(e)}")
            return False
    
    def enter_data_row(self, row_data):
        """
        Enter a single row of data into the web form.
        Modify field selectors based on your web form structure.
        """
        try:
            # Wait for the form to be ready
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "data-entry-form"))
            )
            
            # Example: Fill in form fields
            # Modify these selectors and field names according to your form
            field_mappings = {
                "field1": row_data[0],
                "field2": row_data[1],
                "field3": row_data[2],
                # Add more fields as needed
            }
            
            for field_id, value in field_mappings.items():
                field = self.driver.find_element(By.ID, field_id)
                field.clear()
                field.send_keys(value)
            
            # Submit the form
            submit_button = self.driver.find_element(By.ID, "submit-button")
            submit_button.click()
            
            # Wait for success message or next form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Error entering data row: {str(e)}")
            return False
    
    def process_all_data(self):
        """
        Process all extracted data rows
        """
        success_count = 0
        error_count = 0
        
        for index, row in enumerate(self.data, 1):
            try:
                if self.enter_data_row(row):
                    success_count += 1
                    logging.info(f"Successfully entered row {index}")
                else:
                    error_count += 1
                    logging.error(f"Failed to enter row {index}")
                
                # Add a small delay between entries to avoid overwhelming the server
                time.sleep(1)
                
            except Exception as e:
                error_count += 1
                logging.error(f"Error processing row {index}: {str(e)}")
        
        return success_count, error_count
    
    def cleanup(self):
        """
        Clean up resources
        """
        if self.driver:
            self.driver.quit()
            logging.info("Browser session closed")
    
    def run_automation(self, username, password):
        """
        Run the complete automation process
        """
        try:
            if not self.extract_data_from_pdf():
                raise Exception("Failed to extract data from PDF")
            
            if not self.setup_browser():
                raise Exception("Failed to set up browser")
            
            if not self.login_to_website(username, password):
                raise Exception("Failed to log in to website")
            
            # success_count, error_count = self.process_all_data()
            
            # logging.info(f"""
            # Automation completed:
            # - Total rows processed: {len(self.data)}
            # - Successful entries: {success_count}
            # - Failed entries: {error_count}
            # """)
            
        except Exception as e:
            logging.error(f"Automation failed: {str(e)}")
        
        finally:
            self.cleanup()

# Usage example
if __name__ == "__main__":
    # Configuration
    PDF_PATH = "./patient-line-list-28-Nov-uphczambazar.pdf"
    WEBSITE_URL = "https://mtmlinelist.tn.gov.in/Login"
    USERNAME = "PHC_1481"
    PASSWORD = "121635"
    
    # Create and run automation
    automation = DataEntryAutomation(PDF_PATH, WEBSITE_URL)
    automation.run_automation(USERNAME, PASSWORD)