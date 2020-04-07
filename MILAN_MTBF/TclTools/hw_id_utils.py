import getmac

hw_id = None


def get_hw_id(force_update=False):
    global hw_id
    if not hw_id or force_update:
        hw_id = getmac.get_mac_address()
    return hw_id

