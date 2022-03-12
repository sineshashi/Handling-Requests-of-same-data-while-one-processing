import time
import json
from .models import Post
from .serializers import PostSerializer
from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable, NotFound
import websocket


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
        key = request.build_absolute_uri()
        cache_value = cache.get(key)
        response_data = None
        
        def on_message1(wsapp, message):
            wsapp.close()

        def on_message(wsapp, message):
            time.sleep(2)
            wsapp.close()

        def on_error(wsapp, error):
            wsapp.close()

        if (cache_value == None) or (cache_value['status'] == 'ERROR'):
            cache.set(key, {'response': None, 'status': 'PROCESSING'}) # We are storing cache forever which will be updated upon response. We can specify the timeout too.

            post_data = get_post(id)

            if post_data == 'KeyError':
                cache.set(key, {'response': '', 'status':'ERROR'})
                response_data = 'KeyError'
            else:
                serializer = PostSerializer(post_data)
                cache.set(key, {'response': serializer.data, 'status': 'SUCCESS'})
                response_data = serializer.data

            def on_open(wsapp):
                wsapp.send(json.dumps(serializer.data))

            wsapp = websocket.WebSocketApp(f'ws://127.0.0.1:8000/ws/post/{id}/', on_open=on_open, on_message=on_message1, on_error=on_error)
            wsapp.run_forever()
        
        elif cache_value['status'] == 'PROCESSING':

            wsapp = websocket.WebSocketApp(f'ws://127.0.0.1:8000/ws/post/{id}/', on_message=on_message, on_error=on_error)
            wsapp.run_forever()


        new_cache_value = cache.get(key)
        if response_data  != None:
            if response_data == 'KeyError':
                return Response('KeyError', status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:
            if new_cache_value['status'] == 'SUCCESS':
                return Response(new_cache_value['response'], status=status.HTTP_200_OK)
            else:
                return Response('Error Occured', status=status.HTTP_404_NOT_FOUND)
















        #     id = kwargs['pk']
        #     post = get_post(id)
        #     if post == 'KeyError':
        #         cache.set(key, {'response': 'KeyError', 'status': 'ERROR'}) #Updating cache
        #         raise NotFound(detail="Post Not Found.")
        #     else:
        #         serializer = PostSerializer(post)
        #         cache.set(key, {'response': serializer.data, 'status': 'SUCCESS'}) #Updating cache
        #         return Response(data=serializer.data, status=status.HTTP_200_OK)
        # elif cache_value['status'] == 'ERROR':
        #     raise NotFound(detail="Post Not Found.")
        # elif cache_value['status'] == 'SUCCESS':
        #     return Response(data = cache_value['response'])
        # else:
        #     # When status == PROCESSING, wait to finish query.
        #     time_diff = datetime.datetime.now() - cache_value['time']
        #     ewt = datetime.timedelta(seconds=62) - time_diff # calculating expected time of response.
        #     time.sleep(ewt.total_seconds()) # Wait till the expected time of response finishes.
        #     if cache.get(key)['status'] == 'SUCCESS': # Now check if the query processing has been completed
        #         return Response(data=cache.get(key)['response'], status= status.HTTP_200_OK)
        #     elif cache.get(key)['status'] == 'ERROR':
        #         raise NotFound(detail="Post Not Found.")
        #     else:
        #         # If query is still processing, wait for 5 more seconds to complete the query.
        #         time.sleep(5)
        #         if cache.get(key)['status'] == 'SUCCESS': # Now check if the query processing has been completed
        #             return Response(data=cache.get(key)['response'], status= status.HTTP_200_OK)
        #         elif cache.get(key)['status'] == 'ERROR':
        #             raise NotFound(detail="Post Not Found.")
        #         else:
        #             return Response(data="TIME_OUT", status=status.HTTP_408_REQUEST_TIMEOUT) #If it takes more time, respond to user that time out and please refresh after some time.



