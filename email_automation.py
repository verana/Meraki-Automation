#need to install service_identity, twisted,

from twisted.internet import task
from twisted.internet import reactor
import os
import datetime
import csv
import datetime
import json
import requests
import sys
import time

import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

timeout = 100.0 # 5 mins

#CSV file for the total output


#csv_file = open("ApplianceNetworkDisconnection_" + str(today) + '.csv', 'a', encoding='utf-8')
#fieldnames = ['Network', 'Time']
#writer = csv.DictWriter(csv_file, fieldnames=fieldnames, restval='')
#writer.writeheader()


'''define a global dictionary for the devices and disconnction timestamp'''
device_names = ["Stamford GB", "2Poole GB", "Aycliffe Village GB", "Daventry GB", "San_Diego_CA", "Solihul JLR GB", "Barcelona ES", "Spitfire Park GB", "New Holland_PA", "Nogales_Mex", "Basildon CNH New Holland GB", "Rolo IT", "Istanbul Finance TR", "Brescia IT", "McAllen TX", "china vpn", "Coppell_TX", "Zappon_Mex", "ian_Larkin", "Austin_TX", "Eufaula_AL", "Queretaro_Mex", "Seymour_IN", "open_mexico", "Whitakers_NC", "Bredbury GB", "mexicali_Mex", "San_Luis_Mex_mabe", "San_Luis_Mex_cgt", "Valencia ES", "Pune_IND", "Pickering GB", "Pointe_Claire_QC", "TEST Tulsa_OK", "Darlington GB", "Brugge BE", "San_Jose", "Ageo_City_Jpn", "Elmdon GB", "Stafford GB", "2Schwalbach DE", "Nogales_AZ", "Mannheim DE", "Bielefeld DE", "Barlborough GB", "Norwich Lotus Cars GB", "Crewe GB", "Tuzla Istanbul TR", "Bulgaria BG", "Droitwich GB", "Gateshead GB", "Douai FR", "Sarreguemines FR", "Bordeaux FR", "Columbus", "Jackson  Tn", "Daventry Cummings GB", "operator2", "charles metcalf temp", "Ashland Oh", "shameka giles temp", "Sturtvant WI", "Glenview test new cfg", "Glenview test new cfg", "Jamestown_NY", "troy money", "Xenia_OH", "eric hensly temp", "john adams temp", "York Pa Harley", "Grand Island NE", "operator1", "Tulsa_Navistar", "Greenville SC", "1Core Aurora", "1Wood Dale core network"];

device_dict = {}
for device_name in device_names:
    device_dict[device_name] = []

'''global list for disconnected devices'''
disconnected_devices = []

def get_network_name(network_id, networks):
    return [element for element in networks if network_id == element['id']][0]['name']

def update_timestamp():
    if __name__ == '__main__':
        # Import API key and org ID from login.py
        try:
            import login
            (API_KEY, ORG_ID) = (login.api_key, login.org_id)
        except ImportError:
            API_KEY = input('Enter your Dashboard API key: ')
            ORG_ID = input('Enter your organization ID: ')

        # Find all appliance networks (MX, Z1, Z3, vMX100)
        session = requests.session()
        headers = {'X-Cisco-Meraki-API-Key': API_KEY, 'Content-Type': 'application/json'}

        try:
            name = json.loads(session.get('https://api.meraki.com/api/v0/organizations/' + ORG_ID, headers=headers).text)['name']
        except:
            sys.exit('Incorrect API key or org ID, as no valid data returned')

        networks = json.loads(session.get('https://api.meraki.com/api/v0/organizations/' + ORG_ID + '/networks', headers=headers).text)
        inventory = json.loads(session.get('https://api.meraki.com/api/v0/organizations/' + ORG_ID + '/inventory', headers=headers).text)
        appliances = [device for device in inventory if device['model'][:2] in ('MX', 'Z1', 'Z3', 'vM') and device['networkId'] is not None]

        #all the MX devices
        mx_s = [device for device in inventory if device['model'][:2] in ('MX') and device['networkId'] is not None]
        disconnect_network_list = []
        fd = open("device_list.txt",'w');


        for mx in mx_s:
            network_name = get_network_name(mx['networkId'], networks)
            print("Checking network: " + network_name)
            device_name = json.loads(session.get('https://api.meraki.com/api/v0/networks/' + mx['networkId'] + '/devices/' + mx['serial'], headers=headers).text)['name']
            try:
                perfscore = json.loads(session.get('https://api.meraki.com/api/v0/networks/' + mx['networkId'] + '/devices/' + mx['serial'] + '/performance', headers=headers).text)['perfScore']
            except:
                perfscore = None
            try:
                print('Found appliance ' + device_name)
            except:
                print('Found appliance ' + mx['serial'])
            uplinks_info = dict.fromkeys(['WAN1', 'WAN2', 'Cellular'])
            uplinks_info['WAN1'] = dict.fromkeys(['interface', 'status', 'ip', 'gateway', 'publicIp', 'dns', 'usingStaticIp'])
            uplinks_info['WAN2'] = dict.fromkeys(['interface', 'status', 'ip', 'gateway', 'publicIp', 'dns', 'usingStaticIp'])
            uplinks_info['Cellular'] = dict.fromkeys(['interface', 'status', 'ip', 'provider', 'publicIp', 'model', 'connectionType'])
            uplinks = json.loads(session.get('https://api.meraki.com/api/v0/networks/' + mx['networkId'] + '/devices/' + mx['serial'] + '/uplink', headers=headers).text)

            for uplink in uplinks:
                if uplink['interface'] == 'WAN 1':
                    for key in uplink.keys():
                        uplinks_info['WAN1'][key] = uplink[key]
                elif uplink['interface'] == 'WAN 2':
                    for key in uplink.keys():
                        uplinks_info['WAN2'][key] = uplink[key]
                elif uplink['interface'] == 'Cellular':
                    for key in uplink.keys():
                        uplinks_info['Cellular'][key] = uplink[key]

            #uplinks_info['WAN1']['status']
            #uplinks_info['WAN2']['status']


            if(uplinks_info['WAN1']['status'] == "Failed" and network_name not in disconnect_network_list):
                disconnect_network_list.append(network_name)

        '''section to remove marked unused network'''
        print ("reached 1")
        disconnect_network_list.remove("china vpn")
        disconnect_network_list.remove("Zappon_Mex")
        disconnect_network_list.remove("open_mexico")
        disconnect_network_list.remove("San_Luis_Mex_cgt")
        disconnect_network_list.remove("TEST Tulsa_OK")
        disconnect_network_list.remove("Stafford GB")
        disconnect_network_list.remove("Norwich Lotus Cars GB")
        disconnect_network_list.remove("Glenview test new cfg")
        #disconnect_network_list.remove("Tulsa_Navistar")

        print ("reached here \n\n\n")
        print (len(disconnect_network_list))
        #append the current timestamp into all the disconnect network in the dictionary and in the external csv
        today = datetime.date.today()
        fd = open("ApplianceNetworkDisconnection_" + str(today) + '.txt', 'a')
        for appliance in disconnect_network_list:
            print(appliance)
            now = datetime.datetime.now()
            cur_time = []
            cur_time.append(now.hour)
            cur_time.append(now.minute)
            device_dict[appliance].append(cur_time)
            print(device_dict[appliance])
            time_stamp = str(now.hour) + ":" + str(now.minute)
            fd.write(appliance + ":" + time_stamp)

        fd.close()
        print ("file closed")

def check_dict():
    for key,value in device_dict.items():
        flag = 1
        if(len(value) > 5): # is checkable
            for i in range(5):
                if(value[len(value) - 1 - i][0] * 60 + value[len(value) - 1 - i][1] - value[len(value) - 2 - i][0] * 60 - value[len(value) - 2 - i][1] > 7):
                    flag = 0
                    break
            if(flag == 1):
                disconnected_devices.append(key)



#not send alert every 20 mins
#maybe 3 times a day or so
# call zendesk api (xml information)
#query the information from zendesk to check redundent ticket
#set priority over sites
def send_alert():
    if(len(disconnected_devices) > 0):
        #send the email notification
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()

        fromaddr = "jiana0516@gmail.com"
        toaddr = "jia.na@optimas.com"

        for disconnected_device in disconnected_devices:
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "appliance went down"

            #refomat and include more information
            '''location, device, person at that location, physical location, name of device, timestamp, date (timezone)'''
            '''mute the alert'''
            body = disconnected_device + " has been disconnected for ~20 mins\n"
            #ip address
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(fromaddr, "nj990516")
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
        server.quit()

def main():
    #put all the device connection status over time

    #do work here
    update_timestamp()
    check_dict()
    send_alert()
    pass

l = task.LoopingCall(main)
l.start(timeout) # call every sixty seconds

reactor.run()
