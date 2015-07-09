import time
import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EmailSignInTestCase(unittest.TestCase):

	def setUp(self):
		self.my_email = os.environ.get("MY_EMAIL")
		self.my_pw = os.environ.get("MY_PW")
		self.chrome_path = os.environ.get("CHROMEPATH")
		self.opts = Options()
		self.opts.binary_location = self.chrome_path
		self.driver = webdriver.Chrome(chrome_options = self.opts)
		self.driver.get('http://www.news360.com')
		self.driver.find_element_by_class_name("startreading").click()
		self.init_vars()

	def tearDown(self):
		self.driver.quit()

	def test_SignUpEmptyFields(self):
		self.navigateToSignUpForm()
		self.signup_button.click()
		self.error_messages = self.signup_form.find_elements_by_class_name("required")
		self.assertTrue(len(self.error_messages) == 3)

	def test_InvalidSignUpEmailFormatCheck(self):
		self.navigateToSignUpForm()
		#check if invalid email formats trigger error message
		self.invalidEmails = ["xyz", "xyz@abc@com", "xyz.abc.com", "xyz@abc", "xyz@abc.123", "xyz abc", "xyz,abc",
			"\"xyz@abc.com","xyz2\"abc\"@gggg.com"]
		for self.emailStrings in self.invalidEmails:
			self.signup_email.send_keys(self.emailStrings)
			self.signup_button.click()			
			self.error_messages = self.signup_form.find_elements_by_class_name("type")
			self.assertTrue(len(self.error_messages) == 1)
			self.assertTrue("parsley-error" in self.signup_email.get_attribute("class"))
			self.signup_email.clear()
		#check if valid email formats wipes the error message
		self.validEmails = ["x.y_z-123@abc456.com", "\"xyz\"@abc123.com"]
		for self.emailStrings in self.validEmails:
			self.signup_email.send_keys(self.emailStrings)
			self.signup_button.click()			
			self.assertTrue("parsley-success" in self.signup_email.get_attribute("class"))
			self.signup_email.clear()

	def test_SignUpPasswordTooShort(self): 
		self.navigateToSignUpForm()
		#check if sign up passwords that are too short trigger error message
		self.signup_password.send_keys("short")
		self.signup_button.click()
		self.error_messages = self.signup_form.find_elements_by_class_name("minlength")
		self.assertTrue(len(self.error_messages) == 1)
		self.signup_password.clear()
		#check if sign up passwords that are valid wipes the error message
		self.signup_password.send_keys("short1")
		self.assertTrue("parsley-success" in self.signup_password.get_attribute("class"))

	def test_SignUpDifferentConfirmPassword(self): 
		self.navigateToSignUpForm()
		#check if sign up confirm password that does not match triggers error message
		self.signup_password.send_keys("asdfasdf")
		self.signup_confirmpassword.send_keys("asdfas")
		self.signup_button.click()
		self.error_messages = self.signup_form.find_elements_by_class_name("equalto")
		self.assertTrue(len(self.error_messages) == 1)
		self.signup_confirmpassword.clear()
		#check if same sign up confirm password wipes the error message
		self.signup_confirmpassword.send_keys("asdfasdf")
		self.assertTrue("parsley-success" in self.signup_confirmpassword.get_attribute("class"))

	def test_CompleteSignUp(self):
		self.navigateToSignUpForm()
		try:
			self.signUpWithEmail(self.my_email, self.my_pw)
			self.assertTrue(self.driver.title == "News360")
		finally:
			self.deleteAccount(self.my_pw)

	def test_SignUpAndSignInWithExistingEmail(self):
		self.navigateToSignUpForm()
		try:
			self.signUpWithEmail(self.my_email, self.my_pw)
			self.logout()
			self.driver.find_element_by_class_name("startreading").click()
			self.init_vars()
			self.navigateToSignUpForm()			
			self.signup_email.send_keys(self.my_email)
			self.signup_password.send_keys(self.my_pw)
			self.signup_confirmpassword.send_keys(self.my_pw)
			self.signup_button.click()
			#checks if error message appears
			self.error_messages = self.popup.find_elements_by_class_name("error-message")
			self.assertTrue(len(self.error_messages) == 1)
		finally:
			self.signup_cancel.click()
			self.popup.find_element_by_link_text("Sign in with email").click()
			self.signIn(self.my_email,self.my_pw)
			self.assertTrue(self.driver.title == "News360")
			self.deleteAccount(self.my_pw)

	def test_signInWithNewEmail(self):
		self.signin_email.send_keys(self.my_email)
		self.signin_password.send_keys(self.my_pw)
		self.signin_button.click()
		#checks if error message appears
		self.error_messages = self.popup.find_elements_by_class_name("error-message")
		self.assertTrue(len(self.error_messages) == 1)

	def test_signInWithWrongPassword(self):
		try:
			self.navigateToSignUpForm()
			self.signUpWithEmail(self.my_email, self.my_pw)
			self.logout()
			self.driver.find_element_by_class_name("startreading").click()
			self.init_vars()
			self.signin_email.send_keys(self.my_email)
			self.signin_password.send_keys(self.my_pw + "asdf")
			self.signin_button.click()
			#checks if error message appears
			self.error_messages = self.popup.find_elements_by_class_name("error-message")
			self.assertTrue(len(self.error_messages) == 1)
		finally:
			self.signIn(self.my_email,self.my_pw)
			self.assertTrue(self.driver.title == "News360")
			self.deleteAccount(self.my_pw)

	def test_signInWithInvalidEmailFormat(self):
		#test signing in with empty email
		self.signin_button.click()
		self.error_messages = self.signin_form.find_elements_by_class_name("required")
		self.assertTrue(len(self.error_messages) == 1)
		#test signing in with invalid email format
		self.invalidEmails = ["xyz", "xyz@abc@com", "xyz.abc.com", "xyz@abc", "xyz@abc.123", "xyz abc", "xyz,abc",
			"\"xyz@abc.com","xyz2\"abc\"@gggg.com"]
		for self.emailStrings in self.invalidEmails:
			self.signin_email.send_keys(self.emailStrings)
			self.signin_button.click()			
			self.error_messages = self.signin_form.find_elements_by_class_name("type")
			self.assertTrue(len(self.error_messages) == 1)
			self.assertTrue("parsley-error" in self.signin_email.get_attribute("class"))
			self.signin_email.clear()
		#check if valid email formats wipes the error message
		self.validEmails = ["x.y_z-123@abc456.com", "\"xyz\"@abc123.com"]
		for self.emailStrings in self.validEmails:
			self.signin_email.send_keys(self.emailStrings)
			self.signin_button.click()			
			self.assertTrue("parsley-success" in self.signin_email.get_attribute("class"))
			self.signin_email.clear()

	def test_forgetPasswordAndSignIn(self):
		try:
			self.navigateToSignUpForm()
			self.signUpWithEmail(self.my_email, self.my_pw)
			self.logout()
			self.driver.find_element_by_class_name("startreading").click()
			self.init_vars()

			self.navigateToForgetPasswordForm()
			#forget and sign in
			self.reset_email.send_keys(self.my_email)
			self.reset_button.click()
		finally:
			self.popup.find_element_by_class_name("close").click()
			self.driver.get('http://www.news360.com')
			self.driver.find_element_by_class_name("startreading").click()		
			self.init_vars()	
			self.signIn(self.my_email,self.my_pw)
			self.assertTrue(self.driver.title == "News360")
			#delete account		
			self.deleteAccount(self.my_pw)

	def navigateToSignUpForm(self):	#helper method to navigate to the sign up form through the popup and set up variables for important elements	
		self.popup.find_element_by_link_text("Sign up").click()
		self.signup_form = self.popup.find_element_by_css_selector("form.signup.ng-pristine.ng-valid")
		self.signup_email = self.signup_form.find_element_by_class_name("email")
		self.signup_password = self.signup_form.find_element_by_class_name("password")
		self.signup_confirmpassword = self.signup_form.find_element_by_class_name("confirmpassword")
		self.signup_button = self.signup_form.find_element_by_class_name("signup-button")
		self.signup_cancel = self.signup_form.find_element_by_class_name("cancel-button")
		self.signup_email.clear()
		self.signup_password.clear()
		self.signup_confirmpassword.clear()

	def navigateToForgetPasswordForm(self): #helper method to navigate to the forget password form from the popup box
		self.popup.find_element_by_link_text("Forgot your password?").click()
		self.reset_password_form = self.popup.find_element_by_css_selector("form.resetpassword.ng-pristine.ng-valid")
		self.reset_email = self.reset_password_form.find_element_by_class_name("email")
		self.reset_button = self.reset_password_form.find_element_by_class_name("reset-button")

	def signUpWithEmail(self, email, password): #helper method to sign up with a valid email and password
		self.signup_email.send_keys(email)
		self.signup_password.send_keys(password)
		self.signup_confirmpassword.send_keys(password)
		self.signup_button.click()
		WebDriverWait(self.driver,10).until(EC.title_is("News360")) #TODO: raise exception when timeout
		self.driver.find_element_by_class_name("startReading").click()
		WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"a.user.default"))) #TODO: raise exception when timeout

	def deleteAccount(self, password): #helper to ensure that an account is properly deleted 
		self.driver.find_element_by_css_selector("a.user.default").click()
		WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"div.ebutton.delete.start.ng-binding")))
		self.driver.find_element_by_css_selector("div.ebutton.delete.start.ng-binding").click()
		self.driver.find_element_by_css_selector("div.dropdown-list.settings-popup.delete_account.start").find_element_by_class_name("delete").click()
		self.delete_confirm_pw = self.driver.find_element_by_class_name("confirmpassword").find_element_by_tag_name("input")
		self.delete_confirm_pw.click()
		self.delete_confirm_pw.send_keys(password)
		self.driver.find_element_by_css_selector("div.dropdown-list.settings-popup.delete_account.permanently").find_element_by_class_name("delete").click()
		WebDriverWait(self.driver,10).until(EC.title_is("News360: Your personalized news reader app"))

	def signIn(self, email, password): #helper method to sign in with a given valid email and password
		WebDriverWait(self.driver,10).until(lambda x : self.signin_button.is_enabled())
		self.signin_email.clear()
		self.signin_password.clear()
		self.signin_email.send_keys(email)
		self.signin_password.send_keys(password)
		self.signin_button.click()
		WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"a.user.default"))) #TODO: raise exception when timeout

	def logout(self): #helper method to logout a user
		self.driver.find_element_by_css_selector("a.user.default").click()
		WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CLASS_NAME,"logout")))
		self.driver.find_element_by_class_name("logout").click()
		WebDriverWait(self.driver,10).until(EC.title_is("News360: Your personalized news reader app"))

	def init_vars(self): #helper method to initialize variables for the sign in form
		WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT,"Sign in with email")))
		self.popup = self.driver.find_element_by_class_name("simplepopup")
		self.popup.find_element_by_link_text("Sign in with email").click()
		self.signin_form = self.popup.find_element_by_css_selector("form.signin.ng-pristine.ng-valid")
		self.signin_email = self.signin_form.find_element_by_class_name("email")
		self.signin_password = self.signin_form.find_element_by_class_name("password")
		self.signin_button = self.signin_form.find_element_by_class_name("signin-button")
		self.signin_cancel = self.signin_form.find_element_by_class_name("cancel-button")

if __name__ == "__main__":
	unittest.main()