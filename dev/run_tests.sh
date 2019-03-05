echo "Setting up test environment..."

docker-compose -f dev/test_env/docker-compose.yml up  -d

echo "Running tests"

until curl localhost:8001 -sf > /dev/null; do
    echo "Waiting for Kong to be ready";
    sleep 1
done

pytest --cov

echo "Removing test environment"

docker-compose -f dev/test_env/docker-compose.yml down -v
