from collections import defaultdict
from lib import result_printer


class JankinessDataHolder(object):

    def __init__(self, device_id):
        self.data_pool = defaultdict(list)
        self.device_id = device_id

    def add_test_data(self, case_name, test_data):
        self.data_pool[case_name].append(test_data)

    def add_test_datas(self, case_name, test_datas):
        self.data_pool[case_name].extend(test_datas)

    def upload_result(self, project_id, version_id, submodule, is_heavy=False):
        test_result = []
        for key, value in self.data_pool.iteritems():
            jankiness_count = sum(self._get_array_by_key('jankinessCount', value))
            framerate = self._get_average(self._get_array_by_key('frameRate', value))
            test_result.append([key, jankiness_count, framerate])
        print(project_id, version_id, test_result, is_heavy)
        result_printer.print_jankiness(self.device_id, submodule, test_result, is_heavy)

    def _get_array_by_key(self, key, data):
        return [item[key] for item in data]

    def _get_average(self, data):
        if not data:
            return 0
        return float(sum(data)) / len(data)

    def _key_mapping(self, key):
        return {
            'testScrolling': 'test_scrolling',
            'AppGridSwitching': 'app_grid_switching',
            'AppGridSlowSwitching': 'app_grid_slow_switching',
            'PanelSwitching': 'panel_switching',
            'PanelSlowSwitching': 'panel_slow_switching',
            'AppPaneSlowScrolling': 'app_panel_slows_scrolling',
            'WidgetPaneSlowScrolling': 'widget_panel_slow_scrolling',
            'HubScrolling': 'hub_scrolling',
            'HubFlinging': 'hub_flinging',
            'MessageFlinging': 'message_flinging',
            'MessageScrolling': 'message_scrolling',
            'MessageSwipeDelete': 'message_swipe_delete',
            'MessageSwipeSnooze': 'message_swipe_snooze',
            'MessageFlingSnooze': 'message_fling_snooze',
            'ChromeWebPageScrolling': 'chrome_web_page_scrolling',
            'ChromeWebPageFlinging': 'chrome_web_page_flinging',
            'ChromeWebPageZoomIn': 'chrome_web_page_zoom_in',
            'ChromeWebPageZoomOut': 'chrome_web_page_zoom_out',
            'ChromeWebPagePanLeft': 'chrome_web_page_pan_left',
            'ChromeWebPagePanRight': 'chrome_web_page_pan_right',
            'ChromeWebPagePanUp': 'chrome_web_page_pan_up',
            'ChromeWebPagePanDown': 'chrome_web_page_pan_down',
        }[key]
