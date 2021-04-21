# Book Review Site

Project created for CS50W at Harvard via edX.org
 
Book review site created using only flask, posgresql, HTML and CSS. Create account, login, review books, read other users reviews. 
https://bdougbooks.herokuapp.com/ 

**NOTE** Publice goodreads API is no longer avialable. Book details pages will no longer load. May circle back to find another solution someday, but I have more pressing projects at the moment.

## app

* flask app containing routes and functions for the site

    * extra import of BeautifulSoup
        -used for parsing html/xml
        
    * sets up connection to SQL session
    
    * gets data from database and returns it to our templates
        -some processing to make data readable
        
    * gets user input from templates
        -validates the info and sends to database if needed
        
    * holds session vars
        -inforce logged in requirements
        
    * api call
        -processes data from database for api call


 ## static
 
* style.css
 
  * all the good styling for the site

## templates

* layout.html

  * template for basic layout of site.
    * generates our nav bar
      * has link to search and logout
      * has site title
            
* layout_nonav.html

  * template for basic layout minus nav bar.
    * basic layout for pages for non logged in users
        
* book.html

  * template for /book/<book_id>, entends layout.html
  * a page for showing information about the given book
    * Image
    * Goodreads data
    * Discription
    * local reviews
    * form to add reviews
        
* create.html

  * template for account creation, extends layout_nonav.html
    * contains a form taking username and password
        
* error.html

  * template for displaying errors, extends layout.html
    * displays an error received from app
        
* login.html

  * template for logging in, extends layout_nonav.html
    * redirect here when trying to access any other page while not logged in
    * form taking username and password
    * link to create.html
        
* index.html

  * template for our home/search page, extends layout.html
    * form with radio buttons to select which parameter to search on, and search text
    * table that is displayed after a POST request with the results of search
