import os
import time
import pandas as pd
import threading
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from datetime import datetime
# Assuming config.py and xpath.py are in the same directory
from config import CONFIG
from xpath import *

class WhatsAppBulkSender:
    def __init__(self):
        self.driver = None
        self.config = CONFIG
        self.is_active = False
        self.current = 0
        self.total = 0
        self.success_count = 0
        self.failure_count = 0
        self.logs = []
        self.thread = None

    def add_log(self, message, log_type="info"):
        """Add a log entry with a timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        # Also log to the console/file for debugging
        if log_type == "error":
            logging.error(message)
        else:
            logging.info(message)

    def initialize_driver(self):
        """Initialize Chrome WebDriver with profile support."""
        self.add_log("Initializing Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        
        user_data_dir = self.config.get('user_data_dir', '')
        profile_name = self.config.get('profile_name', 'Default')
        
        if user_data_dir and os.path.exists(user_data_dir):
            profile_path = os.path.join(user_data_dir, profile_name) if profile_name != 'Default' else user_data_dir
            options.add_argument(f'--user-data-dir={profile_path}')
            self.add_log(f"Using Chrome profile: {profile_path}")
        
        # Standard Chrome options for automation
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.add_log("Chrome WebDriver initialized successfully.")
            return True
        except Exception as e:
            self.add_log(f"Failed to initialize WebDriver: {str(e)}", "error")
            return False

    def login_to_whatsapp(self):
        """Login to WhatsApp Web, waiting for QR scan if needed."""
        self.add_log("Connecting to WhatsApp Web...")
        try:
            self.driver.get('https://web.whatsapp.com')
            
            # Check if we are already logged in by looking for the main app interface
            try:
                WebDriverWait(self.driver, self.config['login_timeout']).until(
                    EC.presence_of_element_located((By.XPATH, PANE_SIDE_XPATH))
                )
                self.add_log("Using existing WhatsApp session.")
                return True
            except TimeoutException:
                self.add_log("No existing session found. Please scan the QR code.")
            
            # If not logged in, wait for the user to scan the QR code
            try:
                WebDriverWait(self.driver, 120).until(  # Give 2 minutes for QR scan
                    EC.presence_of_element_located((By.XPATH, PANE_SIDE_XPATH))
                )
                self.add_log("Login successful!")
                return True
            except TimeoutException:
                self.add_log("Login timed out. Please restart the application and try again.", "error")
                return False
        except Exception as e:
            self.add_log(f"An unexpected error occurred during login: {str(e)}", "error")
            return False

    def load_recipient_data(self, file_path):
        """Load and clean recipient data from an Excel file."""
        self.add_log(f"Loading recipients from {os.path.basename(file_path)}...")
        try:
            df = pd.read_excel(file_path)
            
            # Find the column with contact numbers (flexible matching)
            contact_column = None
            for col in df.columns:
                if any(keyword in col.strip().lower() for keyword in ['contact', 'phone', 'number']):
                    contact_column = col
                    break
            
            if not contact_column:
                contact_column = df.columns[0] # Fallback to the first column
                self.add_log(f"Warning: No 'contact' column found. Using first column '{contact_column}'.")

            df.rename(columns={contact_column: 'Contact'}, inplace=True)
            df['Contact'] = df['Contact'].astype(str).str.replace(r'\D', '', regex=True)
            
            if 'Message' not in df.columns:
                df['Message'] = ''
            df['Message'] = df['Message'].fillna('').astype(str)
            
            df.dropna(subset=['Contact'], inplace=True)
            df = df[df['Contact'].str.strip() != '']

            self.add_log(f"Successfully loaded {len(df)} valid recipients.")
            return df
        except Exception as e:
            self.add_log(f"Error loading recipient data: {str(e)}", "error")
            raise

    def send_message(self, contact, message, attachment_path=None):
        self.add_log(f"Attempting to send message to {contact}...")
        try:
            self.add_log(f"Opening chat with {contact}...")
            self.driver.get(f'https://web.whatsapp.com/send?phone={contact}')
            wait = WebDriverWait(self.driver, self.config['chat_load_timeout'])
            try:
                WebDriverWait(self.driver, self.config['chat_load_timeout']).until(EC.any_of(
                    EC.presence_of_element_located((By.XPATH, CHAT_INPUT_BOX_XPATH)),
                    EC.presence_of_element_located((By.XPATH, CHAT_INVALID_NUMBER_XPATH))
                ))
            except TimeoutException:
                self.add_log("Chat loading timed out, proceeding anyway")

            invalid_number = self.driver.find_elements(By.XPATH, CHAT_INVALID_NUMBER_XPATH)
            if invalid_number:
                self.add_log(f"Error: {contact} is not registered on WhatsApp")
                return False

            try:
                input_box = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, CHAT_INPUT_BOX_XPATH)
                ))
            except TimeoutException:
                self.add_log("Error: Could not find message input area")
                return False

            if attachment_path:
                if not self._send_attachment(attachment_path, message):
                    return False
            elif message:
                if not self._send_text_message(message):
                    return False

            try:
                WebDriverWait(self.driver, self.config['message_send_timeout']).until(
                    EC.presence_of_element_located((By.XPATH, CHAT_INPUT_BOX_XPATH))
                )
                self.add_log(f"✓ Message sent successfully to {contact}")
                return True
            except TimeoutException:
                self.add_log("Warning: Message send confirmation not detected")
                return True

        except Exception as e:
            self.add_log(f"Critical error sending to {contact}: {str(e)}")
            return False


    def _send_attachment(self, file_path, caption):
        """Helper function to handle the attachment upload process."""
        try:
            clip_btn = WebDriverWait(self.driver, self.config['chat_load_timeout']).until(
                EC.element_to_be_clickable((By.XPATH, ATTACH_BUTTON_XPATH))
            )
            clip_btn.click()

            file_input = self.driver.find_element(By.XPATH, FILE_INPUT_XPATH)
            file_input.send_keys(os.path.abspath(file_path))

            try:
                WebDriverWait(self.driver, self.config['upload_timeout']).until(
                    EC.presence_of_element_located((By.XPATH, SEND_BUTTON_XPATH))
                )
            except TimeoutException:
                self.add_log("Error: Attachment upload took too long")
                self.driver.find_element(By.XPATH,CLOSE_BUTTON_XPATH).click()
                self.add_log("Attachment upload cancelled")
                return False

            ext = os.path.splitext(file_path)[1].lower()
            if ext in ('.jpg', '.jpeg', '.png', '.gif', '.mp4','.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt') and caption:
                caption_box = self.driver.find_element(By.XPATH, CAPTION_BOX_XPATH)
                caption_box.send_keys(caption)

            send_btn = self.driver.find_element(By.XPATH, SEND_BUTTON_XPATH)
            send_btn.click()
            time.sleep(self.config['delay_between_messages'])
            return True

        except Exception as e:
            self.add_log("Attachment sending failed")
            self.add_log(f"Attachment error: {str(e)}")
            return False

    def _send_text_message(self, message):
        """Helper function to send a simple text message."""
        try:
            text_box = self.driver.find_element(By.XPATH, CHAT_INPUT_BOX_XPATH)
            
            # Use CTRL+A and DELETE to clear any pre-existing text (like a replied quote)
            text_box.send_keys(Keys.CONTROL + "a")
            text_box.send_keys(Keys.DELETE)
            
            # Handle multiline messages correctly
            for line in message.split('\n'):
                text_box.send_keys(line)
                text_box.send_keys(Keys.SHIFT, Keys.ENTER) # Create a new line
            
            text_box.send_keys(Keys.ENTER) # Send the message
            time.sleep(self.config.get('delay_between_messages', 1))
            return True
        except Exception as e:
            self.add_log(f"Failed to send text message: {str(e)}", "error")
            return False

    def process_recipients(self, recipients_df, attachment_path=None):
        """Processes all recipients in a separate thread to keep the UI responsive."""
        def _process():
            self.is_active = True
            self.current = 0
            self.total = len(recipients_df)
            self.success_count = 0
            self.failure_count = 0
            self.logs = []
            
            self.add_log(f"Starting to process {self.total} recipients...")
            
            if not self.initialize_driver() or not self.login_to_whatsapp():
                self.add_log("Setup failed. Halting process.", "error")
                self.is_active = False
                return

            for index, row in recipients_df.iterrows():
                if not self.is_active:
                    self.add_log("Process stopped by user.")
                    break
                    
                contact = str(row['Contact']).strip()
                message = str(row['Message']).strip()
                
                if not contact:
                    continue
                
                self.current = index + 1
                
                success = False
                for attempt in range(self.config['max_retries']):
                    if self.send_message(contact, message, attachment_path):
                        success = True
                        break # Exit retry loop on success
                    else:
                        self.add_log(f"Attempt {attempt + 1} failed for {contact}. Retrying...", "warning")
                        if attempt < self.config['max_retries'] - 1:
                            time.sleep(3) # Wait before the next retry
                
                if success:
                    self.success_count += 1
                else:
                    self.failure_count += 1
                    self.add_log(f"All retries failed for contact {contact}.", "error")
            
            self.add_log(f"Process completed! Success: {self.success_count}, Failed: {self.failure_count}")
            self.is_active = False
            if self.driver:
                self.driver.quit()
                self.driver = None
        
        self.thread = threading.Thread(target=_process, daemon=True)
        self.thread.start()

    def get_progress(self):
        """Returns the current progress for the UI."""
        return {
            'is_active': self.is_active,
            'current': self.current,
            'total': self.total,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'logs': self.logs.copy()
        }

    def stop_process(self):
        """Stops the sending process."""
        self.add_log("Stop signal received. Halting after the current operation...")
        self.is_active = False
