#!/usr/bin/python

import requests
from requests.auth import HTTPDigestAuth
import json
import subprocess
import time
import os
import datetime

prev_val = 0
hot_service = False
counter = 11
hot_service_time_elapsed = 0
while True:
	subprocess.call(['./script.sh'])
	new_val = 0
        local_service_traffic = 0
        time_counter = 0
	Flag = False
        hot_service_time_elapsed = 0
	with open('2.json') as json_file:
		dict = json.load(json_file)
		byte_flag = 0
		for a,b in dict.iteritems():
     			for c,d in b.iteritems():
				leng = len(d)
				for i in range(leng):
             				for e in d[i].iteritems():
               					if e[0] == 'byte_count':
							if int(e[1]) > 0: 		#if byte_count is greater than 1000, capture tcp and ip details
								for f in d[i].iteritems():
									if f[0] == 'match':
										if  bool(f[1]):
											if "tcp_dst" in f[1].keys():
												if(f[1]["ipv4_src"].split('.')[0] == '145' and f[1]["ipv4_src"].split('.')[1] == '14'):
													if(f[1]["tcp_src"] == '80'):
                                                                                                                print f[1]["ipv4_src"]
														new_val = new_val + int(e[1])

	                                                                                if hot_service:
                                                                                                hot_service_time_elapsed = hot_service_time_elapsed + 2
												if "ipv4_src" in f[1].keys() and "ipv4_dst" in f[1].keys():
                                                                                                        if(f[1]["ipv4_src"] == '10.0.0.103' and f[1]["ipv4_dst"] != '10.0.0.100'):
														local_service_traffic =  local_service_traffic + int(e[1])
														if(local_service_traffic < 30000):
															if time_counter == 0 :
																counter = counter - 1
																print "[AEDD:INFO:] SERVICE GOING COLD AGAIN IN {} seconds".format(counter)
															time_counter = time_counter + 1
														Flag = True
		if not Flag and hot_service and hot_service_time_elapsed > 15:
                        if time_counter == 0 :
				counter = counter - 1
                                print "[AEDD:INFO:] SERVICE GOING COLD AGAIN IN {} seconds".format(counter)
                        time_counter = time_counter + 1




        now = datetime.datetime.now()
        print "[AEDD:INFO:]  "
        print "[AEDD:INFO:] Current Time: {}:{}:{}".format(now.hour, now.minute, now.second)
	print "[AEDD:INFO:] Current External Traffic Value: {}".format(new_val)
	print "[AEDD:INFO:] Current Internal Traffic Value: {}".format(local_service_traffic)
	delta = abs(prev_val - new_val) 
        if new_val > 30000:    #THRESHOLD bytecount
            print "[AEDD:INFO:] Traffic increased over Threshold value"
            print "[AEDD:INFO:] "
            print "[AEDD:INFO:] SERVICE CLASSIFIED AS HOT-SERVICE"
            print " "
            hot_service = True
            hot_service_time_elapsed = hot_service_time_elapsed + 2
            try:
                s = subprocess.check_output("kubectl get svc | grep -c run-app-local-svc",shell=True)
            except:
                os.system("kubectl apply -f run_app_local.yaml")
                time.sleep(1)
                os.system("./EditConfigMap.sh")
        if ((hot_service == True and counter == 0)):
            print "[AEDD:INFO:]  "
            print "[AEDD:INFO:] LOCAL SERVICE COLD AGAIN"
            print "[AEDD:INFO:] "
            print "[AEDD:INFO:] Undeploying Edge Application"
            counter = 0
            hot_service = False
            hot_service_time_elapsed = 0
            os.system("./Undeploy.sh")

        prev_val = new_val
	json_file.close()
	time.sleep(1)



