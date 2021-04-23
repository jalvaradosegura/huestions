from allauth.account.forms import SignupForm
from captcha.fields import ReCaptchaField


class MyCustomSignupForm(SignupForm):
    captcha = ReCaptchaField()

    field_order = ['email', 'password1', 'captcha']

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSignupForm, self).save(request)

        # Add your own processing here.

        # You must return the original result.
        return user
