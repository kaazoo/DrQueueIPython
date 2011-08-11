require "rubypython" 
RubyPython.start(:python_exe => "python2.6")
sys = RubyPython.import "sys" 
sys.argv = [""]
DrQueue = RubyPython.import("DrQueue")


# initialize DrQueue client
client = DrQueue.Client.new
# fetch a list of all jobs
jobs = client.query_job_list()

jobs.to_enum.each do |job|
  tasks = client.query_task_list(job)
  
  puts("\nTasks of job "+job.to_s+":")
  puts("msg_id                                 status    owner       completed at")

  # to_enum provides Ruby-like iteration
  tasks.to_enum.each do |task|
    tmsg_id = task['msg_id']
    theader = task['header']
    username = theader['username']

    if task['completed'] == nil
      status = "pending"
    else
      result_header = task['result_header']
      status = result_header['status']
      cpl = task['completed']
    end
    # converting Python string to Ruby string and then to Ruby integer helps for using format strings
    puts(tmsg_id+"   "+status.ljust(8)+"  "+username.ljust(10)+"  "+cpl.year.to_s+"-"+("%02i-%02i %02i:%02i:%02i" % [cpl.month.to_s.to_i, cpl.day.to_s.to_i, cpl.hour.to_s.to_i, cpl.minute.to_s.to_i, cpl.second.to_s.to_i]))
  end
end


RubyPython.stop
