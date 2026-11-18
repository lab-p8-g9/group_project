Part 2 Project

IO_manager/io_manager.py is our main program to be run.
To run the file in docker, under if __name__ == '__main__': in the said main file, 
change app.run(host="127.0.0.1" to just "0.0.0.0 in order for it to run. 

The relevant test files for each managers in inside each managers' files with the filename containing
test in it.

use - docker run --rm -p 8080:8080 --env-file .env inf1103_project_part2 python -m IO_manager.io_manager - to run the system on decker.