from django import forms
from django.utils.translation import ugettext_lazy as _


class SearchForm(forms.Form):
    '''
    Form for search bar of the XListView
    '''
    search = forms.CharField(
                            label='',
                            max_length=128,
                            required=False,
                            widget=forms.TextInput(
                                    attrs={'placeholder': _('search')}))

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions for the SearchForm form class
        '''
        try:
            self.fields['search'].initial = kwargs.pop('search')
        except Exception:
            pass

        # get the initial form class values
        super(SearchForm, self).__init__(*args, **kwargs)
