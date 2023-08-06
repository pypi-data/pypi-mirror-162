# Example Package

This is a simple example package. You can use
[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.

# Notes
python3 -m pip install --upgrade build
python3 -m build
python3 -m pip install --upgrade twine
python3 -m twine upload --repository testpypi dist/*


python3 -m twine upload --repository dist/*


python3 -m pip install --index-url https://test.pypi.org/simple/ your-package
python3 -m pip download --only-binary :all: --dest . --no-cache --index-url https://test.pypi.org/simple/ rgtracker==0.0.1
python3 -m pip wheel 'rgtracker-0.0.1-py3-none-any.whl'

gears-cli run --host localhost --port 6379 src/rgtracker/example.py REQUIREMENTS


--extra-index-url https://test.pypi.org/simple/ rgtracker==0.0.1

docker cp rgtracker-0.0.1-py3-none-any.whl b1066aa1076b:/var/opt/redislabs/modules/rg/python3/rgtracker-0.0.1-py3-none-any.whl