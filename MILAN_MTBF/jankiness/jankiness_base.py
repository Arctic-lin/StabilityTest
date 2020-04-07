import os


class JankinessBase():
    RAW_DATA_DIR = 'uiJankinessRawData'
    ITERATION = 20

    def __init__(self):
        self.jankiessArray = [0] * self.ITERATION
        self.frameRateArray = [0] * self.ITERATION
        self.maxDeltaVsyncArray = [0] * self.ITERATION
        self.mSuccessTestRuns = 0

    def record_results(self, test_case, iteration, surface_flinger):
        if not os.path.isdir(self.RAW_DATA_DIR):
            os.makedirs(self.RAW_DATA_DIR)
        raw_file_name = os.path.join(self.RAW_DATA_DIR, '{}_{}.txt'.format(test_case, iteration))
        with open(raw_file_name, 'w') as f:
            f.write(surface_flinger.get_frame_buffer_data())
        jankiness_count = surface_flinger.get_vsync_jankiness()
        framerate = surface_flinger.get_frame_rate()
        max_delta_vaync = surface_flinger.get_max_delta_vsync()
        if jankiness_count >= 0 and framerate > 0:
            self.jankiessArray[iteration] = jankiness_count
            self.frameRateArray[iteration] = framerate
            self.maxDeltaVsyncArray[iteration] = max_delta_vaync
            self.mSuccessTestRuns += 1

    def save_results(self, test_case):
        avg_jankiness_count = self.get_average(self.jankiessArray)
        max_jankiness_count = max(self.jankiessArray)
        avg_frame_rate = self.get_average(self.frameRateArray)
        avg_max_delta_vsync = self.get_average(self.maxDeltaVsyncArray)
        return {
            'testCaseName': test_case,
            'avgJankinessCount': avg_jankiness_count,
            'maxJankinessCount': max_jankiness_count,
            'avgFrameRate': avg_frame_rate,
            'avgMaxDeltaVsync': avg_max_delta_vsync
        }

    def get_average(self, data):
        if not data:
            return 0
        return float(sum(data)) / len(data)
