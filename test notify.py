from plyer import notification

def notify(title, message,):
    notification.notify(
        title=title,
        message=message,
        app_name='YouTube Downloader',
        app_icon= None,
        timeout=2
    )

notify('something','something')