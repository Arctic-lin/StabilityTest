from lib import aoscommon
import subprocess
import re


class GfxInfoHelper(object):
    BUFFER_SIZE = 128
    BUFFER_NUM = 4
    GFXINFO_CMD = 'dumpsys gfxinfo'
    PROFILE_HEADER = 'Profile data in ms:'
    COLUMN_HEADER = 'Draw\tPrepare\tProcess\tExecute'
    VIEW_HIERARCHY_HEADER = 'View hierarchy:'

    def __init__(self):
        self._clear_data()

    def clear_buffer(self, device_id, process_name):
        self._clear_data()
        cmd = 'adb -s {} shell {} {}'.format(device_id, self.GFXINFO_CMD, process_name)
        aoscommon.call_adb(cmd)

    def _clear_data(self):
        self.frame_buffer_data = []
        self.total_frame_time = []
        self.max_frame_time = -1
        self.min_frame_time = -1
        self.avg_frame_time = -1
        self.late_frames = -1

    def dump_gfx_info_stats(self, device_id, process_name, window_name):
        cmd = 'adb -s {} shell {} {}'.format(device_id, self.GFXINFO_CMD, process_name)
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        line = p.stdout.readline()
        pattern = re.compile('\s*(\d+.\d+)\s+(\d+.\d+)\s+(\d+.\d+)\s+(\d+.\d+)\s*')
        found_profile_header = False
        found_window_header = False
        found_column_header = False
        found_view_hierarchy_header = False
        for line in p.stdout.readline():
            line = line.strip()
            if not line:
                continue
            if not found_profile_header:
                found_profile_header = line == self.PROFILE_HEADER
                continue
            elif not found_window_header:
                found_window_header = line == window_name
                continue
            elif not found_column_header:
                found_column_header = line == self.COLUMN_HEADER
            elif not found_view_hierarchy_header:
                found_view_hierarchy_header = line == self.VIEW_HIERARCHY_HEADER
                if found_view_hierarchy_header:
                    break
            render_times = pattern.findall(line)
            render_times = map(int, render_times)
            self.frame_buffer_data.append(render_times)
            self.total_frame_time.append(sum(render_times))

    def get_frame_buffer_data(self):
        if not len(self.frame_buffer_data):
            return ''
        raw_data = self.COLUMN_HEADER + '\n'
        raw_data += '\n'.join(
            ['\t'.join(map(str, item)) for item in self.frame_buffer_data]
        )
        return raw_data

    def process_frame_times(self):
        if not len(self.total_frame_time):
            return
        self.late_frames = 0
        for t in self.frame_buffer_data:
            if t > 16:
                self.late_frames += 1
        self.min_frame_time = min(self.total_frame_time)
        self.max_frame_time = max(self.total_frame_time)
        self.avg_frame_time = sum(self.total_frame_time) / len(self.total_frame_time)

    def get_min_frame_time(self):
        if not len(self.frame_buffer_data):
            return -1
        return self.min_frame_time

    def get_max_frame_time(self):
        if not len(self.frame_buffer_data):
            return -1
        return self.max_frame_time

    def get_avg_frame_time(self):
        if not len(self.frame_buffer_data):
            return -1
        return self.min_frame_time

    def get_late_frame_count(self):
        if not len(self.frame_buffer_data):
            return -1
        return self.min_frame_time

    def get_total_frame_count(self):
        if not len(self.frame_buffer_data):
            return -1
        return self.min_frame_time
