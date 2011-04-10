from optparse import OptionParser
import platform
import os
from IPython.kernel import client
from IPython.kernel.task import StringTask


def get_osname():
    osname = platform.system()
    if osname == 'Darwin':
        osname = 'OSX'
    return osname


def get_rendertemplate(renderer):
    if renderer == 'blender':
        filename = 'blender_sg.py'
    if renderer == 'maya':
        filename = 'maya_sg.py'
    if renderer == 'mentalray':
        filename = 'mentalray_sg.py'
    return filename    


def main():
    # parse arguments
    parser = OptionParser()
    parser.usage = "%prog [options] -r renderer -f scenefile"
    parser.add_option("-s", "--startframe", dest="startframe", default=1,
                      help="first frame")
    parser.add_option("-e", "--endframe", dest="endframe", default=1,
                      help="last frame")
    parser.add_option("-b", "--blocksize", dest="blocksize", default=1,
                      help="size of block")
    parser.add_option("-f", "--scenefile", dest="scenefile", default=1,
                      help="path to scenefile")
    parser.add_option("-r", "--renderer", dest="renderer",
                      help="render type (maya|blender|mentalray)")
    parser.add_option("-v", "--verbose",
                      action="store_false", dest="verbose", default=True,
                      help="verbose output")
    (options, args) = parser.parse_args()

    # initialize IPython
    tc = client.TaskClient()

    task_ids = list()
    task_frames = range(int(options.startframe), int(options.endframe)+1, int(options.blocksize))

    for x in task_frames:
        # prepare script input
        push_dict = {
        'DRQUEUE_OS' : get_osname(),
        'DRQUEUE_ETC' : os.getenv('DRQUEUE_ROOT') + "/etc",
        'DRQUEUE_FRAME' : x,
        'DRQUEUE_BLOCKSIZE' : int(options.blocksize),
        'DRQUEUE_ENDFRAME' : int(options.endframe),
        'SCENE' : options.scenefile,
        'RENDER_TYPE' : "animation"
        }

        # prepare task
        work = "execfile(\"" + os.getenv('DRQUEUE_ROOT') + "/etc/" + get_rendertemplate(options.renderer) + "\")"
        mytask = StringTask(work, push=push_dict, clear_before=True)

        # run task on cluster

        task_id = tc.run(mytask)
        task_ids.append(task_id)

    for x in task_ids:
        task_results = tc.get_task_result(x, True)
        print("Task %i was running on %i and took %f seconds to run." % (x,task_results.engineid,task_results.duration))

        if task_results.failure:
            print("task failed:")
            print(task_results.failure)


if __name__ == "__main__":
    main()


