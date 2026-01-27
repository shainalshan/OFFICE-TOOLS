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

    # Approver field (used if flag is active)
    approver = UserModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        label="Approver (Optional)"
    )

    class Meta:
        model = Ticket
        fields = ['issue', 'priority', 'deadline', 'assigned_to', 'approver']
        widgets = {
            'issue': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your issue here...'}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        approver_queryset = kwargs.pop('approver_queryset', None)
        super(TicketForm, self).__init__(*args, **kwargs)
        
        # Enable assigned_to for all users
        # Allow assigning to users in 'Ticket Admin' OR 'Ticket Support' group
        from django.db.models import Q
        self.fields['assigned_to'].queryset = User.objects.filter(
            Q(groups__name='Ticket Admin') | Q(groups__name='Ticket Support')
        ).distinct()
        
        # Enable approver based on passed queryset or default to all
        if approver_queryset is not None:
            self.fields['approver'].queryset = approver_queryset
            
            # Optional: Hide if empty and using restricted list? 
            # For now, just let it be empty so they know they need to add approvers.
        else:
            self.fields['approver'].queryset = User.objects.all().order_by('username')

