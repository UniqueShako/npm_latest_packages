# npm_latest_packages
A simple Python program that queries the Libraries.io api to pull down the latest published and updated NPM packages


NOTE: THIS PROGRAM WILL NOT WORK IF YOU DO NOT HAVE A LIBRARIES.IO API KEY AND HAVE IT INSERTED INTO THE api_key VARIABLE ON LINE 21. SEE BELOW ON HOW TO OBTAIN API KEY

This program queries the libraries.io API for new and newly updated NPM packages for today. It then takes the package name, date published, and version number and adds them to a CSV file
in the current directory. If the CSV file does not exist it will be created automatically. Finally it will remove duplicate entries from the CSV file and output the _final CSV file.

To run this program yourself you will need a libraries.io API key, which can be obtained by signing up for a free libraries.io account and checking your account settings page.
This program depends on the "requests" library which you may need to install using "pip install requests"

This may take several minutes to run depending on how much load is being put on the libraries.io servers. It will handle errors and wait 2 minutes between each error code returned from the server.

If it encounters 10 error messages over the course of running, the program will clean up duplicates and end. You can try messing with the error threshold if you're not getting enough results. The libraries.io API is unstable and will return 502 bad gateway errors at some points. I haven't been able to determine a pattern for these besides that it seems to happen around 3-5 thousand entries.

Feel free to contact me on discord with improvements or additional features -> Step bro Taylor#2209
