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
        
    # prepare script input
    push_dict = {
    'DRQUEUE_OS' : get_osname(),
    'DRQUEUE_ETC' : "/usr/local/drqueue/etc",
    'DRQUEUE_FRAME' : int(options.startframe),
    'DRQUEUE_BLOCKSIZE' : int(options.blocksize),
    'DRQUEUE_ENDFRAME' : int(options.endframe),
    'SCENE' : options.scenefile,
    'RENDER_TYPE' : "animation"
    }

    # prepare task
    work = "execfile(\"" + os.getenv('DRQUEUE_ROOT') + "/etc/" + get_rendertemplate(options.renderer) + "\")"
    mytask = StringTask(work, push=push_dict, clear_before=True)
    
    # run task on cluster
    tc = client.TaskClient()
    task_id = tc.run(mytask)
    
    task_results = tc.get_task_result(task_id, True)
    print("Task %i was running on %i and took %f seconds to run." % (task_id,task_results.engineid,task_results.duration))
    
    if task_results.failure:
        print("task failed:")
        print(task_results.failure)


if __name__ == "__main__":
    main()


