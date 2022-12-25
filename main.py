import argparse
import bluetooth
import distance

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='IOT Project',
        description='Runs Either 1. Bluetooth Emulator, or 2. Distance Estimator',
        epilog='Try python main.py -r bluetooth -f send')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-b', '--bluetooth',
                       action='store_true')
    group.add_argument('-d', '--distance',
                       action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--send',
                       action='store_true')
    group.add_argument('-r', '--recv',
                       action='store_true')
    parser.add_argument('-ip', '--ip', action="store",
                        default="192.168.0.1", type=str)
    parser.add_argument('-p', '--port', action="store", default=5000, type=int)
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    if args.bluetooth:
        if args.recv:
            bluetooth.recv_gui.startRecvGUI(args.debug)
        else:
            bluetooth.send_gui.startSendGUI(args.debug)
    else:
        if args.recv:
            receiver = distance.recv.Recv(args.port)
            receiver.start()
        else:
            sender = distance.send.Sender(args.ip, args.port)
            sender.start()
