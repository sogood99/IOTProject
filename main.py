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
    group.add_argument('-ip', '--ip', default="192.168.0.1")
    group.add_argument('-p', '--port', default=5000)

    args = parser.parse_args()

    if args.bluetooth:
        if args.recv:
            bluetooth.recv_gui.startRecvGUI()
        else:
            bluetooth.send_gui.startSendGUI()
    else:
        if args.recv:
            receiver = distance.recv.Recv(args.port)
            receiver.start()
        else:
            sender = distance.send.Sender(args.ip, args.port)
            sender.start()
