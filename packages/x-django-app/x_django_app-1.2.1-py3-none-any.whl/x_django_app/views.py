from django.views.generic import (
                                ListView, FormView,
                                CreateView, UpdateView,
                            )
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.db import transaction

from .forms import SearchForm
from .models import XActivity
# Create your views here.


class XListView(ListView, FormView):
    '''
    List view with search and sort criteria
    '''
    template_name = None
    model = None
    queryset = None
    ordering = None
    search_fields = None
    success_url = None
    form_class = SearchForm

    def post(self, request, *args, **kwargs):
        '''
        add keywords to url in post search
        '''
        if request.POST['search']:
            return HttpResponseRedirect("{0}?search={1}".format(
                                                    request.path_info,
                                                    request.POST['search']))
        else:
            return HttpResponseRedirect(request.path_info)

    def get_form_kwargs(self):
        '''
        Return the keyword arguments for instantiating the form.
        '''
        kwargs = super().get_form_kwargs()
        kwargs.update({'search': self.request.GET.get('search')})
        return kwargs

    def get_initial(self):
        '''
        get initial values for the class
        '''
        return {'search': self.request.GET.get('search')}

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        search = None
        if self.request.GET.get('search'):
            search = self.request.GET.get('search')
            kwargs.update({'search': search})
        if self.request.GET.get('sort'):
            sort = self.request.GET.get('sort')
            kwargs.update({'sort': sort})
        context.update(kwargs)
        return context

    def get_queryset(self):
        '''
        get queryset
        '''
        queryset = super().get_queryset()
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
        else:
            ordering = ('id', )
        if self.request.GET.get('search'):
            search = self.request.GET.get('search')
            fields = dict()
            for field in self.search_fields:
                field += '__icontains'
                fields[field] = search
            or_condition = Q()
            for key, value in fields.items():
                or_condition.add(Q(**{key: value}), Q.OR)
            queryset = queryset.filter(
                                or_condition).distinct().order_by(*ordering)
        if self.request.GET.get('sort'):
            sort = self.request.GET.get('sort')
            queryset = queryset.all().order_by(sort)
        return queryset


class XCreateView(CreateView):
    '''
    Create a new object with activity and created_by for requested user
    '''

    def form_valid(self, form):
        '''
        Method for valid form
        '''
        self.object = form.save()
        self.object.save()
        # Store user activity
        activity = XActivity.objects.create_activity(
                                activity_object=self.object,
                                activity=XActivity.CREATE,
                                user=self.request.user,
                                message=self.get_message(self.object)
        )
        activity.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Object-{object.id}"


class XUpdateView(UpdateView):
    '''
    Edit an existing object with activity and edited for requested user
    '''
    def form_valid(self, form):
        '''
        Method for valid form
        '''
        self.object = form.save()
        self.object.save()
        self.object.refresh_from_db()
        # Store user activity
        activity = XActivity.objects.create_activity(
                                activity_object=self.object,
                                activity=XActivity.EDIT,
                                user=self.request.user,
                                message=self.get_message(self.object)
        )
        activity.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Object-{object.id}"

# Function views


def x_record_delete_object(request, object, message):
    '''
    Record delete activity to requested user
    '''
    activity = XActivity.objects.create_activity(
                        activity_object=object,
                        activity=XActivity.DELETE,
                        user=request.user,
                        message=message
    )
    activity.save()

    try:
        with transaction.atomic():
            object.delete()
    except Exception as error_type:
        print(error_type)
        activity.delete()
        return False
    return True
