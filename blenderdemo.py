import bpy
from bpy.props import IntProperty, FloatVectorProperty
from OSC import OSCServer

class ModalOperator(bpy.types.Operator):
    """Move an object with the leap"""
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"

    first_mouse_x = IntProperty()
    first_value = FloatVectorProperty()

    def log_timestamp(self, path, tags, args, source):
        print(path)
        print(args)
        print(source)
        print("-----------")

    def move_object(self, path, tags, args, source):
        #/leap/frame/hand/pos
        self.obj.location.x = args[1]/10
        self.obj.location.z = args[2]/10
        self.obj.location.y = -1*args[3]/10

    def quit_callback(self, path, tags, args, source):
        print("Quit callback")
        self.server.close()

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            print("LM Close Server")
            self.server.close()
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("Cancelled Close Server")
            context.object.location = self.first_value
            self.server.close()
            return {'CANCELLED'}

        elif event.type == 'TIMER':
            print("TIMER")
            self.server.handle_request()
            print("-----")

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        if context.object:
            SERVER_ADDR = 7113
            self.server = OSCServer( ("localhost", SERVER_ADDR) )
            self.server.timeout = 0

            self.server.addMsgHandler( "/leap/frame/timestamp", self.log_timestamp )
            self.server.addMsgHandler( "/leap/frame/hand/pos", self.move_object )
            self.server.addMsgHandler( "/leap/frame/hand/orientation", self.log_timestamp )
            self.server.addMsgHandler( "/quit", self.quit_callback )

            self.first_mouse_x = event.mouse_x
            self.first_value = context.object.location

            context.window_manager.modal_handler_add(self)

            self._timer = context.window_manager.event_timer_add(0.001, context.window)

            self.obj = context.object 

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(ModalOperator)


def unregister():
    bpy.utils.unregister_class(ModalOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.modal_operator('INVOKE_DEFAULT')
