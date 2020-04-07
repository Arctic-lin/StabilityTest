from lib.tcl_launcher import TclLauncher
from surface_flinger_helper import SurfaceFlingerHelper
from jankiness_data_holder import JankinessDataHolder
import sys
from lib import adbcommon

app_process_name = 'com.tcl.android.launcher'
app_window_name = 'com.tcl.android.launcher/com.tcl.android.launcher.Launcher#0'

NUM_ITERATIONS = 2
TRACE_TIME = 1

sfh = SurfaceFlingerHelper()


def test_app_grid_switch(device_id):
    case_name = 'AppGridSwitching'
    test_data = []
    print('running case {}'.format(case_name))
    launcher = TclLauncher(device_id)
    launcher.device.press.home()
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        launcher.device.swipe(1000, 500, 200, 500, 2)
        launcher.device.wait.idle()
        sfh.dump_frame_latency(device_id, app_window_name, True)
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
        launcher.device.swipe(200, 500, 1000, 500, 2)
        launcher.device.wait.idle()
    return case_name, test_data


def test_app_grid_slow_switching(device_id):
    case_name = 'AppGridSlowSwitching'
    test_data = []
    print('running case {}'.format(case_name))
    launcher = TclLauncher(device_id)
    launcher.device.press.home()
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        launcher.device.swipe(1000, 500, 0, 500, 200)
        sfh.dump_frame_latency(device_id, app_window_name, True)
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
        launcher.device.swipe(200, 500, 1000, 500, 2)
    return case_name, test_data



def test_app_panel_slow_scrolling(device_id):
    case_name = 'AppPaneSlowScrolling'
    test_data = []
    print('running case {}'.format(case_name))
    launcher = TclLauncher(device_id)
    launcher.device.press.home()
    # swipe up open app panel
    launcher.device.swipe(500, 800, 500, 200, 20)
    app_list = launcher.device(resourceId='com.tcl.android.launcher:id/apps_list_view')
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        app_list.scroll.vert.toEnd(steps=200, max_swipes=1)
        launcher.device.wait.idle()
        sfh.dump_frame_latency(device_id, app_window_name, True)
        app_list.scroll.vert.toBeginning(max_swipes=2)
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
    return case_name, test_data


def main(device_id, is_heavy=False, num_iterations=2, trace_time=5):
    global NUM_ITERATIONS
    NUM_ITERATIONS = num_iterations
    jdh = JankinessDataHolder(device_id)
    tl = TclLauncher(device_id)
    tl.device.press.home()
    tl.device.wait.idle()
    for _ in range(trace_time):
        case_name, data = test_app_grid_switch(device_id)
        jdh.add_test_datas(case_name, data)
        case_name, data = test_app_grid_slow_switching(device_id)
        jdh.add_test_datas(case_name, data)
        case_name, data = test_app_panel_slow_scrolling(device_id)
        jdh.add_test_datas(case_name, data)
    project_id, version_id = adbcommon.get_project_id_version_id(device_id)
    jdh.upload_result(project_id, version_id, 'launcher',is_heavy)


if __name__ == '__main__':
    device_id = adbcommon.get_connected_device()
    main(device_id)
