Problem Statement:

    1. Let's say we are working on a web service (very high traffic) where you
    have to do some processing based on the get parameter “querystring”. To create a response for one unique querystring (say q1), it takes around one minute to complete (You can simulate it on your code by time. sleep). Many requests will come for a querystring (say q1) by the 1 minute you are creating a response in. The web service should be able to store all requests for querystring == q1 while time. sleep gets over and then returns a common output for all query == q1. You can use any python web framework {django, flask, node js, etc} to write this.


Using Guide (Windows):

    Clone the repo and then get into it.
    Now create virtual env by :
        python -m venv env

    Activate env by:
        ./env/scripts/activate

    Now install requirements by:
        pip install -r requirements.txt

    Get into the project directory:
        cd ./query_project

    Now use simple django commands for makemigrations, migrate, createsuperuser and reunserver.

How has problem been handled:

    Since we have a large data so we are using redis for caching which will improve our speed. The request response cycle flow will be like this:
    1) If request asks for the data already stored in redis with status key value 'SUCCESS', it will give response from there.
    2) If request asks for the data not in redis then it will first set cache with status 'PROCESSING' and current time and then start processing the query.
        Once the query is finished, it stores that data into redis with status of SUCCESS.
    3) If request asks for the data which is being currecntly processed by some other request, it will find status 'PROCESSING' in redis and will estimate time of finishing that query and sleep for that time. 
        After sleep time being over, it will check again the status key in the redis, if it is 'SUCCESS' or 'ERROR' it will response accordingly.
    4) If any new requests comes which has been saved it the redis as 'ERROR' will be treated as no data for the request.