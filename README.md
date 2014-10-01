YAAS_project
============

This is a project to learn how to use Django to developp web applications and webservices. 

UC1: Create an user account
	URL: /regiter/
	Scenario: The user can create an account by filling a form with these informations:
		+ fisrt name
		+ last name
		+ username (mandatory) -> Should not be empty
		+ email adress
		+ password (mandatory) -> Should not be empty
		+ password confirmation ( should be the same with password specify before)
	1. If the username or password is not fill then (inform the user than these filled are mandatory)
	2. If the password confirmation and the initial password are not the same, inform the user that they are not the same (in real time)
	3. If a user with the same username exists in the database then inform the user that the username already exist
	4. If the address mail does not match an adress mail format the inform the user that his adress contain errors

	When the user account is created, the user is directly redirected to his profile page where he can see his all his account informations. 


UC2: Edit account information
	URL: /edit/ 
	Scénario : A logged in user can change his/her email address and password

	1. If a non logged in user try to access /edit/ he is directly redirected to the sign in page
	2. In the edit profile page , the user can see his current email ; the password field is blank, same for the confirmation one.
	3. password (mandatory) -> Should not be empty
	4.If all the informations are good then redirect the user to his profil page where he can see his new informations

