#!/usr/bin/python3
"""
MeerKAT Extension (MKE)
(r)emote (i)nterface (m)anagement (lib)rary
interface library for accessing remote experiment and analysis data in a dbserver
"""

import copy
import requests
import inspect

import datetime
import time

import os
import json

import logging
import sys

_log = logging.getLogger()
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
_log.addHandler(streamHandler)

from mke_client.helpers import get_utcnow, make_zulustr, parse_zulutime
import mke_client.filesys_storage_api as filesys


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    
def print_red(msg):
    print(f"{bcolors.FAIL}{msg}{bcolors.ENDC}")

def print_color(msg, color=bcolors.ENDC):
    print(f"{color}{msg}{bcolors.ENDC}")



allowed_status_codes = {

    'INITIALIZING': 0,
    'AWAITING_CHECK': 1,
    'WAITING_TO_RUN': 2,
    'HOLD': 3,
    
    'STARTING': 10,
    'RUNNING': 11,
    'CANCELLING': 12,
    'FINISHING': 13,

    'FINISHED': 100,
    'ABORTED': 101,

    'CANCELLED': 1001,
    'FAILED': 1000,
    'FAULTY': 1002,
}


def print_sys_info():
    try:
        import platform
        from psutil import virtual_memory
        import getpass
        import datetime
        import time

        username = getpass.getuser()
        now = datetime.datetime.now()
        mem = virtual_memory()
        uname = platform.uname()

        print("="*40, "System Information", "="*40)
        print("")
        print(f"User:      {username}")
        print(f"System:    {uname.system}")
        print(f"Node Name: {uname.node}")
        print(f"Release:   {uname.release}")
        print(f"Version:   {uname.version}")
        print(f"Machine:   {uname.machine}")
        print(f"Processor: {uname.processor}")
        print("RAM:       {:.1f} GB".format(mem.total / (1024 * 1024 * 1024)))
        print ("\n")
        print("Current date and time : " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("                  ISO : " + datetime.datetime.now().astimezone().replace(microsecond=0).isoformat())
        print('')
        print("="*40, "System Information", "="*40)
    except Exception:
        print_red('Error while trying to print system info')


def __run_fun(fun, dc, *args, **kwargs):
    if not fun is None and hasattr(fun, '__call__'):
        dc = fun(dc, *args, **kwargs)
        assert isinstance(dc, dict), 'return type dict was expeted from function, but atual return type was: ' + str(type(dc))
    return dc

def wait_for_start_condition(start_condition, wait_increment_max=10, verb=True):
    dt_start = parse_zulutime(start_condition)
    

    t_rem = (dt_start - get_utcnow() ).total_seconds()
    if t_rem <= 0:
        return

    t_rem = max(1, t_rem + 1)
    
    if verb:
        print('Waiting for start condition: "{}" (~{}s)'.format(start_condition, int(t_rem)))

    while t_rem > 0:
        t_wait = min(wait_increment_max, t_rem) 
        time.sleep(t_wait)
        t_rem -= t_wait






class BaseRimObj():
    """base object to have the Analysis and Experiment 
    classes inherit from
    """
    def __init__(self, uri, tablename, id):
        self.uri = uri
        self.__tablename = tablename
        self.id = id

    @property
    def tablename(self):
        """this objects associated table name"""
        return self.__tablename

    def get(self, tablename=None, id=None, **kwargs):
        if id is None:
            id = self.id
        if tablename is None:
            tablename = self.tablename
        r = requests.get(f'{self.uri}/{tablename}/{id}', **kwargs)
        assert r.status_code  == 200, r.text
        return r.json()

    def patch_me(self, **kwargs):
        r = requests.patch(f'{self.uri}/{self.tablename}/{self.id}', **kwargs)
        assert r.status_code < 300, r.text
        return r.json()

    def post(self, route, **kwargs):
        r = requests.post(f'{self.uri}/{route}', **kwargs)
        assert r.status_code < 300, r.text
        return r.json()

    def get_me(self) -> dict:
        """returns the database entry row associated with this objects id as dictionary"""
        return self.get()

    def get_my_antenna(self) -> dict:
        """returns the antenna entry row associated with this objects antenna_id as dictionary"""
        me = self.get() 
        return self.get('antennas', me['antenna_id'])

    def get_my_antenna_url(self) -> dict:
        """returns the antenna entry row associated with this objects antenna_id as dictionary"""
        antenna = self.get_my_antenna()
        antenna_url = str(antenna['address'])

        if not ':' in antenna_url:
            antenna_url = antenna_url + ':8080'
        if not antenna_url.startswith('http'):
            antenna_url = 'http://' + antenna_url
        return antenna_url

    def get_my_antenna_ip(self) -> dict:
        """returns the antenna entry row associated with this objects antenna_id as dictionary"""
        antenna = self.get_my_antenna()
        antenna_ip = str(antenna['address'])
        return antenna_ip


    def set_status(self, new_status:str, ignore_enum=False) -> dict:
        """set a new status to my object in the DB and return the updated 
        remote object as dictionary.

        Example::
            The status must be one of::

                INITIALIZING, AWAITING_CHECK, WAITING_TO_RUN, HOLD, STARTING, 
                RUNNING, CANCELLING, FINISHING, FINISHED, ABORTED, CANCELLED, 
                FAILED, FAULTY

            but ideally you should only set RUNNING, or FINISHING. See::
            
                .set_status_finishing()
                .set_status_running()

        Args:
            new_status (str): the new status to set. See above
            ignore_enum (bool, optional): set True to not check if the new status is allowed. Defaults to False.

        Returns:
            dict: the database entry row associated with this objects id as dictionary
        """
        assert new_status in allowed_status_codes or ignore_enum, "the given status was not within the allowed status strings: allowed are: " + ', '.join(allowed_status_codes.keys())
        return self.patch_me(json=dict(status=new_status))


    def set_status_cancelling(self) -> dict:
        """set CANCELLING as new status to my object in the DB and return the updated 
        remote object as dictionary.

        Returns:
            dict: the database entry row associated with this objects id as dictionary
        """
        return self.set_status('CANCELLING')


    def set_status_finishing(self) -> dict:
        """set FINISHING as new status to my object in the DB and return the updated 
        remote object as dictionary.

        Returns:
            dict: the database entry row associated with this objects id as dictionary
        """
        return self.set_status('FINISHING')

    def set_status_running(self) -> dict:
        """set RUNNING as new status to my object in the DB and return the updated 
        remote object as dictionary.

        Returns:
            dict: the database entry row associated with this objects id as dictionary
        """
        return self.set_status('RUNNING')

    def check_for_cancel(self) -> bool:
        """gets the remote table row associated with me and returns whether or not a cancel was requested
        
        Returns:
            bool: true if cancel was requested, false if not
        """
        me = self.get()
        assert me['status'] in allowed_status_codes, 'ERROR! The remote status ' + me['status'] + ' is unrecognized'
        return allowed_status_codes[me['status']] >= 100 or me['status'] == 'CANCELLING'

    
    def get_remaining_time(self, t_is: datetime.datetime = None) -> float:
        """gets my remote object and checks how much time it 
        is allowed to be running by returning
            (start_condition + duration_expected) < utcnow

        Returns:
            float: the remaining time in hours for this script to run
        """
        me = self.get()
        tstart = parse_zulutime(me['start_condition'])
        assert tstart is not None, '"start_condition" could not be parsed. Got: {} {}'.format(type(me['start_condition']), me['start_condition'])
        if t_is is None:
            t_is = get_utcnow()

        t_end_req = tstart + datetime.timedelta(hours=float(me['duration_expected_hr_dec']))
        t_rem = (t_end_req - t_is).total_seconds() / 60.0 / 60.0
        return max(0, t_rem)


    def wait_for_start_condition(self, wait_increment_max=10, verb=True):
        dc = self.get()
        wait_for_start_condition(dc['start_condition'], wait_increment_max,  verb)


#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################


    def run_experiment(self, f_init=None, f_start=None, f_get_time = None, f_tick=None, f_finish=None, f_post=None, is_dryrun=True, n_ticks_max=float("inf"), ignore_time=True, verbose=True, ticklen=1, skip_faulty_ticks=True):
        
        if not verbose:
            def print(*args, **kwargs):
                pass        

        if not f_init is None and hasattr(f_init, '__call__'):
            print(make_zulustr(get_utcnow()) + ' | Initializing...')
            dc = __run_fun(f_init, dc)

        t_start = get_utcnow()
        print(make_zulustr(get_utcnow()) + ' | Starting...')

        if inspect.isgeneratorfunction(f_tick):
            ticker = f_tick(dc)   
        else:
            ticker = None

        has_started = False
        tickcount = 0
        try:
            self.set_status_running()
            
            
            while tickcount < n_ticks_max: 
                try:
                    tickcount += 1
                    
                    # ---------------------------------------
                    # wait for my start condition
                    # ---------------------------------------
                    if hasattr(self, 'wait_for_start_condition'):
                        self.wait_for_start_condition()
                    
                    # ---------------------------------------
                    # check if I should stop
                    # ---------------------------------------

                    if not is_dryrun and not ignore_time and self.get_remaining_time(f_get_time()) <= ticklen*1.1:
                        print(make_zulustr(get_utcnow()) + ' | Time is up... finshing')
                        my_row_as_dict = self.set_status_finishing()
                        break

                    if not is_dryrun and self.check_for_cancel():
                        print(make_zulustr(get_utcnow()) + ' | Cancle initiated from externally... cancelling')
                        my_row_as_dict = self.set_status_cancelling()
                        break

                    if not has_started:
                        print(make_zulustr(get_utcnow()) + ' | Starting Telescope...')
                        dc = __run_fun(f_start, dc)
                        has_started = True

                    # ---------------------------------------
                    # perform the test
                    # ---------------------------------------

                    if f_tick is None:
                        pass
                    elif ticker is not None:
                        try:
                            print(make_zulustr(get_utcnow()) + ' | Calling next(tick)...')
                            dci = next(ticker)
                            assert isinstance(dci, dict), 'expected dict return type for tick iterator'
                            if dci != dc:
                                dc = {**dc, **dci}
                        except StopIteration:
                            print(make_zulustr(get_utcnow()) + ' | Last Iteration Reached... stopping loop')
                            break
                    elif hasattr(f_tick, '__call__'):
                        print(make_zulustr(get_utcnow()) + ' | Calling tick()...')
                        dc = __run_fun(f_tick, dc)
                    else:
                        raise Exception('f_tick is neither None, nor an iterator, nor a function handle. But one of the three was expected')


                    print(make_zulustr(get_utcnow()) + f' | completed tick {tickcount} ...')
                except Exception as err:
                    if skip_faulty_ticks:
                        print_red('ERROR: ' + str(err))
                    else:
                        raise


            dc = __run_fun(f_post, dc)

            t_end = get_utcnow()
            t_elapsed = t_start - t_end
            my_row_as_dict = self.set_status('AWAITING_POST_PROC')

            print(make_zulustr(get_utcnow()) + f' | Finished main loop (t_elapsed={t_elapsed})') 
            
            
        except Exception as err:
            print_red('ERROR: ' + str(err))
            raise
        finally:
            # ---------------------------------------+
            # shutdown the antenna
            # ---------------------------------------
            dc = __run_fun(f_finish, dc)
            

        return my_row_as_dict, t_elapsed, dc

        




class Experiment(BaseRimObj):
    """An interface object to get access to experiments in the 
    database.

    Args:
        RimObj: _description_
    """
    __tablename = 'experiments'

    @staticmethod
    def make_new(uri=None, script_in_path=None, script_out_path=None, params={}, status="RUNNING", parameters_script_json=None, id=None, antenna_id=None, start_condition=None, 
            duration_expected_hr_dec=0.0, devices_json="[]", script_name=None, needs_manual_upload=0,
            comments='', script_version=None, forecasted_oc=None, time_initiated_iso=None, **kwargs):

        if uri is None:
            uri = os.environ.get('DBSERVER_URI')

        assert id is None or isinstance(id, int), "id must be of type int!"
        # assert os.path.exists(script_in_path), "input path does not exist"
        assert script_in_path is None or script_in_path.endswith('.ipynb'), "input path must be jupyter notebook file ending with .ipynb" + str(script_in_path)
        assert script_out_path is None or script_out_path.endswith('.ipynb') or script_out_path.endswith('.html'), "output path must be jupyter notebook file ending with .ipynb" + str(script_out_path)
        assert (params is None and parameters_script_json is not None) or (params is not None and parameters_script_json is None), "either params or parameters_script_json"
        

        if not parameters_script_json:
            parameters_script_json = json.dumps(params)

        defaults = {
            'antenna_id': 'NA_ant',
            'comments': None,
            'time_initiated_iso': make_zulustr(get_utcnow()), 
            'errors': None, 
            'results_json': '{}',
            'start_condition': make_zulustr(get_utcnow()),
            'time_started_iso': None, 
            'papermill_json': None, 
            'devices_json': '[]', 
            'duration_expected_hr_dec': 0.1, 
            'id':id,
            'script_out_path':None,
            'script_params_json':'{}',
            'caldav_uid':None,
            'script_name':None,
            'script_version':None,
            'needs_manual_upload':None,
            'status':'RUNNING',
            'forecasted_oc':None,
            'aux_files_json': '{}'
            }


        obj = { "id": id,
                "script_name": script_name,
                "script_version": script_version,
                "script_in_path": script_in_path,
                "script_out_path": script_out_path,

                "status": status,
                "antenna_id": antenna_id,
                "script_params_json":  parameters_script_json,
                
                "start_condition": start_condition,
                "time_initiated_iso": time_initiated_iso,
                "duration_expected_hr_dec": duration_expected_hr_dec,

                "devices_json": devices_json,
                "needs_manual_upload": needs_manual_upload,
                "comments": comments,
                "forecasted_oc": forecasted_oc
            }     

        for k, v in kwargs.items():
            if k in defaults:
                obj[k] = v
            
        
        exp_row = {**defaults, **obj}

        r = requests.post(f'{uri}/{Experiment.__tablename}', json=exp_row)
        assert r.status_code < 300, r.text
        dc = r.json()

        return Experiment(dc['id'], uri=uri), dc


    def __init__(self, id, uri = None):
        """create a new Experiment object with an id to get access 
        to this expiriment objects row in the database

        Args:
            id (int): the id of the analyses in the DB
            uri (string, optional): the URI to connect to. 
                If not given will be tried to be resolved 
                from environmental valiables.
                    Defaults to None.
        """
        if uri is None:
            uri = os.environ.get('DBSERVER_URI')
        assert uri, 'need to give a valid URI for a DB connection!'

        super().__init__(uri, self.__tablename, id)

    def ping_test(self):
        """will ping the DB server and return if successful
        """
        try:
            r = requests.get(f'{self.uri}/ping', timeout=2)
            return r.status_code <= 200
        except Exception as err:
            _log.error('Error while pinging: ' + str(err))
            return False

        
    def get_expected_devices(self):
        """returns a list of strings with the devices which are expected with this measurement"""
        dc = self.get()
        return json.loads(dc['devices_json'])


    def upload_new_datafile(self, data_file, aux_files = {}, start_time=None, tag=None):
        """upload a set of files for a measurement consisting of a main measurement file and a dictionary
        of auxiliary data files connected with the main file. 
        Example::
            Expects the aux_files to be a dictionary with the keys to associate the 
            auxiliary files with when uploading. E.G::

                experiment_id = 1
                obj = Experiment(experiment_id, 'http://localhost:8080')
                aux_files = {
                    'RFC': '/path/to/my/rfcfile.csv',
                    'MWS': '/path/to/my/mwsfile.zip'
                }
                aux_pathes = obj.upload_new_datafile(devices_to_add)
                (key_rfc, id_rfc, savepath_rfc) = aux_pathes[0]
                (key_mws, id_mws, savepath_mws) = aux_pathes[1]


        Args:
            data_file (str or file object): the file object or path to the main file to upload to the server
            aux_files (dict, optional): a dictionary with key:path_to_file pairs for auxiliary files to upload. Defaults to {}.
            start_time (str or datetimedatetime, optional): None for now, else give an iso string with UTC! time to register this files with. Defaults to None.
            tag (str, optional): any tag you want to associate with these files (will end up in filename so, choose wisely). Defaults to None.

        Returns:
            path (str): path, where the file was saved on the server
            id (int): id this file has been given
            aux_files (list): auxiliary files as list of tuples with (key, id, path)
        """
        if isinstance(start_time, datetime.datetime):
            start_time = make_zulustr(start_time)
        if not start_time:
            start_time = make_zulustr(get_utcnow())


        fpd = data_file if not hasattr(data_file, 'read') else open(data_file, 'rb')
        files = {'ACU': fpd}
        for k, v in aux_files.items():
            files[k] = v if hasattr(v, 'read') else open(v, 'rb')

        payload = {
            'id': self.id, 
            'row':{
                'time_iso': start_time,
                'tags': tag
                }
            }

        dc = self.post('upload_measurement_data', json=payload, files=files)
        return dc['path'], dc['id'], dc['aux_files'] 

    def get_path_for_new_datafile(self, devices_to_add = {'ACU': '.csv'}, start_time=None, tag=None):
        """register a set of files and return the save pathes for a measurement consisting of a main measurement file and a dictionary
        of auxiliary data files connected with the main file. 

        Example::
            Expects the aux_files to be a dictionary with the keys to associate the 
            auxiliary files with when uploading. E.G::

                experiment_id = 1
                obj = Experiment(experiment_id, 'http://localhost:8080')
                devices_to_add = {'RFC': '.csv', 'MWS': '.zip'}
                main_path, main_id, aux_pathes = obj.get_path_for_new_datafile(devices_to_add)

                with open(main_path, 'w') as fp:
                   fp.write(main_data)

                (key_rfc, id_rfc, savepath_rfc) = aux_pathes[0]
                with open(savepath_ocs, 'w') as fp:
                   fp.write(rfc_data)

                (key_mws, id_mws, savepath_mws) = aux_pathes[1]
                with open(savepath_mws, 'wb') as fp:
                   fp.write(mws_data)
                   


        Args:
            data_file (str or file object): the file object or path to the main file to upload to the server
            devices_to_add (dict, optional): a dictionary with key:extension pairs for auxiliary files you would like to add. Defaults to {}.
            start_time (str or datetimedatetime, optional): None for now, else give an iso string with UTC! time to register this files with. Defaults to None.
            tag (str, optional): any tag you want to associate with these files (will end up in filename so, choose wisely). Defaults to None.

        Returns:
            path (str): path, where the file was saved on the server
            id (int): id this file has been given
            aux_files (list): auxiliary files as list of tuples with (key, id, path)
        """

        if isinstance(start_time, datetime.datetime):
            start_time = make_zulustr(start_time)
        if not start_time:
            start_time = make_zulustr(get_utcnow())

        if isinstance(devices_to_add, str):
            extensions = {devices_to_add: '.csv'}
        elif isinstance(devices_to_add, list) and len(devices_to_add) > 0 and isinstance(devices_to_add[0], str):
            extensions = {{k: '.csv'} for k in devices_to_add}
        elif isinstance(devices_to_add, list) and len(devices_to_add) > 0 and len(devices_to_add[0]) == 2:
            extensions = dict(devices_to_add)
        else:
            extensions = {k:v for k, v in devices_to_add.items()}

        if 'ACU' not in extensions:
            extensions['ACU'] ='.csv'

        payload = {
            'id': self.id, 
            'extensions': extensions, 
            'row':{
                'time_iso': start_time,
                'tags': tag
                }
            }

        dc = self.post('register_measurement_data', json=payload)
        return dc['path'], dc['id'], dc['aux_files'] 


    def get_pathes_for_new_global_auxfiles(self, devices_to_add = {}):
        """register a set of experiment level auxiliary files and return the pathes 
        to save these under.

        Example::
            Expects the devices_to_add to be a dictionary with the keys to associate the 
            auxiliary files with when uploading::
                experiment_id = 1
                obj = Experiment(experiment_id, 'http://localhost:8080')
                devices_to_add = {'OCS': '.csv', 'MWS': '.zip'}
                aux_pathes = obj.get_pathes_for_new_global_auxfiles(devices_to_add)

                (key_ocs, id_ocs, savepath_ocs) = aux_pathes[0]
                with open(savepath_ocs, 'w') as fp:
                   fp.write(ocs_data)

                (key_mws, id_mws, savepath_mws) = aux_pathes[1]
                with open(savepath_mws, 'wb') as fp:
                   fp.write(mws_data)

        Args:
            devices_to_add (dict, optional): a dictionary with key:extension pairs for auxiliary files you would like to add. Defaults to {}.

        Returns:
            aux_files (list): auxiliary files as list of tuples with (key, id, path)
        """

        if isinstance(devices_to_add, str):
            extensions = {devices_to_add: '.csv'}
        elif isinstance(devices_to_add, list) and len(devices_to_add) > 0 and isinstance(devices_to_add[0], str):
            extensions = {{k: '.csv'} for k in devices_to_add}
        elif isinstance(devices_to_add, list) and len(devices_to_add) > 0 and len(devices_to_add[0]) == 2:
            extensions = dict(devices_to_add)
        else:
            extensions = devices_to_add

        payload = {
            'id': self.id, 
            'extensions': extensions
            }

        dc = self.post('register_exp_aux_files', json=payload)
        return dc['aux_files'] 


    def upload_new_global_auxfiles(self, devices_to_add = {}):
        """upload a set of experiment level auxiliary files and return the pathes 
        where they were saved on the server.

        Example::
            Expects the devices_to_add to be a dictionary with the keys 
            and file pathes or file like objects::

                experiment_id = 1
                obj = Experiment(experiment_id, 'http://localhost:8080')
                devices_to_add = {
                    'OCS': '/path/to/my/ocsfile.csv',
                    'MWS': '/path/to/my/mwsfile.zip'
                }
                aux_pathes = obj.upload_new_global_auxfiles(devices_to_add)
                (key_ocs, id_ocs, savepath_ocs) = aux_pathes[0]
                (key_mws, id_mws, savepath_mws) = aux_pathes[1]

        Args:
            devices_to_add (dict, optional): a dictionary with key:extension pairs for auxiliary files you would like to add. Defaults to {}.

        Returns:
            aux_files (list): auxiliary files as list of tuples with (key, id, path)
        """

        files = [v if hasattr(v, 'read') else open(v, 'rb') for k, v in devices_to_add.items()]
        
        payload = {
            'id': self.exp.id, 
            }

        dc = self.post('upload_exp_aux_files', json=payload, files=files)
        return dc['aux_files'] 


class Analysis(BaseRimObj):
    """An interface object to get access to analyses in the 
    database."""
    __tablename = 'analyses'
    def __init__(self, id, uri = None):
        """create a new Analysis object with an id to get access 
        to this analyses objects row in the database

        Args:
            id (int): the id of the analyses in the DB
            uri (string, optional): the URI to connect to. 
                If not given will be tried to be resolved 
                from environmental valiables.
                    Defaults to None.
        """
        if uri is None:
            uri = os.environ.get('DBSERVER_URI')
        assert uri, 'need to give a valid URI for a DB connection!'
        super().__init__(uri, self.__tablename, id)




def run_experiment_detached(f_init=None, f_start=None, f_get_time = None, f_tick=None, f_finish=None, f_post=None, is_dryrun=True, n_ticks_max=float("inf"), ignore_time=True, verbose=True, skip_faulty_ticks=True, start_condition=None, end_time=None, dc={}):
    
    if not verbose:
        def printf(*args, **kwargs):
            pass  
    else:
        printf = print

    print(make_zulustr(get_utcnow()) + ' | Runninng Experiment detached from any DB...')

    if not f_init is None and hasattr(f_init, '__call__'):
        print(make_zulustr(get_utcnow()) + ' | Initializing...')
        dc = __run_fun(f_init, dc)

    t_start = get_utcnow()
    printf(make_zulustr(get_utcnow()) + ' | Starting...')

    if inspect.isgeneratorfunction(f_tick):
        ticker = f_tick(dc)   
    else:
        ticker = None

    has_started = False
    tickcount = 0
    try:

        
        while tickcount < n_ticks_max: 
            try:
                tickcount += 1
            
                # ---------------------------------------
                # wait for my start condition
                # ---------------------------------------
                if start_condition is not None:
                    if not isinstance(start_condition, str):
                        start_condition = start_condition.iso

                    wait_for_start_condition(start_condition)


                # ---------------------------------------
                # check if I should stop
                # ---------------------------------------

                if not is_dryrun and not ignore_time and f_get_time() <= end_time:
                    printf(make_zulustr(get_utcnow()) + ' | Time is up... finshing')
                    break

                if not has_started:
                    printf(make_zulustr(get_utcnow()) + ' | Starting Telescope...')
                    dc = __run_fun(f_start, dc)
                    has_started = True



                # ---------------------------------------
                # perform the test
                # ---------------------------------------

                if f_tick is None:
                    pass
                elif ticker is not None:
                    try:
                        printf(make_zulustr(get_utcnow()) + f' | calling next(tick) {tickcount} ...')
                        dci = next(ticker)
                        assert isinstance(dci, dict), 'expected dict return type for tick iterator'
                        if dci != dc:
                            dc = {**dc, **dci}
                    except StopIteration:
                        printf(make_zulustr(get_utcnow()) + ' | Last Iteration Reached... stopping loop')
                        break
                elif hasattr(f_tick, '__call__'):
                    printf(make_zulustr(get_utcnow()) + f' | calling tick {tickcount} ...')
                    dc = __run_fun(f_tick, dc)
                else:
                    raise Exception('f_tick is of unknown type')

                printf(make_zulustr(get_utcnow()) + f' | completed tick {tickcount} ...')
            except Exception as err:
                if skip_faulty_ticks:
                    print_red('ERROR: ' + str(err))
                else:
                    raise

        dc = __run_fun(f_post, dc)

        t_end = get_utcnow()
        t_elapsed = t_start - t_end

        printf(make_zulustr(get_utcnow()) + f' | Finished main loop (t_elapsed={t_elapsed})') 
        
    except Exception as err:
        print_red('ERROR: ' + str(err))
        raise
    finally:
        # ---------------------------------------+
        # shutdown the antenna
        # ---------------------------------------
        dc = __run_fun(f_finish, dc)

    return {}, t_elapsed, dc