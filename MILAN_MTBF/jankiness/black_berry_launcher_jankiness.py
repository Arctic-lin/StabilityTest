 from lib.bb_launcher import BBLauncher
from surface_flinger_helper import SurfaceFlingerHelper
from jankiness_data_holder import JankinessDataHolder
import sys
from lib import adbcommon

app_process_name = 'com.blackberry.blackberrylauncher'
app_window_name = 'com.blackberry.blackberrylauncher/com.blackberry.blackberrylauncher.MainActivity#0'

NUM_ITERATIONS = 2
TRACE_TIME = 5

sfh = SurfaceFlingerHelper()


def test_app_grid_switch(device_id):
    case_name = 'AppGridSwitching'
    test_data = []
    print('running case {}'.format(case_name))
    launcher = BBLauncher(device_id)
    page1 = launcher.device(descriptionStartsWith='Screen indicator 1')
    page2 = launcher.device(descriptionStartsWith='Screen indicator 2')
    launcher.device.press.home()
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        page2.click()
        launcher.device.wait.idle()
        sfh.dump_frame_latency(device_id, app_window_name, True)
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
        page1.click()
        launcher.device.wait.idle()
    return case_name, test_data


def test_app_grid_slow_switching(device_id):
    case_name = 'AppGridSlowSwitching'
    test_data = []
    print('running case {}'.format(case_name))
    launcher = BBLauncher(device_id)
    page1 = launcher.device(descriptionStartsWith='Screen indicator 1')
    main_view = launcher.device(resourceId='com.blackberry.blackberrylauncher:id/panel_pager')
    launcher.device.press.home()
    if main_view.exists:
        bounds = main_view.info['bounds']
        right = bounds['right'] - 100
        center_y = (bounds['top'] + bounds['bottom']) / 2
        for i in range(NUM_ITERATIONS):
            sfh.clear_buffer(device_id, app_window_name)
            launcher.device.swipe(right, center_y, 0, center_y, 200)
            sfh.dump_frame_latency(device_id, app_window_name, True)
            test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
            page1.click()
    return case_name, test_data


def test_panel_switching(device_id):
    case_name = 'PanelSwitching'
    test_data = []
    print('running case {}'.format(case_name))
    launcher = BBLauncher(device_id)
    all_items = launcher.device(descriptionStartsWith='All Items')
    available_items_pager = launcher.device(resourceId='com.blackberry.blackberrylauncher:id/available_items_pager')
    launcher.device.press.home()
    all_items.click.wait()
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        available_items_pager.swipe.left(steps=20)
        launcher.device.wait.idle()
        sfh.dump_frame_latency(device_id, app_window_name, True)
        available_items_pager.swipe.right(steps=2)
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
    return case_name, test_data


def test_panel_slow_switching(device_id):
    case_name = 'PanelSlowSwitching'
    test_data = []
    print('running case {}'.format(case_name))
    launcher = BBLauncher(device_id)
    launcher.device.press.home()
    all_items = launcher.device(descriptionStartsWith='All Items')
    all_items.click()
    available_items_pager = launcher.device(resourceId='com.blackberry.blackberrylauncher:id/available_items_pager')
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        available_items_pager.swipe.left(steps=200)
        launcher.device.wait.idle()
        sfh.dump_frame_latency(device_id, app_window_name, True)
        available_items_pager.swipe.right(steps=2)
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
    return case_name, test_data


def test_app_panel_slow_scrolling(device_id):
    case_name = 'AppPaneSlowScrolling'
    test_data = []
    print('running case {}'.format(case_name))
    launcher = BBLauncher(device_id)
    launcher.device.press.home()
    all_items = launcher.device(descriptionStartsWith='All Items')
    all_items.click.wait()
    available_items_pager = launcher.device(resourceId='com.blackberry.blackberrylauncher:id/available_items_pager')
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        available_items_pager.scroll.vert.toEnd(steps=200, max_swipes=1)
        launcher.device.wait.idle()
        sfh.dump_frame_latency(device_id, app_window_name, True)
        available_items_pager.scroll.vert.toBeginning(max_swipes=2)
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
    return case_name, test_data


def test_widget_panel_slow_scrolling(device_id):
    case_name = 'WidgetPaneSlowScrolling'
    test_data = []
    print('running case {}'.format(case_name))
    launcher = BBLauncher(device_id)
    launcher.device.press.home()
    all_items = launcher.device(descriptionStartsWith='All Items')
    all_items.click.wait()
    launcher.device.delay(1)
    widgets = launcher.device(textStartsWith='WIDGETS')
    widgets.click.wait()
    available_items_pager = launcher.device(resourceId='com.blackberry.blackberrylauncher:id/available_items_pager')
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        available_items_pager.scroll.vert.toEnd(steps=400, max_swipes=1)
        launcher.device.wait.idle()
        sfh.dump_frame_latency(device_id, app_window_name, True)
        available_items_pager.scroll.vert.toBeginning(max_swipes=2)
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
    return case_name, test_data


def main(device_id, is_heavy=False, num_iterations=2, trace_time=5):
    global NUM_ITERATIONS
    NUM_ITERATIONS = num_iterations
    jdh = JankinessDataHolder(device_id)
    b = BBLauncher(device_id)
    b.device.press.home()
    b.device.wait.idle()
    for _ in range(trace_time):
        case_name, data = test_app_grid_switch(device_id)
        jdh.add_test_datas(case_name, data)
        case_name, data = test_app_grid_slow_switching(device_id)
        jdh.add_test_datas(case_name, data)
        case_name, data = test_panel_switching(device_id)
        jdh.add_test_datas(case_name, data)
        case_name, data = test_panel_slow_switching(device_id)
        jdh.add_test_datas(case_name, data)
        case_name, data = test_app_panel_slow_scrolling(device_id)
        jdh.add_test_datas(case_name, data)
        case_name, data = test_widget_panel_slow_scrolling(device_id)
        jdh.add_test_datas(case_name, data)
    project_id, version_id = adbcommon.get_project_id_version_id(device_id)
    jdh.upload_result(project_id, version_id, is_heavy)


if __name__ == '__main__':
    device_id = adbcommon.get_connected_device()
    main(device_id)
