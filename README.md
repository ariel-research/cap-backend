# cap-backend

### Requirements:
python v3.8.10, pip v20.0.2 , virtualenv v20.23.0

1. install pip and venv if needed: \
  `sudo apt install python-pip python-venv`

### Installation:

1. Clone the repository: \
  `git clone https://github.com/ariel-research/cap-backend`
2. Switch to 'ariel' branch: \
  `git checkout ariel`
3. Write the command: \
	`cd cap-backend`
4. Create a Python virtual environment for your Django project: \
  `python -m venv venv`
5. Activate the virtual environment: \
  For Linux: `source venv/bin/activate` \
  For Windows: `venv\Scripts\activate`
6. Install Python dependencies for this project: \
  `pip install -r requirements.txt`
7. Create super user using: \
	`python manage.py createsuperuser`
8. Start the Django development server by command: \
	`python manage.py runserver` 
9. Open http://127.0.0.1:8000/admin/ in a web browser to view your application.
10. Insert your super user information has been created for Django.
11. Now you can examine the database.
