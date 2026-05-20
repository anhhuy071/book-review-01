# PowerShell helper to run Flask with debug + reload
$env:FLASK_APP = "application"
$env:FLASK_DEBUG = "1"
python -m flask --app application --debug run --reload
