from rest_framework.exceptions import ValidationError


class PasswordsMatchValidationMixin:
    def validate(self, data):
        password = data.get("password")
        password2 = data.pop("password2")
        if password != password2:
            raise ValidationError("passwords not match")
        return data
