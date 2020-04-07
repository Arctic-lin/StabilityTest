from lib import adbcommon
from surface_flinger_helper import SurfaceFlingerHelper
from jankiness_data_holder import JankinessDataHolder
from lib.cts_device import CTSDevice

APP_PROCESS_NAME = "com.android.cts.ui"
APP_WINDOW_NAME = "com.android.cts.ui/com.android.cts.ui.ScrollingActivity#0"

NUM_ITERATIONS = 2
TRACE_TIME = 5

sfh = SurfaceFlingerHelper()


def test_scrolling(device_id):
    case_name = 'testScrolling'
    print('running case {}'.format(case_name))
    test_data = []
    cts = CTSDevice(device_id)
    for i in range(NUM_ITERATIONS):
        sfh.clear_buffer(device_id, APP_WINDOW_NAME)
        el = cts.device(resourceId='android:id/list')
        el.scroll.vert.forward()
        cts.device.wait.idle()
        test_data.append(sfh.dump_frame_latency(device_id, APP_WINDOW_NAME, True))
        el.fling.toBeginning()
        cts.device.wait.idle()
    return case_name, test_data


def main(device_id, is_heavy=False):
    jdh = JankinessDataHolder(device_id)
    c = CTSDevice(device_id)
    c.launch_by_adb()
    for _ in range(TRACE_TIME):
        case_name, test_data = test_scrolling(device_id)
        jdh.add_test_datas(case_name, test_data)
    project_id = adbcommon.get_project_id(device_id)
    version_id = adbcommon.get_build_number(device_id)
    jdh.upload_result(project_id, version_id, 'cts', is_heavy)
    c.suicide()


if __name__ == '__main__':
    device_id = adbcommon.get_connected_device()
    main(device_id)
