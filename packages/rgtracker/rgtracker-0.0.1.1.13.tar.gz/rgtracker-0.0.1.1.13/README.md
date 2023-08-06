# Build Python project
change version in pyproject.toml
delete /dist files
python3 -m build

# Upload Python package
python3 -m twine upload --repository testpypi dist/*
python3 -m twine upload dist/*

# Update Local Python Package
pip install rgtracker==0.0.1.1.13

# Run RedisGears Jobs
python src/jobs/produce.py 
python src/jobs/axiom.py 
gears-cli run --host localhost --port 6379 src/jobs/bigbang.py REQUIREMENTS rgtracker==0.0.1.1.13
gears-cli run --host localhost --port 6379 src/jobs/megastar.py REQUIREMENTS rgtracker==0.0.1.1.13 pandas
gears-cli run --host localhost --port 6379 src/jobs/megastorm.py REQUIREMENTS rgtracker==0.0.1.1.13 pandas