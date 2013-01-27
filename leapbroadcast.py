import Leap, sys
from OSC import OSCClient, OSCMessage, OSCBundle

SERVER_ADDR = 7113

class LeapListener(Leap.Listener):
    def __init__(self, osc_client):
        Leap.Listener.__init__(self)
        self.osc_client = osc_client
        self.server_running = True

    def on_init(self, controller):
        print("Initialized")
        self.osc_client.connect( ("localhost", SERVER_ADDR) )
        print("Done Init")

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        print("Disconnected")
        self.osc_client.send( OSCMessage("/quit") )

    def on_exit(self, controller):
        print("Exited")
        self.osc_client.send( OSCMessage("/quit") )

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        print ("Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d" % (
                      frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools)))

        if not frame.hands.empty:
            bundle = OSCBundle()

            bundle.append(OSCMessage("/leap/frame/timestamp", str(frame.timestamp)))

            for hand in frame.hands:
                handPos = OSCMessage("/leap/frame/hand/pos",
                    [hand.id, hand.palm_position[0], hand.palm_position[1], hand.palm_position[2]])
                bundle.append(handPos)
                normal = hand.palm_normal
                direction = hand.direction
                #handOrientation = OSCMessage("/leap/frame/hand/orientation",
                #    [hand.id, hand.palm_position[0], hand.palm_position[1], hand.palm_position[2]])
                #bundle.append(handOrientation)

            try:
                self.osc_client.send(bundle)
            except:
                print("Unable to connect to server!")
                
def main():
    # Create a listener and controller
    listener = LeapListener(OSCClient())
    controller = Leap.Controller()

    # Have the listener receive events from the controller
    controller.add_listener(listener)

    # Keep this OSC client running until Enter is pressed
    print("Press Enter to quit...")
    sys.stdin.readline()

    # Remove the sample listener when done
    controller.remove_listener(listener)

if __name__ == "__main__":
    main()