# sample_project
This is a template project, you need to do the following to generate your project: 
- Text replacement: "sample_project" to "${your_project_name}"
- Text replacement: "sample-project" to "${your-project-name}"
- Text replacement: "./src/sample_project" to "./src/${your_project_name}"
- Edit "./src/${your_project_name}/\__version__.py"

## Prepare
### 1. Install the pip3 from https://pypi.org/project/pip/
### 2. Install the twine (publish)
```
pip3 install twine
```

## Commands
### 1. Install to environment:
```
pip3 install -r requirements-dev.txt
```
### 2. Packcge:
```
python3 setup.py sdist bdist_wheel
```
### 3. Packcge and Upload:
```
python3 setup.py sdist bdist_wheel
twine upload dist/*
```