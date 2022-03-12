import time
from .models import Post
from .serializers import PostSerializer
from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable, NotFound
import datetime


class PostView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):

        # Writing a get query function which takes 1 minute to perform the task.
        def get_post(id):
            time.sleep(60)
            try:
                return Post.objects.get(id = id)
            except:
                return 'KeyError' #object does not exists for the given key.
        
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Please provide primary key.")
        id = kwargs['pk']
        key = request.build_absolute_uri() #Finding the url which we will use as key for cache.
        cache_value = cache.get(key) #Getting cache for the key.
     
        if cache_value == None or cache_value['status'] == 'ERROR':
            cache.set(key, {'response': '', 'status': 'PROCESSING', 'time': datetime.datetime.now()})
            id = kwargs['pk']
            post = get_post(id)
            if post == 'KeyError':
                cache.set(key, {'response': 'KeyError', 'status': 'ERROR'}) #Updating cache
                raise NotFound(detail="Post Not Found.")
            else:
                serializer = PostSerializer(post)
                cache.set(key, {'response': serializer.data, 'status': 'SUCCESS'}) #Updating cache
                return Response(data=serializer.data, status=status.HTTP_200_OK)

        elif cache_value['status'] == 'SUCCESS':
            return Response(data = cache_value['response'])
        else:
            # When status == PROCESSING, wait to finish query.
            time_diff = datetime.datetime.now() - cache_value['time']
            ewt = datetime.timedelta(seconds=65) - time_diff # calculating expected time of response.
            time.sleep(ewt.total_seconds()) # Wait till the expected time of response finishes.
            if cache.get(key)['status'] == 'SUCCESS': # Now check if the query processing has been completed
                return Response(data=cache.get(key)['response'], status= status.HTTP_200_OK)
            elif cache.get(key)['status'] == 'ERROR':
                raise NotFound(detail="Post Not Found.")
            else:
                if cache.get(key)['status'] == 'SUCCESS': # Now check if the query processing has been completed
                    return Response(data=cache.get(key)['response'], status= status.HTTP_200_OK)
                else: 
                    return Response(data="Error occured", status=status.HTTP_404_NOT_FOUND) #If it takes more time, respond to user that time out and please refresh after some time.



