import os, sys, json, requests, random

red = '\033[31m'
yellow = '\033[93m'
lgreen = '\033[92m'
clear = '\033[0m'
bold = '\033[01m'
cyan = '\033[96m'

class ip:
    def address(*ips:str):
        users = [
	    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3831.6 Safari/537.36",
	    "Mozilla/5.0 (Linux; Android 8.0.0; SM-G930F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Mobile Safari/537.36",
	    "Mozilla/5.0 (Linux; Android 9; POCOPHONE F1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.136 Mobile Safari/537.36",
	    "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36",
	    "Mozilla/5.0 (Linux; Android 6.0.1; vivo 1603 Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.83 Mobile Safari/537.36",
	    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
	    "Mozilla/5.0 (X11; Linux i686; rv:67.0) Gecko/20100101 Firefox/67.0",
	    "Mozilla/5.0 (Android 9; Mobile; rv:67.0.3) Gecko/67.0.3 Firefox/67.0.3",
	    "Mozilla/5.0 (Android 7.1.1; Tablet; rv:67.0) Gecko/67.0 Firefox/67.0",
	    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.27 Safari/537.36 OPR/62.0.3331.10 (Edition beta)",
	    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
	    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
	    "Mozilla/5.0 (Android; Linux armv7l; rv:10.0.1) Gecko/20100101 Firefox/10.0.1 Fennec/10.0.1",
	    "Mozilla/5.0 (Android; Linux armv7l; rv:2.0.1) Gecko/20100101 Firefox/4.0.1 Fennec/2.0.1",
	    "Mozilla/5.0 (WindowsCE 6.0; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
	    "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
	    "Mozilla/5.0 (Windows NT 5.2; rv:10.0.1) Gecko/20100101 Firefox/10.0.1 SeaMonkey/2.7.1",
	    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
	    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/18.6.872.0 Safari/535.2 UNTRUSTED/1.0 3gpp-gba UNTRUSTED/1.0"
        ]
        headers = {
		'User-Agent' : random.choice(users)
	}
        ipaddr = " ".join([str(m) for m in ips])
        print(red+"""
██╗██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗
██║██╔══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝
██║██████╔╝███████║███████║██║░░╚═╝█████═╝░
██║██╔═══╝░██╔══██║██╔══██║██║░░██╗██╔═██╗░
██║██║░░░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""+red)
        print(yellow+bold+"        Developer: Misha Korzhik "+clear)
        print(yellow+bold+"           Tool Version: v1.4 \n"+clear)
        try:
            ipdata_list = ['?api-key=6818a70bf0dcdbf1dd6bf89e62299740a49725ac65ff8e4056e3b343', '?api-key=7d9bf69a54c63b6f9274c6074b2f50aee46208d10a33533452add840', '?api-key=6453632fcabd2a4c2de4bb45ab35254594fd719e61d58bacde4429f0']
            ipdata = random.choice(ipdata_list)
            paste = "https://api.ipdata.co/"+ipaddr+ipdata
            data1 = requests.get(paste, headers=headers).json()
            data5 = requests.get("https://ipapi.co/"+ipaddr+"/json/", headers=headers).json()
            data6 = requests.get("http://ip-api.com/json/"+ipaddr+"?fields=status,message,isp,org,as,reverse,mobile,proxy,hosting,query,district", headers=headers).json()
            a = lgreen+bold+"[>]"
            print(a, "[Status]:", data6['status'])
            print(a, "[Victim]:", data1['ip'])
            print(a, "[Is eu]:", data1['is_eu'])
            print(a, "[Type]:", data5['version'])
            print(a, "[City]:", data1['city'])
            print(a, "[Region]:", data1['region'])
            print(a, "[Region Code]:", data1['region_code'])
            print(a, "[Region Type]:", data1['region_type'])
            print(a, "[Country Name]:", data1['country_name'])
            print(a, "[Country Code]:", data1['country_code'])
            print(a, "[Latitude]:", data1['latitude'])
            print(a, "[Longitude]:", data1['longitude'])
            print(a, "[Zip code]:", data1['postal'])
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
            print(a, "[Reverse]:", data6['reverse'])
            print(a, "[District]:", data6['district'])
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
            print(a, "[Hosting]:", data6['hosting'])
            print(a, "[Is datacenter]:", data4['is_datacenter'])
            print(a, "[Is anonymous]:", data4['is_anonymous'])
            print(a, "[Is known attacker]:", data4['is_known_attacker'])
            print(a, "[Is known abuser]:", data4['is_known_abuser'])
            print(a, "[Is threat]:", data4['is_threat'])
            print(a, "[Is bogon]:", data4['is_bogon'])

        except KeyboardInterrupt:
            print('Quiting Utility! Bye Bye, Have a nice day!'+lgreen)
            sys.exit(0)
        except requests.exceptions.ConnectionError as e:
            print (red+"[-]"+" Please check your internet connection!"+clear)
            print (red+"[-]"+" Error code: 106 DNS server refused to connect!"+clear)
        except:
            b = red+bold+"[-]"
            print(b, "[Error]: Rate limited, use vpn")
