def info(msg, *args, **kwargs):
    print(msg.format(*args))


info('{} {}', 1, 2)
