# Build Python project
python3 -m build

# Upload Python package
python3 -m twine upload --repository testpypi dist/*
python3 -m twine upload --repository dist/*

# Run RedisGears Job
gears-cli run --host localhost --port 6379 src/rgtracker/example.py REQUIREMENTS rgtracker