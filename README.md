# fyipen-backend

# Execution

1. Install Python 3.11.4 from python.org -> Downloads
2. Add Python & Python/Scripts to environment variables (PATH var for windows) in your system (Follow: https://www.machinelearningplus.com/python/add-python-to-path-how-to-add-python-to-the-path-environment-variable-in-windows/)
3. Create an empty folder one level above where you wish to clone this repo
4. Within this empty folder, open a cmd prompt shell and create a virtual environment for python.
5. If you are doing this for the first time, run "pip install virtualenv"
6. Activate the virtual env depending upon your OS. (Folow: https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/)
7. Now clone the repository within the folder.
8. Open the project directory within the shell/command prompt.
9. Run "pip install -r requirements.txt".
10. Now open [https://www.mongodb.com/](https://cloud.mongodb.com/) and login with your id.
11. Create a new cluster. If you already have a cluster created then, you can ignore this step.
12. Create a new project. Name it as per your convenience.
13. After the project is created, click on "Build a database".
14. During this process, username and password get displayed. Copy them and paste them to PROJECT_DIR/DBCredentials/db.py within the respective fields.
15. Later, a section titled "Where would you like to connect from?" appears. Click -> My Local Environment. Also click on "Add My Current IP Address" to whitelist it.
16. A cluster name appears ( usually Cluster0 ). Press Connect -> Drivers -> Select Python 3.11 or later
17. Now check point no 3 (Add your connection string into your application code) in the pop up and enable View full code sample.
18. Copy the 2nd line ( uri = .... ) and paste ( and replace) it above PROJECT_DIR/config/database.py line 5 (where an identical line is written).
19. Replace the @... (e.g., @cluster0.a6v......) part in the original uri with the new uri. Before that should remain intact.
20. Now remove the copied uri string in step 18 from the file.
21. Modify PROJECT_DIR/utils/token.py -> Add a long random alphanumeric secret key to the file.
22. Your server is ready to run.
23. Execute the server, by running from terminal -> uvicorn main:app --reload

# Points to note:-

1. The backend API has a route (/addBook) to add new book to the DB. This API also needs an imgUrl. For the sake of accessibility, I request you to add images from products/books from amazon.in because I have whitelisted the same for usage within the frontend.
2. This API runs on localhost (PORT: 8000). So keep it free.
