# cap-backend

### Requirements:
python v3.8.10, pip v20.0.2 , virtualenv v20.23.0, 
gmail account \
1. install pip and venv if needed: \
  `sudo apt install python-pip python-venv`

### Installation:

1. Clone the repository: \
  `git clone https://github.com/ariel-research/cap-backend`
2. Write the command: \
	`cd cap-backend`
3. Switch to 'ariel' branch: \
  `git checkout ariel`
4. Create a Python virtual environment for your Django project: \
  `python -m venv venv`
5. Activate the virtual environment: \
  For Linux: `source venv/bin/activate` \
  For Windows: `venv\Scripts\activate`
6. Install Python dependencies for this project: \
  `pip install -r requirements.txt`
7. Create super user using: \
	`python manage.py createsuperuser`
8. Set up a gmail account app password [here](https://myaccount.google.com/u/5/apppasswords?rapt=AEjHL4PVSRuI1AeFAIqdg6dIjB9A4zziBSL3xoeb7ggmM9kZNb8ZZz-0GkY9PnOa7OnM5Ge1g1mt02nZYo5vdZYenIA13zjbJg)
9. Open cap/settings.py file, and add the following settings: \
	`EMAIL_HOST_USER = '<your@gmail.com>'` \
	`EMAIL_HOST_PASSWORD = '<app-password>'`
10. Start the Django development server by command: \
	`python manage.py runserver` 
11. Open http://127.0.0.1:8000/admin/ in a web browser to view your application.
12. Insert your super user information has been created for Django.
13. Now you can examine the database.
