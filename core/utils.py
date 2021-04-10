from django.shortcuts import redirect


def redirect_and_check_if_list_was_shared(
    kwargs, view_name, target_list, username
):
    if 'username' in kwargs:
        return redirect(view_name, target_list.slug, username)
    return redirect(view_name, target_list.slug)
