import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the hostname and port from command line arguments
hostname = os.getenv("HOSTNAME")
port = os.getenv("PORT_BACKEND")

# Build the command to run the Django development server
run_django = f'nohup python manage.py runserver {hostname}:{port} &'

# Activate the virtual environment
venv_activate = 'source venv/bin/activate'

# Build the full command
command = f'{venv_activate} && {run_django}'

# Run the command using subprocess and redirect the output to a log file
#subprocess.Popen(command, shell=True, stdout=open('backend.log', 'w'), stderr=subprocess.STDOUT)
os.system(command)
