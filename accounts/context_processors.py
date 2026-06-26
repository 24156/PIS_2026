def notifications(request):
    if request.user.is_authenticated:
        unread = request.user.notifications.filter(lu=False).count()
        return {'unread_notifications': unread}
    return {'unread_notifications': 0}
