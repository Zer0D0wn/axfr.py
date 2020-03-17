#!/usr/bin/env python3
# coding: utf-8
# This script try to do a zone transfer on the target server.

import sys

#Usage
if len(sys.argv) != 2 or sys.argv[1] in ("--help", "-h"):
    print("Usage :",sys.argv[0],"<domain>\n\n-h or --help : show this message")
    exit(0)

# Validate the sys.argv[0]
import re
if sys.argv[1][-1] == ".":
    sys.argv[1] = sys.argv[0][:-1] # Delete the last '.'
if len(sys.argv[1]) > 253:
    sys.stderr.write('Error: invalid hostname, he is too long\n')
    exit(1)

hostname_part = sys.argv[1].split(".")

if re.match(r"[0-9]+$", hostname_part[-1]):
       sys.stderr.write('Error, the Top Level Domain can\'t be only numeric\n')
       exit(1)

regex = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)

if (all(regex.match(label) for label in hostname_part)) == False:
    sys.stderr.write('Error, an part of the hostname is invalid\n')
    exit(1)

#Modules
#import dns.resolver
import dns.name, dns.resolver

#Search for DNS
hostname = dns.name.from_text(sys.argv[1])
try:
    while True:
        try:
            # Send request
            ns_servers = dns.resolver.query(hostname, 'NS')
        except dns.resolver.NXDOMAIN:
            sys.stderr.write("Invalid hostname, trying with the parent\n\n")
        except dns.resolver.NoAnswer:
            print("| No NS recording for",hostname.to_text()+", attempt with the parent. |")
        else :
            print("NS recording found for",hostname.to_text(),":")
            records = [] # Save the records
            for record in ns_servers:
                actual_record = record.to_text()
                print("\t"+actual_record)
                records.append(actual_record)
            break;
        # Try with parent
        hostname = hostname.parent()

except dns.name.NoParent:
    #If no parent
    sys.stderr.write("No NS server found")
    exit(1)

# AXFR
print("\n\nWould you try an AXFR ? (yes/no)")
user_input = input("==> ")
while user_input not in ("yes", "no"):
    print("Invalid input, retry (yes/no):")
    user_input = input("==> ")

if user_input == "no":
    exit(0)

# Do AXFR
import dns.zone, dns.query

for entry in records:
    try :
        name_server = dns.zone.from_xfr(dns.query.xfr(entry,hostname.to_text()))
    except:
        print("Unable to AXFR",entry+"\n")
    else:
        print("AXFR of",entry,":")
        axfr_result = name_server.nodes.keys()
        for i in axfr_result:
            print(name_server[i].to_text(i))
    print("\n")
