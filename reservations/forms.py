
from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    """
    Форма для создания и редактирования бронирования столика.
    """
    class Meta:
        model = Reservation
        fields = ["date", "time", "guests", "phone", "email"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean_guests(self):
        """
        Проверяет, что количество гостей положительное.
        """
        guests = self.cleaned_data.get("guests")
        if guests < 1:
            raise forms.ValidationError(
                "Количество гостей должно быть положительным числом."
            )
        return guests
