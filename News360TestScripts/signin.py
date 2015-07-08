import time
import unittest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class EmailSignInTestCase(unittest.TestCase):

	def setUp(self):
		self.chrome_path = os.environ.get("CHROMEPATH")
		self.opts = Options()
		self.opts.binary_location = self.chrome_path
		self.driver = webdriver.Chrome(chrome_options = self.opts)
		self.driver.get('http://www.news360.com')
		self.driver.find_element_by_class_name("startreading").click()
		self.popup = self.driver.find_element_by_class_name("simplepopup")
		self.popup.find_element_by_link_text("Sign in with email").click()

	def tearDown(self):
		self.driver.close()

	def test_SignUpEmptyFields(self):
		self.popup.find_element_by_link_text("Sign up").click()
		self.signup_form = self.popup.find_element_by_css_selector("form.signup.ng-pristine.ng-valid")
		self.assertTrue(self.signup_form.is_displayed())
		self.signup_email = self.signup_form.find_element_by_class_name("email")
		self.signup_password = self.signup_form.find_element_by_class_name("password")
		self.signup_confirmpassword = self.signup_form.find_element_by_class_name("confirmpassword")
		self.signup_email.clear()
		self.signup_password.clear()
		self.signup_confirmpassword.clear()
		time.sleep(1)

if __name__ == "__main__":
	unittest.main()