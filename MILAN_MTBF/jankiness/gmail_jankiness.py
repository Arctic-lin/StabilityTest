from lib import adbcommon
from lib.gmail import Gmail
from surface_flinger_helper import SurfaceFlingerHelper
from jankiness_data_holder import JankinessDataHolder

app_window_name = 'com.google.android.gm/com.google.android.gm.ConversationListActivityGmail#0'
message_window_name = 'com.google.android.gm/com.google.android.gm.ConversationListActivityGmail#0'

NUM_ITERATIONS = 2
TRACE_TIME = 5

sfh = SurfaceFlingerHelper()


def test_01_main_window_scrolling(device_id):
    case_name = 'GmailScrolling'
    print('running case {}'.format(case_name))
    test_data = []
    gmail = Gmail(device_id)
    # run at the main window
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        sx, sy, ex, ey = _get_swipe_or_fling_points()
        gmail.device.swipe(sx, sy, ex, ey, 55)
        gmail.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
        gmail.device.swipe(sx, ey, ex, sy, 55)
        gmail.device.wait.idle()
    return case_name, test_data


def test_02_main_window_flinging(device_id):
    case_name = 'GmailFlinging'
    print('running case {}'.format(case_name))
    test_data = []
    gmail = Gmail(device_id)
    # run at the main window
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        sx, sy, ex, ey = _get_swipe_or_fling_points()
        gmail.device.swipe(sx, sy, ex, ey, 5)
        gmail.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
        gmail.device.swipe(sx, ey, ex, sy, 5)
        gmail.device.wait.idle()
    return case_name, test_data


def test_03_message_flinging(device_id):
    case_name = 'MessageFlinging'
    print('running case {}'.format(case_name))
    test_data = []
    gmail = Gmail(device_id)
    # run at the main window
    el = gmail.device(descriptionContains='as_osprofile01')
    el.click.wait(timeout=5000)
    gmail.device.delay(5)
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, message_window_name)
        sx, sy, ex, ey = _get_swipe_or_fling_points()
        gmail.device.swipe(sx, sy, ex, ey, 5)
        gmail.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, message_window_name, True))
        gmail.device.swipe(sx, ey, ex, sy, 5)
        gmail.device.wait.idle()
    gmail.device.press.back()
    gmail.device.wait.idle()
    return case_name, test_data


def test_04_message_scrolling(device_id):
    case_name = 'MessageScrolling'
    print('running case {}'.format(case_name))
    test_data = []
    gmail = Gmail(device_id)
    # run at the main window
    el = gmail.device(descriptionContains='as_osprofile01')
    el.click.wait(timeout=5000)
    gmail.device.delay(5)
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, message_window_name)
        sx, sy, ex, ey = _get_swipe_or_fling_points()
        gmail.device.swipe(sx, sy, ex, ey, 55)
        gmail.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, message_window_name, True))
        gmail.device.swipe(sx, ey, ex, sy, 55)
        gmail.device.wait.idle()
    gmail.device.press.back()
    gmail.device.wait.idle()
    return case_name, test_data


def test_05_message_swipe_archive(device_id):
    case_name = 'MessageSwipeArchive'
    print('running case {}'.format(case_name))
    test_data = []
    gmail = Gmail(device_id)
    # run at the main window
    el = gmail.device(resourceId='com.google.android.gm:id/thread_list_view') \
        .child(className='android.view.View', index=2)
    undo_btn = gmail.device(text='Undo')
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, app_window_name)
        el.scroll.horiz.forward()
        gmail.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, app_window_name, True))
        if undo_btn.exists:
            undo_btn.click.wait()
        gmail.device.wait.idle()
    return case_name, test_data


def _get_swipe_or_fling_points():
    return [500, 2100, 500, 500]


def main(device_id, is_heavy=False):
    jdh = JankinessDataHolder(device_id)
    g = Gmail(device_id)
    g.launch_by_adb()
    for _ in range(TRACE_TIME):
        case_name, test_data = test_01_main_window_scrolling(device_id)
        jdh.add_test_datas(case_name, test_data)
        case_name, test_data = test_02_main_window_flinging(device_id)
        jdh.add_test_datas(case_name, test_data)
        g.device.swipe(500, 300, 500, 2000, 5)
        case_name, test_data = test_03_message_flinging(device_id)
        jdh.add_test_datas(case_name, test_data)
        case_name, test_data = test_04_message_scrolling(device_id)
        jdh.add_test_datas(case_name, test_data)
        case_name, test_data = test_05_message_swipe_archive(device_id)
        jdh.add_test_datas(case_name, test_data)
    project_id = adbcommon.get_project_id(device_id)
    version_id = adbcommon.get_build_number(device_id)
    jdh.upload_result(project_id, version_id, 'gmail', is_heavy)
    g.suicide()


if __name__ == '__main__':
    device_id = adbcommon.get_connected_device()
    main(device_id)
