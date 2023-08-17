# Backend Assignment | FamPay😎🤑

To make an API to fetch latest videos sorted in reverse chronological order of the publishing date-time from YouTube for a given search query in paginated response
 
## Functionalities✨
-Used threading to let happen the fetch process continously with the given interval

-GET request gives the JSON response of the list of videos in the right order

## Tech Stack:💻
#### Backend: 
-Flask(Python) 

#### Database:
-MongoDb

#### Testing:
-Postman

## Highlights:👌
1) Indexing has been done for better performance
2) Pagination with a limit of 10 has been done for GET request
3) Used multiple API key options incase of any errors

## Using the project:🥰
1) Clone the project
2) PIP install the requirements.txt in a new virtual env
3) Setup the .env file with API Links, MongoDb URI, Table and Collection Name
4) To run the project use the command " python -m flask run "

#### On running the project data will begin to be fetched and stored in the database, to view the data                    
#### GET req: localhost/v1/response/{page_number}



## Found a bug/want to request a feature? Thanks! Just follow the steps below:😉

1. File an issue with appropriate tags
2. Fork this repo
3. Make changes to a feature branch
`git checkout -b <issue-#>`
4. Once done, run `npm run commit`
5. Make sure you `sync up` the branch with the upstream master
6. Raise a PR for review

   

