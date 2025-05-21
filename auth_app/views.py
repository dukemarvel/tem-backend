from dj_rest_auth.views import LoginView

class LoginWithRefreshView(LoginView):
    def get_response(self):
        response = super().get_response()
        refresh_cookie = response.cookies.get("lms_refresh_token")
        if refresh_cookie:
            print("refresh cookie from customzed view: {}".format(refresh_cookie))
            response.data["refresh"] = refresh_cookie.value
        else:
            print("Refresh cookie not generated")
        return response
