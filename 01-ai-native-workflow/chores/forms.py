from django import forms
from .models import Household, Chore


class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ["name"]


class JoinHouseholdForm(forms.Form):
    invite_code = forms.CharField(max_length=32, label="Invite Code")


class ChoreForm(forms.ModelForm):
    rotation_members = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        help_text="Hold command/ctrl to select multiple members.",
    )

    class Meta:
        model = Chore
        fields = [
            "title",
            "description",
            "frequency",
            "point_value",
            "next_due_date",
            "rotation_members",
        ]
        widgets = {
            "next_due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, household=None, **kwargs):
        super().__init__(*args, **kwargs)
        if household:
            members = household.get_members()
            self.fields["rotation_members"].choices = [
                (str(m.pk), m.username) for m in members
            ]
        if self.instance and self.instance.pk and self.instance.rotation_members:
            self.initial["rotation_members"] = [
                str(pk) for pk in self.instance.rotation_members
            ]

    def clean_rotation_members(self):
        data = self.cleaned_data.get("rotation_members")
        if data:
            return [int(x) for x in data]
        return []
