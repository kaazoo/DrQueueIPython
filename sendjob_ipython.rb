require 'optparse'
require "rubypython" 
RubyPython.start(:python_exe => "python2.6")
sys = RubyPython.import "sys" 
sys.argv = [""]
DrQueue = RubyPython.import("DrQueue")


# parse arguments
options = {}
options[:startframe] = 1
options[:endframe] = 1
options[:blocksize] = 1
options[:options] = "{}"
options[:retries] = 1
options[:owner] = Etc.getlogin
options[:wait] = false
options[:verbose] = false

OptionParser.new do |opts|
    opts.banner = "Usage: "+__FILE__+" [options] -n name -r renderer -f scenefile"
    opts.on("-s N", "--startframe N", Integer, "first frame") do |startframe|
        options[:startframe] = startframe
    end
    opts.on("-e N", "--endframe N", Integer, "last frame") do |endframe|
        options[:endframe] = endframe
    end
    opts.on("-b N", "--blocksize N", Integer, "size of block") do |blocksize|
        options[:blocksize] = blocksize
    end
    opts.on("-n NAME", "--name NAME", String, "name of job") do |name|
        options[:name] = name
    end
    opts.on("-r RENDERER", "--renderer RENDERER", String, "render type (maya|blender|mentalray)") do |renderer|
        options[:renderer] = renderer
    end
    opts.on("-f FILE", "--scenefile FILE", String, "path to scenefile") do |scenefile|
        options[:scenefile] = scenefile
    end
    opts.on("-o OPTS", "--options OPTS", String, "specific options for renderer as Python dict") do |extraoptions|
        options[:options] = extraoptions
    end
    opts.on("--retries N", Integer, "number of retries for every task") do |retries|
        options[:retries] = retries
    end
    opts.on("--owner OWNER", String, "Owner of job. Default is current username.") do |owner|
        options[:owner] = owner
    end
    opts.on("-w", "--wait", "wait for job to finish") do |wait|
        options[:wait] = true
    end
    opts.on("-v", "--verbose", "verbose output") do |verbose|
        options[:verbose] = true
    end
end.parse!


# initialize DrQueue client
client = DrQueue.Client.new

# convert string to Python dict
pyoptions = RubyPython::PyMain.eval(options[:options], {}, {})

# initialize DrQueue job
job = DrQueue.Job.new(options[:name], options[:startframe], options[:endframe], options[:blocksize], options[:renderer], options[:scenefile], options[:retries], options[:owner], pyoptions)

# run job with client
begin
    client.job_run(job)
rescue RubyPython::PythonError => e
    puts e.message
    exit(1)
end

# tasks which have been created
tasks = client.query_task_list(job['name'])

# wait for all tasks of job to finish
if options[:wait]
    tasks.to_enum.each do |task|
        ar = client.task_wait(task['msg_id'])
        # add some verbose output
        if options[:verbose]
            cpl = ar.metadata.completed
            tmsg_id = ar.metadata.msg_id
            status = ar.status
            engine_id = ar.metadata.engine_id
            puts("Task "+tmsg_id.to_s+" finished with status '"+status.to_s+"' on engine "+engine_id.to_s+" at "+cpl.year.to_s+"-"+("%02i-%02i %02i:%02i:%02i" % [cpl.month.to_s.to_i, cpl.day.to_s.to_i, cpl.hour.to_s.to_i, cpl.minute.to_s.to_i, cpl.second.to_s.to_i])+".")
            if ar.pyerr != nil
                puts ar.pyerr
            end
        end
    end
    puts("Job %s finished." % job['name'])
end

RubyPython.stop
