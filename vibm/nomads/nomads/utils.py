import os

import subprocess

def ping_host_full_response(hostname):
    cmd = "ping -c 1 " + hostname

    try: 
        output = subprocess.check_output( cmd.split(" ") ).decode().strip()
        lines = output.split("\n")
        
        #total = lines[-2].split(",")[3].split()[1]
        
        print( "&&&&& : %s" % lines[1])
        bytes_icmp_ttl = lines[1].split(":")
        bytes_   = bytes_icmp_ttl[0].split(" ")[0].strip()
        icmp_seq = bytes_icmp_ttl[1].split(" ")[1].split("=")[1].strip()
        ttl      = bytes_icmp_ttl[1].split(" ")[2].split("=")[1].strip()
        time_ms  = bytes_icmp_ttl[1].split(" ")[3].split("=")[1].strip()

        print("bytes = %s ... icmp_seq = %s ... ttl = %s ... time_ms = %s" % (bytes_ , icmp_seq, ttl, time_ms) )

        ping_dns_ip = lines[0]
        split0 = ping_dns_ip.split(" ")
        dns = split0[1]
        ip  = split0[2]
        #print("dns = %s ... ip = %s" % (dns, ip) )

        # print( "+++++ : %s", lines[-1] )
        rtt_min_max = lines[-1]
        split1 = rtt_min_max.split("=")
        min_avg_maxmdev = split1[1].split(" ")[1].strip()
        min  = min_avg_maxmdev.split("/")[0].strip()
        avg  = min_avg_maxmdev.split("/")[1].strip()
        max  = min_avg_maxmdev.split("/")[2].strip()
        mdev = min_avg_maxmdev.split("/")[3].strip()
        unit = split1[1].split(" ")[2].strip()
        # print("min/avg/max/ mdev ... %s/ %s/ %s/ %s %s" % (min, avg, max, mdev, unit))

        # print( "***** : %s", total )
        packets_transm_recv = lines[-2]
        print( "***** : %s", packets_transm_recv )
        transmitted = packets_transm_recv.split(",")[0].split()[0].strip() + " p"
        received    = packets_transm_recv.split(",")[1].split()[0].strip() + " p"
        loss        = packets_transm_recv.split(",")[2].split()[0].strip() 
        
        time_spent  = packets_transm_recv.split(",")[3].strip()
        print("Packets Transmitted = %s ... Received = %s ... Loss = %s ... Time = %s" % (transmitted, received, loss, time_spent))

        data = { 
            "bytes": bytes_, "icmp_seq": icmp_seq, "ttl": ttl, "time_ms": time_ms,
            "ip": ip, "dns": dns, "min": min, "avg": avg, "max": max, "mdev": mdev, "unit": unit, 
            "transmitted": transmitted, "received": received, "loss": loss, "time-spent": time_spent
        }

        return data

    except Exception as e:
        print(e)
        return None

def ping_host(hostname):
    cmd = "ping -c 1 " + hostname

    response = os.system(cmd)
    
    if response == 0:
        return "Up!"
    else:
        return "Down?"

def scan_vlab_open_ports_now( hostname ):
    # cmd = "nmap -sU -sT " + hostname
    cmd = "nmap -sT " + hostname
    
    response = subprocess.check_output( cmd, shell=True )
    
    response_utf8 = response.decode('utf-8').strip()
    
    print("Open Ports NMAP Response ... %s" % response_utf8)

    lines = response_utf8.split("\n")

    if "down" in lines[1]:
        print("Specific Host seems to be Down!")
        return [{"Port": "None", "State": "Server Down", "Service": "None"}]

    target = lines[1].split()[-2:]
    target = '-'.join( target )

    # print("Target is ... %s" % (target))
    
    num_filtered_ports = lines[4].split(":")[1].strip().split()[0].strip()
    
    # print("Number of Filtered Ports ... %s" % (num_filtered_ports))
    open_ports = []

    a = 6
    for i in range(20):
        b = a + i

        if not lines[ b ]:
            a = b+1
            break

        #print("Port is ... %s" % lines[b] )
        
        op_dict = {
            "Port": lines[b].split()[0].strip(),
            "State": lines[b].split()[1].strip(),
            "Service": lines[b].split()[2].strip(),
        }

        open_ports.append( op_dict )
    
    done_resp = lines[a].split(":")[1].strip()
    host_is_up = done_resp[
        done_resp.find("(") + 1: 
        done_resp.find(")")]

    scan_time  = done_resp.split()[-2:]

    #print("*** %s\n+++ %s" % (response_utf8, scan_time))

    data = {
        "target": target, "num-filtered-ports": num_filtered_ports, "open-ports": open_ports,
        "host-is-up": host_is_up, "scan-time": scan_time, 
    }

    #return data
    return open_ports

def write_tsv_file():
    import csv

    with open("gui/data/data_waterfall.tsv", "wt") as out_file:
        tsv_writer = csv.writer(out_file, delimiter="\t")
        
        """tsv_writer.writerow(["age", "population"])
        tsv_writer.writerow(["<5", "2704659"])
        tsv_writer.writerow(["5-13", "4499890"])
        tsv_writer.writerow(["14-17", "2159981"])
        tsv_writer.writerow(["18-24", "3853788"])
        tsv_writer.writerow(["25-44", "14106543"])
        tsv_writer.writerow(["45-64", "8819342"])
        tsv_writer.writerow([">64", "612463"])"""

        """tsv_writer.writerow(["letter", "frequency"])
        tsv_writer.writerow(["A", ".08167"])
        tsv_writer.writerow(["B", ".01492"])
        tsv_writer.writerow(["C", ".02782"])
        tsv_writer.writerow(["D", ".04253"])
        tsv_writer.writerow(["E", ".12702"])
        tsv_writer.writerow(["F", ".02288"])
        tsv_writer.writerow(["G", ".02015"])
        tsv_writer.writerow(["H", ".06094"])
        tsv_writer.writerow(["I", ".06966"])
        tsv_writer.writerow(["J", ".00153"])
        tsv_writer.writerow(["K", ".00722"])"""

        tsv_writer.writerow(["region", "value"])
        tsv_writer.writerow(["server-A", "47"])
        tsv_writer.writerow(["server-B", "22"])
        tsv_writer.writerow(["server-C", "12"])
        tsv_writer.writerow(["arm-A", "7"])
        tsv_writer.writerow(["arm-B", "-3"])
        tsv_writer.writerow(["arm-C", "-26"])
        tsv_writer.writerow(["rts-pico", "-69"])


    
    return

    return

if __name__ == "__main__":
    write_tsv_file()