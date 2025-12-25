from django import forms
from django.contrib.auth.models import User
from .models import Ticket


class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.username

class TicketForm(forms.ModelForm):
    # Use custom field for assignee to show full name
    assigned_to = UserModelChoiceField(
        queryset=User.objects.none(), # Populated in __init__
        required=False,
        label="Assign To (Optional)"
    )

    class Meta:
        model = Ticket
        fields = ['issue', 'priority', 'deadline', 'assigned_to']
        widgets = {
            'issue': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your issue here...'}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TicketForm, self).__init__(*args, **kwargs)
        
        # Enable assigned_to for all users
        # Allow assigning to users in 'Ticket Admin' OR 'Ticket Support' group
        from django.db.models import Q
        self.fields['assigned_to'].queryset = User.objects.filter(
            Q(groups__name='Ticket Admin') | Q(groups__name='Ticket Support')
        ).distinct()

