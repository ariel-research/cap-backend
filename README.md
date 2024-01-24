# cap-backend

### Requirements:
python v3.8.10, pip v20.0.2 , virtualenv v20.23.0, 
gmail account 
1. install pip and venv if needed: \
  `sudo apt install python-pip python-venv`

### Installation:

1. Clone the repository: \
  `git clone https://github.com/ariel-research/cap-backend`
2. Write the command: \
	`cd cap-backend`
3. Create a Python virtual environment for your Django project: \
  `python -m venv venv`
4. Activate the virtual environment: \
  For Linux: `source venv/bin/activate` \
  For Windows: `venv\Scripts\activate`
5. Install Python dependencies for this project: \
  `pip install -r requirements.txt`
6. Create an .env file and customize the project's environment variables. You can see [here](.env-example) an example.
	> Please ensure that you provide proper values for the `DJANGO_SECRET_KEY`, `EMAIL_HOST_USER`, and `EMAIL_HOST_PASSWORD` variables, 	and that your `.gitignore` file includes the `.env` file.
7. Create super user using: \
	`python manage.py createsuperuser`
8. To enable email functionality, you need to set up an email account and generate an app password. \
 [Click here](https://myaccount.google.com/u/5/apppasswords?rapt=AEjHL4PVSRuI1AeFAIqdg6dIjB9A4zziBSL3xoeb7ggmM9kZNb8ZZz-0GkY9PnOa7OnM5Ge1g1mt02nZYo5vdZYenIA13zjbJg) to set a password for a **Gmail** account.
9. Run Django development server:    	
	1. To run the project on the default address (localhost:8000):
	    1. Start the Django development server using the following command: \
		`python manage.py runserver`
	    2. Open `http://localhost:8000/admin/` in a web browser to view your application.
	2. To run the project on a different address:
	    1. Start the Django development server using the following command: \
		`python manage.py runserver <your-hostname>:<port-number>`
	    2. Open `http://<your-hostname>:<port-number>/admin/` in a web browser to view your application.
10. Insert your super user information has been created for Django.
11. Now you can examine the database.
12. Optional: for running Django with Gunicorn (and React app with Nginx) follow [this](https://austinogiza.medium.com/deploying-react-and-django-rest-framework-with-nginx-and-gunicorn-7a0553459500) guide.
