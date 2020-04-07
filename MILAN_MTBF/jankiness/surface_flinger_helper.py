import subprocess
import sys
import os
import re
# from lib import result_printer


class SurfaceFlingerHelper(object):
    BUFFER_SIZE = 128
    BUFFER_NUM = 3

    CLEAR_BUFFER_CMD = 'dumpsys SurfaceFlinger --latency-clear'
    FRAME_LATENCY_CMD = 'dumpsys SurfaceFlinger --latency'
    RAW_DATA_DIR = 'UiJankinessRawData'
    PAUSE_LATENCY = 20

    PENDING_FENCE_TIME = '9223372036854775807'

    def __init__(self):
        self.device_id = ''
        self._clear_data()

    def clear_buffer(self, device_id, window_name):
        self._clear_data()
        subprocess.call('adb -s {} shell {} {}'.format(device_id, self.CLEAR_BUFFER_CMD, window_name).split())

    def _clear_data(self):
        self.frame_buffer_data = []
        self.refresh_period = -1
        self.frame_latency_sample_size = 0
        self.delta_vsync = [-1] * self.BUFFER_SIZE
        self.delta2_vsync = [-1] * self.BUFFER_SIZE
        self.max_delta_vsync = -1
        self.max_round_normalized_delta_vsync = -1
        self.normalized_delta2_vsync = [-1] * self.BUFFER_SIZE
        self.round_normalized_delta2_vsync = [-1] * self.BUFFER_SIZE
        self.jankiness_count = 0
        self.frame_rate = 0

    def dump_frame_latency(self, device_id, window_name, ignore_pending_fence_time=False):
        self.device_id = device_id
        cmd = 'adb -s {} shell {} {}'.format(device_id, self.FRAME_LATENCY_CMD, window_name)
        output = subprocess.check_output(cmd.split())
        lines = output.splitlines()
        return self._manipulate_frame_latency(lines, window_name, ignore_pending_fence_time)

    def _manipulate_frame_latency(self, lines, window_name, ignore_pending_fence_time=False):
        rs = {
            'jankinessCount': 0,
            'frameRate': 0,
            'maxDeltaVsync': 0
        }
        try:
            self.refresh_period = int(lines[0])
        except Exception as e:
            print(e)
            self.refresh_period = -1
            return False
        for line in lines[1:]:
            line = line.strip()
            if not line:
                break
            buffer_values = re.split('\s+', line)
            if buffer_values[0] == '0':
                continue
            if buffer_values[1] == self.PENDING_FENCE_TIME and ignore_pending_fence_time:
                continue
            if self.frame_latency_sample_size < self.BUFFER_SIZE:
                self.frame_buffer_data.append(map(int, buffer_values))
                self.frame_latency_sample_size += 1
        if self.frame_latency_sample_size <= 2:
            return rs
        # calculate delay vsync and max delta vsync
        self.delta_vsync, self.max_delta_vsync = self._cal_delta_vsync(self.frame_buffer_data)
        # calculate delay2 vsync
        self.delta2_vsync = self._cal_delta2_vsnyc(self.delta_vsync)
        # normalized delta2 vsync
        self.normalized_delta2_vsync = self._cal_normalized_delta2_vsync(self.delta2_vsync, self.refresh_period)
        # round normalized delta2 vsync
        self.round_normalized_delta2_vsync = self._cal_round_normalized_delta2_vsync(self.normalized_delta2_vsync)
        # jankiness count
        self.jankiness_count = self._cal_vsync_jankiness(self.round_normalized_delta2_vsync)
        # max normalized delta vsync
        self.max_round_normalized_delta_vsync = self._cal_max_round_normalized_delta_vsync(self.max_delta_vsync,
                                                                                           self.refresh_period)
        # frame rate
        self.frame_rate = self._cal_frame_rate(self.frame_buffer_data)

        self.dump_to_file(window_name)

        return {
            'jankinessCount': self.jankiness_count,
            'frameRate': self.frame_rate,
            'maxDeltaVsync': self.max_round_normalized_delta_vsync,
        }

    def _cal_delta_vsync(self, frame_buffer_data):
        delta_vsync = [frame_buffer_data[i][1] - frame_buffer_data[i - 1][1]
                       for i in range(1, len(frame_buffer_data))]
        max_delta_vsync = max(delta_vsync)
        return (delta_vsync, max_delta_vsync)

    def _cal_delta2_vsnyc(self, delta_vsync):
        return [delta_vsync[i] - delta_vsync[i - 1]
                for i in range(1, len(delta_vsync))]

    def _cal_normalized_delta2_vsync(self, delta2_vsync, refresh_period):
        return [float(item) / refresh_period for item in delta2_vsync]

    def _cal_round_normalized_delta2_vsync(self, normalized_delta2_vsync):
        return [int(round(max(item, 0.0))) for item in normalized_delta2_vsync]

    def _cal_vsync_jankiness(self, round_normalized_delta2_vsync):
        jankiness_count = 0
        for item in round_normalized_delta2_vsync:
            if 0 < item < self.PAUSE_LATENCY:
                jankiness_count += 1
        return jankiness_count

    def _cal_max_round_normalized_delta_vsync(self, max_delta_vsync, refresh_period):
        return round(float(max_delta_vsync) / refresh_period)

    def _cal_frame_rate(self, frame_buffer_data):
        dp = map(lambda x: x[1], frame_buffer_data)
        dp = list(set(dp))
        duration = max(dp) - min(dp)
        frame_count = len(dp)
        if duration == 0 or frame_count == 0:
            return -1
        return float(len(dp) - 1) * pow(10, 9) / duration

    def dump_to_file(self, window_name):
        # result_printer.print_frame_latency(self, window_name)
        pass


if __name__ == '__main__':
    windowName = 'com.blackberry.hub/com.blackberry.hub.ui.HubActivity#0'
    sfh = SurfaceFlingerHelper()
    sfh.clear_buffer(windowName)
