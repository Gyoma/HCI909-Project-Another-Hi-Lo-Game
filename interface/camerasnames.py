import platform

# Function 'available_cameras_dict' returns dictionary with keys as camera names and values as camera indexes.

if platform.system().lower().startswith('win'):
    from pygrabber.dshow_graph import FilterGraph

    def available_cameras_dict():
        graph = FilterGraph()
        cameras_list = graph.get_input_devices()

        # The camera's index corresponds to the index in the list
        cameras_dict = {}
        for i, camera in enumerate(cameras_list):
            cameras_dict[camera] = i

        return cameras_dict

elif platform.system().lower().startswith('lin'):
    import v4l2py

    def available_cameras_dict():
        cameras_dict = {}
        for device in v4l2py.iter_video_capture_devices():
            device.open()
            cameras_dict[device.info.card] = device.index
            device.close()
        return cameras_dict
