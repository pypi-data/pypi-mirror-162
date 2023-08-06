# Build Python project
change version in pyproject.toml
delete /dist files
python3 -m build

# Upload Python package
python3 -m twine upload --repository testpypi dist/*
python3 -m twine upload dist/*

# Update Local Python Package
pip install rgtracker==000

# Run RedisGears Job
gears-cli run --host localhost --port 6379 src/jobs/bigbang.py REQUIREMENTS rgtracker==000