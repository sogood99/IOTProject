import argparse
import bluetooth
import distance

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='IOT Project',
        description='Runs Either 1. Bluetooth Emulator, or 2. Distance Estimator',
        epilog='Try python main.py -r bluetooth -f send')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-b', '--bluetooth', default=True,
                       action='store_true')
    group.add_argument('-d', '--distance',
                       action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--send', default=True,
                       action='store_true')
    group.add_argument('-r', '--recv',
                       action='store_true')

    args = parser.parse_args()

    if args.bluetooth:
        if args.recv:
            bluetooth.recv_gui.startRecvGUI()
        else:
            bluetooth.send_gui.startSendGUI()
    else:
        if args.recv:
            pass
        else:
            pass
