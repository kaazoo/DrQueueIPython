require "rubypython" 
RubyPython.start(:python_exe => "python2.7")
sys = RubyPython.import "sys" 
sys.argv = [""]
DrQueue = RubyPython.import("DrQueue")


# initialize DrQueue client
client = DrQueue.Client.new
# fetch a list of all jobs
jobs = client.query_job_list()

jobs.to_enum.each do |job|
  tasks = client.query_task_list(job['_id'])
  meantime, time_left, finish_time = client.job_estimated_finish_time(job['_id'])
  
  puts("\nJob \"" + job['name'].to_s + "\" (ID: " + job['_id'].to_s + "):")
  puts("Overall status: " + client.job_status(job['_id']).to_s)
  puts("Submit time: "+ job['submit_time'].to_s)
  if job['requeue_time'] != false
    puts("Requeue time: "+ job['requeue_time'].to_s)
  end
  puts("Time per task: " + meantime.to_s)
  if client.query_job_tasks_left(job['_id']) > 0
    puts("Time left: " + time_left.to_s)
    puts("Estimated finish time: " + finish_time.to_s)
  else
    puts("Finish time: " + finish_time.to_s)
  end
  puts("Task id                                 status    owner       completed at")

  # to_enum provides Ruby-like iteration
  tasks.to_enum.each do |task|
    tmsg_id = task['msg_id']
    theader = task['header']
    username = theader['username']

    if task['completed'] == nil
      status = "pending"
      puts(tmsg_id+"   "+status.ljust(8)+"  "+username.ljust(10))
    else
      result_header = task['result_header']
      result_content = task['result_content']
      status = result_header['status']
      cpl = task['completed']
      # converting Python string to Ruby string and then to Ruby integer helps for using format strings
      puts(tmsg_id+"   "+status.ljust(8)+"  "+username.ljust(10)+"  "+cpl.year.to_s+"-"+("%02i-%02i %02i:%02i:%02i" % [cpl.month.to_s.to_i, cpl.day.to_s.to_i, cpl.hour.to_s.to_i, cpl.minute.to_s.to_i, cpl.second.to_s.to_i]))

      if result_header['status'] == 'error'
        puts("  Error was: " + result_content['evalue'])
      end
    end
  end
end


RubyPython.stop
