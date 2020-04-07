from lib.chrome import Chrome
from lib import adbcommon
from surface_flinger_helper import SurfaceFlingerHelper
from jankiness_data_holder import JankinessDataHolder

"""
    these pan tests may report error if no content change when panning
"""
APP_WINDOW_Name = 'com.android.chrome/com.google.android.apps.chrome.Main#0'
NUM_ITERATIONS = 1
sfh = SurfaceFlingerHelper()


def test_web_view_scrolling(device_id):
    case_name = 'ChromeWebPageScrolling'
    print('running case {}'.format(case_name))
    test_data = []
    chrome = Chrome(device_id)
    el = chrome.device(resourceId='android:id/content')
    # run at the main window
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, APP_WINDOW_Name)
        el.scroll.vert.forward()
        chrome.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
        el.scroll.vert.backward()
    return case_name, test_data


def test_web_view_flinging(device_id):
    case_name = 'ChromeWebPageFlinging'
    print('running case {}'.format(case_name))
    test_data = []
    chrome = Chrome(device_id)
    el = chrome.device(resourceId='android:id/content')
    # run at the main window
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, APP_WINDOW_Name)
        el.fling.vert.forward()
        chrome.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
        el.fling.vert.backward()
    return case_name, test_data


def test_web_view_zoom_in(device_id):
    case_name = 'ChromeWebPageZoomIn'
    print('running case {}'.format(case_name))
    test_data = []
    chrome = Chrome(device_id)
    el = chrome.device(resourceId='android:id/content')
    # el.scroll.vert.forward()
    chrome.device.wait.idle()
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, APP_WINDOW_Name)
        el.pinch.Out(percent=100, steps=100)
        chrome.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
        el.pinch.In(percent=150, steps=100)
    return case_name, test_data


def test_web_view_zoom_out(device_id):
    case_name = 'ChromeWebPageZoomOut'
    print('running case {}'.format(case_name))
    test_data = []
    chrome = Chrome(device_id)
    el = chrome.device(resourceId='android:id/content')
    # el.scroll.vert.forward()
    chrome.device.wait.idle()
    for i in range(NUM_ITERATIONS):
        el.pinch.Out(percent=100, steps=100)
        chrome.device.wait.idle()
        sfh.clear_buffer(device_id, APP_WINDOW_Name)
        el.pinch.In(percent=150, steps=100)
        chrome.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
    return case_name, test_data


def test_web_view_pan_left(device_id):
    case_name = 'ChromeWebPagePanLeft'
    print('running case {}'.format(case_name))
    test_data = []
    chrome = Chrome(device_id)
    el = chrome.device(resourceId='android:id/content')
    # el.scroll.vert.forward()
    chrome.device.wait.idle()
    el.pinch.Out(percent=200, steps=50)
    chrome.device.wait.idle()
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, APP_WINDOW_Name)
        el.swipe.left(steps=50)
        chrome.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
        el.swipe.right(steps=50)
        chrome.device.wait.idle()
    el.pinch.In(percent=100, steps=50)
    return case_name, test_data


def test_web_view_pan_right(device_id):
    case_name = 'ChromeWebPagePanRight'
    print('running case {}'.format(case_name))
    test_data = []
    chrome = Chrome(device_id)
    el = chrome.device(resourceId='android:id/content')
    # el.scroll.vert.forward()
    chrome.device.wait.idle()
    el.pinch.Out(percent=200, steps=50)
    chrome.device.wait.idle()
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, APP_WINDOW_Name)
        el.swipe.right(steps=50)
        chrome.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
        el.swipe.left(steps=50)
        chrome.device.wait.idle()
    el.pinch.In(percent=100, steps=50)
    return case_name, test_data


def test_web_view_pan_up(device_id):
    case_name = 'ChromeWebPagePanUp'
    print('running case {}'.format(case_name))
    test_data = []
    chrome = Chrome(device_id)
    el = chrome.device(resourceId='android:id/content')
    # el.scroll.vert.forward()
    chrome.device.wait.idle()
    el.pinch.Out(percent=200, steps=50)
    chrome.device.wait.idle()
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, APP_WINDOW_Name)
        el.swipe.up(steps=50)
        chrome.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
        el.swipe.down(steps=50)
        chrome.device.wait.idle()
    el.pinch.In(percent=100, steps=50)
    return case_name, test_data


def test_web_view_pan_down(device_id):
    case_name = 'ChromeWebPagePanDown'
    print('running case {}'.format(case_name))
    test_data = []
    chrome = Chrome(device_id)
    el = chrome.device(resourceId='android:id/content')
    chrome.device.wait.idle()
    el.pinch.Out(percent=200, steps=50)
    chrome.device.wait.idle()
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, APP_WINDOW_Name)
        chrome.device.swipe(200, 351, 200, 1479, 50)
        chrome.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_Name, True))
        chrome.device.swipe(200, 1479, 200, 351, 50)
        chrome.device.wait.idle()
    el.pinch.In(percent=100, steps=50)
    return case_name, test_data


def main(device_id, is_heavy=False, num_iterations=2, trace_time=5):
    global NUM_ITERATIONS
    NUM_ITERATIONS = num_iterations
    # jdh = JankinessDataHolder(device_id)
    c = Chrome(device_id)
    c.launch_by_adb()
    c.device.delay(5)
    url = 'file://////sdcard/testdata/Home-ESPN.html'
    c.go_to_url(url)
    c.device.wait.idle()
    data_list = {}
    for _ in range(trace_time):
        case_name, data = test_web_view_scrolling(device_id)
        data_list[case_name] = data
        # jdh.add_test_datas(case_name, data)
        case_name, data = test_web_view_flinging(device_id)
        # jdh.add_test_datas(case_name, data)
        data_list[case_name] = data
        case_name, data = test_web_view_zoom_in(device_id)
        # jdh.add_test_datas(case_name, data)
        data_list[case_name] = data
        c.device.swipe(200, 400, 200, 200)
        case_name, data = test_web_view_zoom_out(device_id)
        data_list[case_name] = data
        # jdh.add_test_datas(case_name, data)
        case_name, data = test_web_view_pan_left(device_id)
        data_list[case_name] = data
        # jdh.add_test_datas(case_name, data)
        case_name, data = test_web_view_pan_right(device_id)
        # jdh.add_test_datas(case_name, data)
        data_list[case_name] = data
        case_name, data = test_web_view_pan_down(device_id)
        # jdh.add_test_datas(case_name, data)
        data_list[case_name] = data
        case_name, data = test_web_view_pan_up(device_id)
        # jdh.add_test_datas(case_name, data)
        data_list[case_name] = data
        c.swipe_main_view_to_beginning()
    # project_id, version_id = adbcommon.get_project_id_version_id(device_id)
    # jdh.upload_result(project_id, version_id, 'chrome', is_heavy)
    # c.suicide()
    return data_list

if __name__ == '__main__':
    device_id = adbcommon.get_connected_device()
    main(device_id)
