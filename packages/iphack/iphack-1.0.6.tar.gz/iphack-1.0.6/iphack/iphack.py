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
	    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/18.6.872.0 Safari/535.2 UNTRUSTED/1.0 3gpp-gba UNTRUSTED/1.0",
	    "Mozilla/5.0 (Windows NT 6.1; rv:12.0) Gecko/20120403211507 Firefox/12.0",
	    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
	    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:10.0.1) Gecko/20100101 Firefox/10.0.1",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
	    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
	    "Mozilla/5.0 (Windows; U; ; en-NZ) AppleWebKit/527  (KHTML, like Gecko, Safari/419.3) Arora/0.8.0",
	    "Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)",
	    "Mozilla/5.0 (Windows; U; Windows CE 5.1; rv:1.8.1a3) Gecko/20060610 Minimo/0.016",
	    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/531.21.8 (KHTML, like Gecko) Version/4.0.4 Safari/531.21.10",
	    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
	    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.23) Gecko/20090825 SeaMonkey/1.1.18",
	    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10",
	    "Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)",
	    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9",
	    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/533.17.8 (KHTML, like Gecko) Version/5.0.1 Safari/533.17.8",
	    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
	    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/527  (KHTML, like Gecko, Safari/419.3) Arora/0.6 (Change: )"
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
            data7 = requests.get("https://api.ipregistry.co/"+ipaddr+"?key=g54hjdzjnudhhsp4", headers=headers).json()
            a = lgreen+bold+"["+clear+"+"+lgreen+bold+"]"+clear
            r = lgreen+bold+"["+red+bold+"!"+lgreen+bold+"]"+clear
            data9 = data7['location']
            data10 = data9['country']
            data11 = data7['security']
            print(a, "┌──────────[Geolocation]")
            print(a, "├ Status             :", data6['status'])
            print(a, "├ Victim             :", data1['ip'])
            print(a, "┼ Is eu              :", data1['is_eu'])
            print(a, "├ Type               :", data5['version'])
            print(a, "├ City               :", data1['city'])
            print(a, "├ Area               :", data10['area'])
            print(a, "├ Region             :", data1['region'])
            print(a, "├ Region code        :", data1['region_code'])
            print(a, "├ Region type        :", data1['region_type'])
            print(a, "├ Country name       :", data1['country_name'])
            print(a, "├ Country code       :", data1['country_code'])
            print(a, "├ Latitude           :", data1['latitude'])
            print(a, "├ Longitude          :", data1['longitude'])
            print(a, "├ Zip code           :", data1['postal'])
            print(a, "├ Calling code       :", data1['calling_code'])
            print(a, "├ Country area       :", data5['country_area'])
            print(a, "├ Country population :", data5['country_population'])
            print(a, "├ Country capital    :", data5['country_capital'])
            print(a, "├ Country tld        :", data5['country_tld'])
            print(a, "├ Country code iso   :", data5['country_code_iso3'])
            print(a, "├ Currency name      :", data5['currency_name'])
            print(a, "└ Languages          :", data5['languages'])
            data2 = data1['asn']
            data8 = data7['connection']
            data3 = data1['time_zone']
            print(" ")
            print(a, "┌──────────[Router/Time zone]")
            print(a, "├ Asn name           :", data8['asn'])
            print(a, "├ Org name           :", data2['name'])
            print(a, "┼ Reverse            :", data6['reverse'])
            print(a, "├ District           :", data6['district'])
            print(a, "├ Domain             :", data8['domain'])
            print(a, "├ Route              :", data2['route'])
            print(a, "├ Wifi Type          :", data2['type'])
            print(a, "├ Time Zone          :", data3['name'])
            print(a, "├ Abbr               :", data3['abbr'])
            print(a, "├ Offset             :", data3['offset'])
            print(a, "└ Is dst             :", data3['is_dst'])
            print(" ")
            data4 = data1['threat']
            print(a, "┌──────────[Security]")
            print(a, "├ Using tor          :", data11['is_tor'])
            print(a, "├ Using vpn          :", data11['is_vpn'])
            print(a, "┼ Using proxy        :", data11['is_proxy'])
            print(a, "├ Is relay           :", data11['is_relay'])
            print(a, "├ Is hosting         :", data6['hosting'])
            print(a, "├ Is datacenter      :", data4['is_datacenter'])
            print(a, "├ Is anonymous       :", data11['is_anonymous'])
            print(a, "├ Cloud provider     :", data11['is_cloud_provider'])
            print(a, "├ Known attacker     :", data4['is_known_attacker'])
            print(a, "├ Known abuser       :", data4['is_known_abuser'])
            print(a, "├ Is threat          :", data4['is_threat'])
            print(a, "└ Is bogon           :", data4['is_bogon'])

        except KeyboardInterrupt:
            print('Quiting Utility! Bye Bye, Have a nice day!'+lgreen)
            sys.exit(0)
        except requests.exceptions.ConnectionError as e:
            print (red+"[-]"+" Please check your internet connection!"+clear)
            print (red+"[-]"+" Error code: 106 DNS server refused to connect!"+clear)
        except:
            b = red+bold+"[-]"
            print(b, "[Error]: Rate limited, use vpn")
