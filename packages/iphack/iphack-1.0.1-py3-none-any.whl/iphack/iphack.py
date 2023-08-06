import os, sys, json, requests, random

red = '\033[31m'
yellow = '\033[93m'
lgreen = '\033[92m'
clear = '\033[0m'
bold = '\033[01m'
cyan = '\033[96m'

class ip:
    def address(self, *ips:str):
        ipaddr = " ".join([str(m) for m in ips])
        f = open("ip.txt", "w")
        f.write(ipaddr)
        f.close()
        print(red+"""
██╗██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗
██║██╔══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝
██║██████╔╝███████║███████║██║░░╚═╝█████═╝░
██║██╔═══╝░██╔══██║██╔══██║██║░░██╗██╔═██╗░
██║██║░░░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""+red)
        print(yellow+bold+"        Developer: Misha Korzhik "+clear)
        print(yellow+bold+"           Tool Version: v1.1 \n"+clear)
        try:
            r = open("ip.txt", "r")
            ipaddress = r.read()
            ipdata_list = ['?api-key=6818a70bf0dcdbf1dd6bf89e62299740a49725ac65ff8e4056e3b343', '?api-key=7d9bf69a54c63b6f9274c6074b2f50aee46208d10a33533452add840', '?api-key=6453632fcabd2a4c2de4bb45ab35254594fd719e61d58bacde4429f0']
            ipdata = random.choice(ipdata_list)
            paste = "https://api.ipdata.co/"+ipaddress+ipdata
            data1 = requests.get(paste).json()
            data5 = requests.get("https://ipapi.co/"+ipaddr+"/json/").json()
            a = lgreen+bold+"[>]"
            print(a, "[Status]: success")
            print(a, "[Victim]:", data1['ip'])
            print(a, "[Is eu]:", data1['is_eu'])
            #print(a, "[Type]:", data5['version'])
            print(a, "[City]:", data1['city'])
            print(a, "[Region]:", data1['region'])
            print(a, "[Region Code]:", data1['region_code'])
            print(a, "[Region Type]:", data1['region_type'])
            print(a, "[Country Name]:", data1['country_name'])
            print(a, "[Country Code]:", data1['country_code'])
            print(a, "[Latitude]:", data1['latitude'])
            print(a, "[Longitude]:", data1['longitude'])
            print(a, "[Postal]:", data1['postal'])
            print(a, "[Calling Code]:", data1['calling_code'])
            print(a, "[Country Area]:", data5['country_area'])
            print(a, "[Country Population]:", data5['country_population'])
            print(a, "[Country capital]:", data5['country_capital'])
            print(a, "[Country tld]:", data5['country_tld'])
            print(a, "[Country Code iso]:", data5['country_code_iso3'])
            print(a, "[Currency name]:", data5['currency_name'])
            print(a, "[Languages]:", data5['languages'])
            data2 = data1['asn']
            print(" ")
            print(a, "[Asn]:", data2['asn'])
            print(a, "[Org]:", data2['name'])
            print(a, "[Domain]:", data2['domain'])
            print(a, "[Route]:", data2['route'])
            print(a, "[Wifi Type]:", data2['type'])
            data3 = data1['time_zone']
            print(a, "[Time Zone]:", data3['name'])
            print(a, "[Abbr]:", data3['abbr'])
            print(a, "[Offset]:", data3['offset'])
            print(a, "[Is dst]:", data3['is_dst'])
            print(" ")
            data4 = data1['threat']
            print(a, "[Tor]:", data4['is_tor'])
            print(a, "[Proxy]:", data4['is_proxy'])
            print(a, "[Is Datacenter]:", data4['is_datacenter'])
            print(a, "[Is Anonymous]:", data4['is_anonymous'])
            print(a, "[Is known attacker]:", data4['is_known_attacker'])
            print(a, "[Is known abuser]:", data4['is_known_abuser'])
            print(a, "[Is Threat]:", data4['is_threat'])
            print(a, "[Is Bogon]:", data4['is_bogon'])
            f.close()

        except KeyboardInterrupt:
            print('Quiting Utility! Bye Bye, Have a nice day!'+lgreen)
            sys.exit(0)
        except requests.exceptions.ConnectionError as e:
            print (red+"[-]"+" Please check your internet connection!"+clear)
            print (red+"[-]"+" Error code: 106 DNS server refused to connect!"+clear)
