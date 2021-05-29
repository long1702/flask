set -e
chmod 777 ./scripts/run_unit_tests.sh
chmod 777 ./scripts/run_integration_tests.sh

./scripts/run_unit_tests.sh
./scripts/run_integration_tests.sh
