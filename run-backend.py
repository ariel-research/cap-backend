import os
import sys
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

PID_NUM_FILE = os.getenv("PID_NUM_FILE")

if sys.argc == 2:
    command = sys.argv[0]
    if command == 'run':
        # Get the hostname and port from command line arguments
        hostname = os.getenv("HOSTNAME")
        port = os.getenv("PORT_BACKEND")

        # Build the command to run the Django development server
        run_django = f'nohup python3.10 manage.py runserver {hostname}:{port} output.log 2>&1 &'
        save_pid = 'echo $! > save_pid.txt'

        # Run the command using subprocess and redirect the output to a log file
        os.system(run_django)
        os.system(save_pid)

    elif command == 'stop' :
        os.system(f'kill -9 `cat {PID_NUM_FILE}`')
        os.system(f'rm `{PID_NUM_FILE}`')

    else:
        raise Exception("Invalid argument. Usage: ./run-backend.py [run|stop] ")