def __init__(hub):
    # Remember not to start your app in the __init__ function
    # This function should just be used to set up the plugin subsystem
    # The run.py is where your app should usually start
    hub.pop.sub.load_subdirs(hub.discovery, recurse=True)
    hub.discovery.RUNS = {}
