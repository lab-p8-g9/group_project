Part 2 Project

IO_manager/io_manager.py is our main program to be run.
To run the file in docker, under if __name__ == '__main__': in the said main file, 
change app.run(host="127.0.0.1"....) to just "0.0.0.0 in order for it to run. 

The relevant test files for each managers in inside each managers' files with the filename containing
test in it.

Docker build: docker build -t inf1103_project_part2 .

For main program: docker run --rm -p 8080:8080 --env-file .env inf1103_project_part2 

For automated test script: 

docker run --rm inf1103_project_part2 python -m unittest IO_manager/io_test.py

docker run --rm inf1103_project_part2 python Logic_manager/logic_test_script.py

docker run --rm inf1103_project_part2 python -m Logic_manager.valid_sample_script

docker run --rm inf1103_project_part2 python -m Logic_manager.invalid_sample_script

docker run --rm inf1103_project_part2 python -c "from AI_manager.ai_test import test_offline_ai; test_offline_ai()"

github repo link: https://github.com/lab-p8-g9/group_project
