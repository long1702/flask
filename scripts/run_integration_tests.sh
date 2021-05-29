set -e

echo "Running Integration tests"

chmod 777 ./scripts/run_service.sh

chmod 777 ./scripts/wait_for_it.sh

./scripts/run_service.sh &


./scripts/wait_for_it.sh -t 15 localhost:4000 -- echo "Start running integration tests python ..." && python -m unittest discover -s ./ -p "*_itest.py"


echo "Done integration tests."