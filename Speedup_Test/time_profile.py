import time
import os
import threading
import pdb
class TimeRecorder:
    list_of_time = []
    first_flag = True
    @staticmethod
    def show_all():
        len_of_list = len(TimeRecorder.list_of_time)
        out_string = "{\"otherData\": {}, \"traceEvents\":["
        for i in range(0,len_of_list):
            if i == len_of_list-1:
                out_string += str(TimeRecorder.list_of_time[i])
            else:
                out_string += str(TimeRecorder.list_of_time[i]) + ','
        out_string += "]}"

        with open('out_test.json', 'w') as f:
            f.write(out_string)

    @staticmethod
    def append_to_file(json_structure):
        if TimeRecorder.first_flag:
            out_string = "{\"otherData\": {}, \"traceEvents\":["
            with open('out_test_dynamic.json', 'w') as f:
                f.write(out_string)
            TimeRecorder.first_flag = False
        
        with open('out_test_dynamic.json', 'a') as f:
            json_structure += ','
            f.write(json_structure)


class TimeProfiler:
    def __init__(self, class_name, function_name):
        self.start_time = time.time()
        self.func_name = function_name
        self.class_name = class_name
        self.stub_name = self.class_name + ':' + self.func_name
        
     
    
    def __del__(self):
        
        self.end_time = time.time()
        self.time_in_s = (self.end_time - self.start_time)
        
        json_structure = f"{{\"cat\": \"function\", \"dur\":{round(self.time_in_s,3)}, \"name\":\"{self.stub_name}\",\"ph\":\"X\", \"pid\":{os.getpid()}, \"tid\":{threading.get_ident()}, \"ts\":{self.start_time}}}"
        TimeRecorder.list_of_time.append(json_structure)
        #imeRecorder.append_to_file(json_structure)
