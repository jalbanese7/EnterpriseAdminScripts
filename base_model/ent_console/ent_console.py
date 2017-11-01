#!/usr/bin/env python


from contextlib import contextmanager
import datetime
import getopt
import hashlib
import logging
from logging.handlers import SysLogHandler
import sys
import time
import subprocess

import bottle
from bottle import run, route, request, static_file, WaitressServer, Bottle, response, hook
import cherrypy
import simplejson as json

auth_users = [ {'id': '8907', 'username': 'jalbanese', 'fname': 'John', 'lname': 'Albanese', 'access': '111111'}, {'id': '4971', 'username': 'valbanese', 'fname': 'Vince', 'lname': 'Albanese', 'access': '111111'}, {'id': '3542', 'username': 'ralbanese', 'fname': 'Ryan', 'lname': 'Albanese', 'access': '111111'}, {'id': '1977', 'username': 'malbanese', 'fname': 'Mike', 'lname': 'Albanese', 'access': '111111'}, {'id': '9241', 'username': 'jkenas', 'fname': 'Jamie', 'lname': 'Kenas', 'access': '111111'}, {'id': '4827', 'username': 'sberizka', 'fname': 'Stefanie', 'lname': 'Berizka', 'access': '111111'} ]

from admin_utils import Email 

VERSION = '1.0.0'

# Status codes
STATUS_CONTINUE = '100'
STATUS_SWITCHING_PROTOCOLS = '101'
STATUS_PROCESSING = '102'
STATUS_OK = '200'
STATUS_CREATED = '201'
STATUS_ACCEPTED = '202'
STATUS_NON_AUTHORITATIVE_INFORMATION = '203'
STATUS_NO_CONTENT = '204'
STATUS_RESET_CONTENT = '205'
STATUS_PARTIAL_CONTENT = '206'
STATUS_MULTI_STATUS = '207'
STATUS_ALREADY_REPORTED = '208'
STATUS_IM_USED = '226'
STATUS_MULTIPLE_CHOICES = '300'
STATUS_MOVED_PERMANENTLY = '301'
STATUS_FOUND = '302'
STATUS_SEE_OTHER = '303'
STATUS_NOT_MODIFIED = '304'
STATUS_USE_PROXY = '305'
STATUS_SWITCH_PROXY = '306'
STATUS_TEMPORARY_REDIRECT = '307'
STATUS_PERMANENT_REDIRECT = '308'
STATUS_BAD_REQUEST = '400'
STATUS_UNAUTHORIZED = '401'
STATUS_PAYMENT_REQUIRED = '402'
STATUS_FORBIDDEN = '403'
STATUS_NOT_FOUND = '404'
STATUS_METHOD_NOT_ALLOWED = '405'
STATUS_NOT_ACCEPTABLE = '406'
STATUS_PROXY_AUTHENTICATION_REQUIRED = '407'
STATUS_REQUEST_TIMEOUT = '408'
STATUS_CONFLICT = '409'
STATUS_GONE = '410'
STATUS_LENGTH_REQUIRED = '411'
STATUS_PRECONDITION_FAILED = '412'
STATUS_REQUEST_ENTITY_TOO_LARGE = '413'
STATUS_REQUEST_URI_TOO_LONG = '414'
STATUS_UNSUPPORTED_MEDIA_TYPE = '415'
STATUS_REQUESTED_RANGE_NOT_SATISFIABLE = '416'
STATUS_EXPECTATION_FAILED = '417'
STATUS_I_AM_A_TEAPOT = '418'
STATUS_AUTHENTICATION_TIMEOUT = '419'
STATUS_ENHANCE_YOUR_CALM = '420'
STATUS_UNPROCESSABLE_ENTITY = '422'
STATUS_LOCKED = '423'
STATUS_FAILED_DEPENDENCY = '424'
STATUS_UPGRADE_REQUIRED = '426'
STATUS_PRECONDITION_REQUIRED = '428'
STATUS_TOO_MANY_REQUESTS = '429'
STATUS_REQUEST_HEADER_FIELDS_TOO_LARGE = '431'
STATUS_LOGIN_TIMEOUT = '440'
STATUS_NO_RESPONSE = '444'
STATUS_RETRY_WITH = '449'
STATUS_BLOCKED_BY_WINDOWS_PARENTAL_CONTROLS = '450'
STATUS_UNAVAILABLE_FOR_LEGAL_REASONS = '451'
STATUS_REQUEST_HEADER_TOO_LARGE = '494'
STATUS_CERT_ERROR = '495'
STATUS_NO_CERT = '496'
STATUS_HTTP_TO_HTTPS = '497'
STATUS_TOKEN_EXPIRED = '498'
STATUS_CLIENT_CLOSED_REQUEST = '499'
STATUS_INTERNAL_SERVER_ERROR = '500'
STATUS_NOT_IMPLEMENTED = '501'
STATUS_BAD_GATEWAY = '502'
STATUS_SERVICE_UNAVAILABLE = '503'
STATUS_GATEWAY_TIMEOUT = '504'
STATUS_HTTP_VERSION_NOT_SUPPORTED = '505'
STATUS_VARIANT_ALSO_NEGOTIATES = '506'
STATUS_INSUFFICIENT_STORAGE = '507'
STATUS_LOOP_DETECTED = '508'
STATUS_BANDWIDTH_LIMIT_EXCEEDED = '509'
STATUS_NOT_EXTENDED = '510'
STATUS_NETWORK_AUTHENTICATION_REQUIRED = '511'
STATUS_ORIGIN_ERROR = '520'
STATUS_WEB_SERVER_IS_DOWN = '521'
STATUS_CONNECTION_TIMED_OUT = '522'
STATUS_PROXY_DECLINED_REQUEST = '523'
STATUS_TIMEOUT_OCCURRED = '524'
STATUS_NETWORK_READ_TIMEOUT_ERROR = '598'
STATUS_NETWORK_CONNECT_TIMEOUT_ERROR = '599'

def is_system_free(filename):
    full_file_name="/shared_entdata/" + filename
    with open(full_file_name, 'r') as ind_file:
         data=ind_file.read()
    
    if data == "UNLOCKED\n":
      return True 
    else: 
      return False 

def is_entry_present(appname):
    full_file_name="/shared_entdata/" + 'ent_app_driver.conf'
    with open(full_file_name, 'r') as app_driver:
         for line in app_driver:
            if appname in line:
               return True
    return False

def add_splunk_entry(action, message):
    today = datetime.datetime.today()
    full_file_name="/shared_splunk/" + 'ent_admin_audit.log'
    with open(full_file_name, 'a') as splunk_file:
         line_buf='timestamp=' + time.strftime('%Y%m%d%H%M%S') + ' sourcetype=enterprise_framework environment=Admin Console ent_operation=Enterprise Management ent_action=' + action + ' ent_message=' + message + '\n'
         splunk_file.write(line_buf)

@hook('after_request')
def enable_cors():
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

# Core - Status methods
@route('/')
def heartbeat():
    resp = {}
    resp['status'] = STATUS_OK
    resp['method'] = 'heartbeat'
    resp['server'] = parm_servername
    resp['message'] = 'heartbeat sent'
    resp['exception'] = ''
    payload = {}
    payload['version'] = VERSION
    resp['payload'] = payload
    return json.dumps(resp)

@bottle.route('/promote_environment')
def promote_environment():
    if is_system_free("dev_ci_indicator") and is_system_free("promo_status"):
        fromSourceEnv = request.GET.get('from')
        toDestEnv = request.GET.get('to')
        cmdLineArg=toDestEnv + "_from_" + fromSourceEnv + "_master"
        cmdLine="/shared_scripts/ent_set_console_promocode " + cmdLineArg
        p = subprocess.Popen([cmdLine], shell=True)
        p.wait()

        resp = {}
        resp['status'] = STATUS_OK
        resp['method'] = 'promote_environment'
        resp['server'] = parm_servername
        resp['message'] = 'Control Panel ' + fromSourceEnv.upper() + ' to ' + toDestEnv.upper() + ' promotion request has been received'
        resp['exception'] = ''
        payload = {}
        payload['version'] = VERSION
        resp['payload'] = payload
        return json.dumps(resp)
    else:
        resp = {}
        resp['status'] = STATUS_CONFLICT
        resp['method'] = 'promote_environment'
        resp['server'] = parm_servername
        resp['message'] = ''
        resp['exception'] = 'A CI or PROMO process is in progress. Your request cannot be completed at this time.' 
        payload = {}
        payload['version'] = VERSION
        resp['payload'] = payload
        return json.dumps(resp)

@bottle.route('/sendemail')
def sendemail():
    to = request.GET.get('to')
    subject = request.GET.get('subject')
    message = request.GET.get('msg')
    email = Email(to=to, subject=subject)
    email.text('')
    htmlBody='<html><body>' + message + '</body></html>'
    email.html(htmlBody)
    email.send()

    resp = {}
    resp['status'] = STATUS_OK
    resp['method'] = 'sendemail'
    resp['server'] = parm_servername
    resp['message'] = 'Email message has been sent.'
    resp['exception'] = ''
    payload = {}
    payload['version'] = VERSION
    resp['payload'] = payload
    return json.dumps(resp)

@bottle.route('/auth')
def auth():
    id = request.GET.get('id')
    if any(data['id'] == id for data in auth_users):
        for user in auth_users:
           if user['id'] == id:
              username=user['username']
              fname=user['fname']
              lname=user['lname']
              access=user['access']
              break
           fi

        resp = {}
        resp['status'] = STATUS_OK
        resp['method'] = 'auth'
        resp['server'] = parm_servername 
        resp['message'] = 'Valid User'
        resp['exception'] = ''
        resp['version'] = VERSION
        payload = { 'username': username, 'fname': fname, 'lname': lname, 'access': access }
        resp['payload'] = payload
        return json.dumps(resp)
    else:
        resp = {}
        resp['status'] = STATUS_UNAUTHORIZED
        resp['method'] = 'auth'
        resp['server'] = parm_servername 
        resp['message'] = 'Invalid User'
        resp['exception'] = ''
        resp['version'] = VERSION
        payload = {}
        resp['payload'] = payload
        return json.dumps(resp)

@bottle.route('/get_apps')
def get_apps():
        with open('/shared_entdata/guardian_appstats/appmanagement.json') as json_data:
             data = json.load(json_data)

        resp = {}
        resp['status'] = STATUS_OK
        resp['method'] = 'get_apps'
        resp['server'] = parm_servername
        resp['message'] = 'App List'
        resp['exception'] = ''
        resp['version'] = VERSION
        payload = data
        resp['payload'] = payload
        return json.dumps(resp)

@bottle.route('/get_activity')
def get_activity():
        dev_primary_listeners = []
        dev_failover_listeners = []
        uat_primary_listeners = []
        uat_failover_listeners = []
        prod_primary_listeners = []
        prod_failover_listeners = []

        dev_primary_websites = []
        dev_failover_websites = []
        uat_primary_websites = []
        uat_failover_websites = []
        prod_primary_websites = []
        prod_failover_websites = []

        dev_primary_batch = []
        dev_failover_batch = []
        uat_primary_batch = []
        uat_failover_batch = []
        prod_primary_batch = []
        prod_failover_batch = []

        dev_primary_gateway = []
        dev_failover_gateway = []
        uat_primary_gateway = []
        uat_failover_gateway = []
        prod_primary_gateway = []
        prod_failover_gateway = []

        lis_keys = [ 'appname', 'status', 'occurrence', 'port' ]
        lis_files = [ '/shared_entdata/guardian_activity/dev_primary_listeners', '/shared_entdata/guardian_activity/dev_failover_listeners', '/shared_entdata/guardian_activity/uat_primary_listeners', '/shared_entdata/guardian_activity/uat_failover_listeners', '/shared_entdata/guardian_activity/prod_primary_listeners', '/shared_entdata/guardian_activity/prod_failover_listeners' ]

        web_keys = [ 'appname', 'status' ]
        web_files = [ '/shared_entdata/guardian_activity/dev_primary_web', '/shared_entdata/guardian_activity/dev_failover_web', '/shared_entdata/guardian_activity/uat_primary_web', '/shared_entdata/guardian_activity/uat_failover_web', '/shared_entdata/guardian_activity/prod_primary_web', '/shared_entdata/guardian_activity/prod_failover_web' ]

        batch_keys = [ 'appname', 'status' ]
        batch_files = [ '/shared_entdata/guardian_activity/dev_primary_batch', '/shared_entdata/guardian_activity/dev_failover_batch', '/shared_entdata/guardian_activity/uat_primary_batch', '/shared_entdata/guardian_activity/uat_failover_batch', '/shared_entdata/guardian_activity/prod_primary_batch', '/shared_entdata/guardian_activity/prod_failover_batch' ]

        gateway_keys = [ 'appname', 'status' ]
        gateway_files = [ '/shared_entdata/guardian_activity/dev_primary_gateway', '/shared_entdata/guardian_activity/dev_failover_gateway', '/shared_entdata/guardian_activity/uat_primary_gateway', '/shared_entdata/guardian_activity/uat_failover_gateway', '/shared_entdata/guardian_activity/prod_primary_gateway', '/shared_entdata/guardian_activity/prod_failover_gateway' ]

        for lis_file in lis_files:
            with open(lis_file) as f:
                for l in f:
                    values=l.strip().split("^")
                    new_dict = dict(zip(lis_keys, values))
                    if lis_file == '/shared_entdata/guardian_activity/dev_primary_listeners':
                        dev_primary_listeners.append(new_dict)
                    if lis_file == '/shared_entdata/guardian_activity/dev_failover_listeners':
                        dev_failover_listeners.append(new_dict)
                    if lis_file == '/shared_entdata/guardian_activity/uat_primary_listeners':
                        uat_primary_listeners.append(new_dict)
                    if lis_file == '/shared_entdata/guardian_activity/uat_failover_listeners':
                        uat_failover_listeners.append(new_dict)
                    if lis_file == '/shared_entdata/guardian_activity/prod_primary_listeners':
                        prod_primary_listeners.append(new_dict)
                    if lis_file == '/shared_entdata/guardian_activity/prod_failover_listeners':
                        prod_failover_listeners.append(new_dict)

        for web_file in web_files:
            with open(web_file) as f:
                for l in f:
                    values=l.strip().split("^")
                    new_dict = dict(zip(web_keys, values))
                    if web_file == '/shared_entdata/guardian_activity/dev_primary_web':
                        dev_primary_websites.append(new_dict)
                    if web_file == '/shared_entdata/guardian_activity/dev_failover_web':
                        dev_failover_websites.append(new_dict)
                    if web_file == '/shared_entdata/guardian_activity/uat_primary_web':
                        uat_primary_websites.append(new_dict)
                    if web_file == '/shared_entdata/guardian_activity/uat_failover_web':
                        uat_failover_websites.append(new_dict)
                    if web_file == '/shared_entdata/guardian_activity/prod_primary_web':
                        prod_primary_websites.append(new_dict)
                    if web_file == '/shared_entdata/guardian_activity/prod_failover_web':
                        prod_failover_websites.append(new_dict)

        for batch_file in batch_files:
            with open(batch_file) as f:
                for l in f:
                    values=l.strip().split("^")
                    new_dict = dict(zip(batch_keys, values))
                    if batch_file == '/shared_entdata/guardian_activity/dev_primary_batch':
                        dev_primary_batch.append(new_dict)
                    if batch_file == '/shared_entdata/guardian_activity/dev_failover_batch':
                        dev_failover_batch.append(new_dict)
                    if batch_file == '/shared_entdata/guardian_activity/uat_primary_batch':
                        uat_primary_batch.append(new_dict)
                    if batch_file == '/shared_entdata/guardian_activity/uat_failover_batch':
                        uat_failover_batch.append(new_dict)
                    if batch_file == '/shared_entdata/guardian_activity/prod_primary_batch':
                        prod_primary_batch.append(new_dict)
                    if batch_file == '/shared_entdata/guardian_activity/prod_failover_batch':
                        prod_failover_batch.append(new_dict)

        for gateway_file in gateway_files:
            with open(gateway_file) as f:
                for l in f:
                    values=l.strip().split("^")
                    new_dict = dict(zip(gateway_keys, values))
                    if gateway_file == '/shared_entdata/guardian_activity/dev_primary_gateway':
                        dev_primary_gateway.append(new_dict)
                    if gateway_file == '/shared_entdata/guardian_activity/dev_failover_gateway':
                        dev_failover_gateway.append(new_dict)
                    if gateway_file == '/shared_entdata/guardian_activity/uat_primary_gateway':
                        uat_primary_gateway.append(new_dict)
                    if gateway_file == '/shared_entdata/guardian_activity/uat_failover_gateway':
                        uat_failover_gateway.append(new_dict)
                    if gateway_file == '/shared_entdata/guardian_activity/prod_primary_gateway':
                        prod_primary_gateway.append(new_dict)
                    if gateway_file == '/shared_entdata/guardian_activity/prod_failover_gateway':
                        prod_failover_gateway.append(new_dict)



        resp = {}
        resp['status'] = STATUS_OK
        resp['method'] = 'get_activity'
        resp['server'] = parm_servername
        resp['message'] = 'Activity Status List'
        resp['exception'] = ''
        resp['version'] = VERSION
        payload = {}
        payload['dev_primary_listeners']=dev_primary_listeners
        payload['dev_failover_listeners']=dev_failover_listeners
        payload['uat_primary_listeners']=uat_primary_listeners
        payload['uat_failover_listeners']=uat_failover_listeners
        payload['prod_primary_listeners']=prod_primary_listeners
        payload['prod_failover_listeners']=prod_failover_listeners
        payload['dev_primary_websites']=dev_primary_websites
        payload['dev_failover_websites']=dev_failover_websites
        payload['uat_primary_websites']=uat_primary_websites
        payload['uat_failover_websites']=uat_failover_websites
        payload['prod_primary_websites']=prod_primary_websites
        payload['prod_failover_websites']=prod_failover_websites
        payload['dev_primary_batch']=dev_primary_batch
        payload['dev_failover_batch']=dev_failover_batch
        payload['uat_primary_batch']=uat_primary_batch
        payload['uat_failover_batch']=uat_failover_batch
        payload['prod_primary_batch']=prod_primary_batch
        payload['prod_failover_batch']=prod_failover_batch
        payload['dev_primary_gateway']=dev_primary_gateway
        payload['dev_failover_gateway']=dev_failover_gateway
        payload['uat_primary_gateway']=uat_primary_gateway
        payload['uat_failover_gateway']=uat_failover_gateway
        payload['prod_primary_gateway']=prod_primary_gateway
        payload['prod_failover_gateway']=prod_failover_gateway
        resp['payload'] =  payload
        return json.dumps(resp)


@bottle.route('/manage_apps')
def manage_apps():
     if is_system_free("dev_ci_indicator") and is_system_free("promo_status") and is_system_free("console_action_indicator"):
        action = request.GET.get('action')
        appName = request.GET.get('appname')
        requesterId = request.GET.get('reqid')

        if action == "addListener" or action == "addWebsite":
            if is_entry_present(appName):
                err_msg='App name ' + appName + ' already exists. Request denied.' 
                add_splunk_entry(action, err_msg) 
                resp = {}
                resp['status'] = STATUS_CONFLICT
                resp['method'] = 'manage_apps'
                resp['server'] = parm_servername
                resp['message'] = ''
                resp['exception'] = err_msg
                payload = {}
                payload['version'] = VERSION
                resp['payload'] = payload
                return json.dumps(resp)

        if action == "deleteApp":
            if not is_entry_present(appName):
                err_msg='App name ' + appName + ' does not exist. Request denied.' 
                add_splunk_entry(action, err_msg) 
                resp = {}
                resp['status'] = STATUS_CONFLICT
                resp['method'] = 'manage_apps'
                resp['server'] = parm_servername
                resp['message'] = ''          
                resp['exception'] = err_msg 
                payload = {}
                payload['version'] = VERSION
                resp['payload'] = payload
                return json.dumps(resp)

        # Successful processing path
        cmdLineArg=action + "_" + appName + "_" + requesterId
        cmdLine="/shared_scripts/ent_set_console_action " + cmdLineArg
        p = subprocess.Popen([cmdLine], shell=True)
        p.wait()

        resp = {}
        resp['status'] = STATUS_OK
        resp['method'] = 'manage_apps'
        resp['server'] = parm_servername
        resp['message'] = 'App Action Request ' + cmdLineArg + ' has been received'
        resp['exception'] = ''
        payload = {}
        payload['version'] = VERSION
        resp['payload'] = payload
        return json.dumps(resp)
     else:
        resp = {}
        resp['status'] = STATUS_CONFLICT
        resp['method'] = 'manage_apps'
        resp['server'] = parm_servername
        resp['message'] = ''
        resp['exception'] = 'Another Administrative operation is in progress. Your request cannot be completed at this time.' 
        payload = {}
        payload['version'] = VERSION
        resp['payload'] = payload
        return json.dumps(resp)

@bottle.route('/change_instances')
def manage_apps():
     if is_system_free("dev_ci_indicator") and is_system_free("promo_status") and is_system_free("console_action_indicator"):
        instances = request.GET.get('instances')
        action = request.GET.get('action')
        appName = request.GET.get('appname')
        requesterId = request.GET.get('reqid')

        # Successful processing path
        cmdLineArg=action + "_" + appName + "_" + requesterId + "_" + instances
        cmdLine="/shared_scripts/ent_set_console_action " + cmdLineArg
        p = subprocess.Popen([cmdLine], shell=True)
        p.wait()

        resp = {}
        resp['status'] = STATUS_OK
        resp['method'] = 'change_instances'
        resp['server'] = parm_servername
        resp['message'] = 'App Action Request ' + cmdLineArg + ' has been received'
        resp['exception'] = ''
        payload = {}
        payload['version'] = VERSION
        resp['payload'] = payload
        return json.dumps(resp)
     else:
        resp = {}
        resp['status'] = STATUS_CONFLICT
        resp['method'] = 'manage_apps'
        resp['server'] = parm_servername
        resp['message'] = ''
        resp['exception'] = 'Another Administrative operation is in progress. Your request cannot be completed at this time.'
        payload = {}
        payload['version'] = VERSION
        resp['payload'] = payload
        return json.dumps(resp)



if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['ip=', 'port=', 'servername=', 'help'])
    except:
        print('Error obtaining runtime parameters.  Aborting.')
        sys.exit(1)

    for o, a in opts:
        if o == '--ip':
            parm_listeningip = a
        elif o == '--port':
            parm_listeningport = a
        elif o == '--servername':
            parm_servername = a
        elif o == '--help':
            print ('usage-->ip=123, port=1234, servername=test')
            sys.exit(0)


    bottle.run(server='cherrypy', host=parm_listeningip, port=parm_listeningport, reloader=False)
