def user_role(request):
    if request.user.is_authenticated:
        return {
            'is_admin_role': request.user.is_admin_role or request.user.is_superuser,
            'is_class_teacher': request.user.is_class_teacher,
            'is_teacher_role': request.user.is_teacher_role,
            'user_role_display': request.user.get_role_display() if hasattr(request.user, 'get_role_display') else '',
        }
    return {}
