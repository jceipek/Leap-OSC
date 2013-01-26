import bpy
from bpy.props import IntProperty, FloatProperty
from OSC import OSCServer

class ModalOperator(bpy.types.Operator):
    """Move an object with the leap"""
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"

    def log_timestamp(self, path, tags, args, source):
        print(path)
        print(args)
        print(source)
        print("-----------")

    def quit_callback(self, path, tags, args, source):
        self.server.close()

    first_mouse_x = IntProperty()
    first_value = FloatProperty()

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            delta = self.first_mouse_x - event.mouse_x
            context.object.location.x = self.first_value + delta * 0.01
            self.server.handle_request()

        elif event.type == 'LEFTMOUSE':
            self.server.close()
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.object.location.x = self.first_value
            self.server.close()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            SERVER_ADDR = 7113
            self.server = OSCServer( ("localhost", SERVER_ADDR) )
            self.server.timeout = 0

            self.server.addMsgHandler( "/leap/frame/timestamp", self.log_timestamp )
            self.server.addMsgHandler( "/leap/frame/hand/pos", self.log_timestamp )
            self.server.addMsgHandler( "/leap/frame/hand/orientation", self.log_timestamp )
            self.server.addMsgHandler( "/quit", self.quit_callback )

            self.first_mouse_x = event.mouse_x
            self.first_value = context.object.location.x

            context.window_manager.modal_handler_add(self)
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
