from PeopleCounter import PeopleCounter
from app.ApplicationContext import ApplicationContext

app_context = ApplicationContext.getApplicationContext()
app_props = app_context.get_props()


def add_people_counter(input_source, source_name=None, skip_frames=None):
    pc_obj = PeopleCounter(input_source=input_source, source_name=source_name, skip_frames=skip_frames)
    app_context.pc_obj_map.update({pc_obj.source_name: pc_obj})
    pc_obj.start()
    # print(app_context.pc_obj_map)


def stop_people_counter(source_name):
    for pc in app_context.pc_obj_map.keys():
        if pc is source_name:
            # call STOP on the object
            app_context.pc_obj_map[source_name].stop_counter()
            return True
    # Counter for given source_name doest not exist
    return False

add_people_counter("videos/example_01.mp4")
# print(stop_people_counter("videos/example_01.mp4"))
