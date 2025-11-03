from django.shortcuts import redirect


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # only check for authenticated users
        if request.user.is_authenticated:
            user_profile = getattr(request.user, 'userprofile', None)

            # proceed only if user has profile
            if user_profile:
                role = user_profile.role

                # block employers from student route
                if path.startswith('/student/') and role != 'student':
                    return redirect('home')

                # block students from employer route
                if path.startswith('/employer/') and role != 'employer':
                    return redirect('home')

        return self.get_response(request)
