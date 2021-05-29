echo "Running coverage analysis"
coverage run --source=./ -m unittest discover -s ./ -p "*_test.py"
coverage report -m
echo "Done coverage analysis"