import log_utils


def number_tel(device):
    number = {
        "5000000100": ["665692", "18658235692"],  # Athena stability
        # "5900000040": ["661360", "18658271360"],  # Athena stability
        "5000000229": ["660741", "18668570741"],  # Athena stability
        "5000000208": ["667201", "18658237201"],  # Athena stability
        "5000000266": ["662025", "18668572025"],  # Athena stability  dual sim

        "5000000184": ["667816", "18668537816"],  # Athena endurance 1
        "5900000040": ["666927", "18658456927"],  # Athena endurance 2
        "5000002595": ["683", "18267421737"],  # Luna endurance Mdevice
        "5000002965": ["666", "18267429151"],  # Luna endurance Sdevice
        "1163817824": ["668713", "18658238713"],
    }
    if number.has_key(device):
        return number[device]
    else:
        log_utils.get_common_logger().warning("%s device not number exists" % device)
        return None, None
