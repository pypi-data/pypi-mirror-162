from rest_framework import (
                            status, generics
                            )
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import XActivity

# Create your views here.


class XCreateAPIView(generics.CreateAPIView):
    """
    Concrete view for creating a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        object = serializer.save()
        headers = self.get_success_headers(serializer.data)
        # Store user activity
        activity = XActivity.objects.create_activity(
                                activity_object=object,
                                activity=XActivity.CREATE,
                                user=self.request.user,
                                message=self.get_message(object)
        )
        activity.save()
        return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers)
    
    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Object-{object.id}"


class XRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        object = serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        
        activity = XActivity.objects.create_activity(
                                activity_object=object,
                                activity=XActivity.EDIT,
                                user=self.request.user,
                                message=self.get_message(object)
        )
        activity.save()

        return Response(serializer.data)

    
    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Object-{object.id}"


class XDestroyAPIView(generics.DestroyAPIView):
    """
    Concrete view for deleting a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        object = self.get_object()
        # self.perform_destroy(instance)
        activity = XActivity.objects.create_activity(
                        activity_object=object,
                        activity=XActivity.DELETE,
                        user=request.user,
                        message=self.get_message(object)
        )
        activity.save()

        try:
            with transaction.atomic():
                object.delete()
        except Exception as error_type:
            print(error_type)
            activity.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Object-{object.id}"
