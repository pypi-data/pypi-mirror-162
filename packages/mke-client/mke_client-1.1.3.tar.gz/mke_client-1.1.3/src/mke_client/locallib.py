import re
import datetime
import json
import hashlib
import os

import logging
import sys


_log = logging.getLogger()
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
_log.addHandler(streamHandler)

from mke_client.helpers import get_utcnow, make_zulustr, parse_zulutime
import mke_client.filesys_storage_api as filesys
from mke_client.rimlib import BaseRimObj, allowed_status_codes, wait_for_start_condition


add_to_json = lambda fld, to_add: json.dumps({**(json.loads(fld) if fld else {}), **to_add})



dc_antennas = {
    'localhost': 'localhost',
    'test_antenna': '<no-ip-needed>',
    'test-antenna': '<no-ip-needed>',
    'skampi': '10.96.64.10',
    'sim-bonn': '134.104.22.44',
    }


class LocalExperiment(BaseRimObj):
    """An interface object to get access to experiments in the 
    database.

    Args:
        RimObj: _description_
    """
    __tablename = 'experiments'
    def __init__(self, id=0, fallback_local_basepath = 'output', exp_row = {}, **kwargs):
        """create a new Experiment object with an id to get access 
        to this expiriment objects row in the database

        Args:
            id (int): the id of the analyses in the DB

        """

        id = max(int(id), 1)

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

        if 'antenna_ip' in kwargs:
            antenna_ip = kwargs['antenna_ip']
            if ':' in antenna_ip:
                antenna_ip = antenna_ip.split(':')[-2]

            if antenna_ip.startswith('http://'):
                antenna_ip = antenna_ip.replace('http://', '')
            if antenna_ip.startswith('https://'):
                antenna_ip = antenna_ip.replace('https://', '')
                
            if antenna_ip.startswith('//'):
                antenna_ip = antenna_ip.replace('//', '')

            antenna_id = antenna_ip.replace('.', '_')
            if antenna_ip and antenna_ip[0].isdigit():
                antenna_id = 'IP_' + antenna_ip
            
            kwargs['antenna_id'] = antenna_id


        exp_row = {**defaults, **exp_row, **kwargs}

        exp_name = exp_row['script_name'] if 'script_name' in exp_row and exp_row['script_name'] else 'NA_scr'
        antenna_id = exp_row['antenna_id'] if 'antenna_id' in exp_row and exp_row['antenna_id'] else 'NA_ant'
        tag = exp_row['tag'] if 'tag' in exp_row and exp_row['tag'] else ''
        dtime = get_utcnow()

        self.fallback_local_basepath = fallback_local_basepath
        self.savedir = filesys.get_exp_save_dir(self.fallback_local_basepath, 
                                                    dtime=dtime, 
                                                    experiment_id=id, 
                                                    experiment_name=exp_name, 
                                                    antenna_id=antenna_id,
                                                    tag=tag,
                                                    make_dir=True)



        if not exp_row['script_out_path']:
            outpth = filesys.get_exp_save_filepath(self.fallback_local_basepath, 
                                            dtime=dtime, 
                                            experiment_id=id,  
                                            antenna_id=antenna_id,
                                            experiment_name=exp_name, 
                                            make_dir=False)
                                            
            exp_row['script_out_path'] = outpth

        # initial commit
        self.commit('experiments', exp_row, id)

        super().__init__('<ip-is-not-needed>', self.__tablename, id)

#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################

    def commit(self, tablename, dc, id=None, raise_on_exists=False):
        
        dbpath = filesys.join(self.savedir, tablename + '.json')
        if os.path.exists(dbpath):
            with open(dbpath, 'r') as fp:
                db = json.load(fp)
        else:
            db = {}
        
        if id is not None and id in db and raise_on_exists:
            raise Exception('ID {} already exists in db: {}'.format(id, dbpath))
        
        if id is None and db and 'id' in dc:
            id = int(dc['id']) if not isinstance(dc['id'], int) and dc['id'].isdigit() else dc['id']
        elif id is None and db:
            keys = [int(k) for k in db.keys()]
            id = max(keys) + 1
        elif id is None and not db:
            id = 1

        dc['id'] = id

        id = str(id)

        if id in db:
            # merge
            db[id] = {**db[id], **dc}
        else:
            # add
            db[id] = dc
        
        with open(dbpath, 'w+') as fp:
            json.dump(db, fp, indent=3)

        return db[id]
            


    def get(self, tablename=None, id=None, **kwargs):
        if id is None:
            id = self.id
        if tablename is None:
            tablename = self.tablename

        dbpath = filesys.join(self.savedir, tablename + '.json')
        if not os.path.exists(dbpath):
            raise FileNotFoundError('file {} was not found'.format(dbpath))
        with open(dbpath, 'r') as fp:
            db = json.load(fp)
        return db[str(id)]  


    def patch_me(self, **kwargs):
        return self.commit(self.tablename, kwargs['json'], self.id)
        
    def get_my_antenna(self):
        raise NotImplementedError("get_my_antenna is not valid for a 'local' experiment object")

    def get_my_antenna_ip(self) -> dict:
        me = self.get_me()
        return dc_antennas[me['antenna_id']]

        
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################


    def wait_for_start_condition(self, wait_increment_max=10, verb=True):
        dc = self.get()
        wait_for_start_condition(dc['start_condition'], wait_increment_max,  verb)
            
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################


    def __register_andor_upload_exp_aux_files(self, files, is_upload):
        
        parent_id = self.id
        parent = self.get()
        devices_parent = json.loads(parent['devices_json'])
        devices_new = []

        if 'ALL' in files:
            return {'error:' 'the key ALL is forbidden for aux file upload!'}, 413
        
        basedir = filesys.join(os.path.dirname(parent['script_out_path']), 'data_aux')
        exp_filename = os.path.basename(parent['script_out_path'])


        try:
            tstrt = datetime.datetime.strptime(exp_filename[:15], filesys.timeformat_str)
        except:
            tstrt = None
        
        if not tstrt and parent['time_started_iso']:
            tstart = parse_zulutime(parent['time_started_iso'])
        elif not tstrt and parent['start_condition']:
            tstart = parse_zulutime(parent['start_condition'])
        else:
            return {'error:' 'could not find a suitable candidate for start time in parent!'}, 404
        
        # iterate and save all aux files for my measurement data object
        dc = {}
        for device, f in files.items():

            if is_upload:
                ext = os.path.splitext(f.filename)[-1]
            elif isinstance(f, str):
                ext = f
            else:
                ext = None

            ext = ext if ext and ext.startswith('.') else '.csv'

            # get a suitable filepath for the current aux file
            pth_for_upload = filesys.get_exp_aux_save_filepath(basedir, 
                                                    tstart, 
                                                    parent_id, 
                                                    device_key=device,
                                                    extension=ext, 
                                                    make_dir=(not is_upload))

            # make a aux file table entry for the new aux file
            aux_row = {
                "parent_id": parent_id, 
                "path": pth_for_upload,
                "parent_type": 'measurement_data', 
                'device': device
            }
            
            self.commit('aux_files', aux_row)

            dc[device] = aux_row
            _log.debug('adding row: ' + pth_for_upload)


            if is_upload:
                _log.debug('saving file: ' + pth_for_upload)
                f.save(pth_for_upload)
                
            if device not in devices_parent:
                devices_new.append(device)

        # -------------------------------------------------------------
        # STEP 2.0: upload devices to parent if need be
        # -------------------------------------------------------------
        if devices_new: 
            parent['devices_json'] = json.dumps(devices_parent + devices_new)


        # -------------------------------------------------------------
        # STEP 2.1: upload AuxFiles to table and update row entry results
        # -------------------------------------------------------------
        if len(dc) > 0:
            
            # now the aux files should have ids
            # add complete aux files to experiment
            files_aux_new = {v['id']:v['path'] for v in dc.values()}
            parent['aux_files_json'] = add_to_json(parent['aux_files_json'], files_aux_new)

        self.commit(self.tablename, parent)

        # -------------------------------------------------------------
        # STEP 3: make result return dictionary and return
        # -------------------------------------------------------------
        ret = { 'id': parent['id'], 
                'path': parent['script_out_path'],
                'aux_files': [(k, v['id'], v['path']) for k, v in dc.items()]}
        
        return ret, 200
        

    def __register_exp_aux_files(self, **kwargs):
        dc = kwargs['json']
        extensions = dc['extensions']   

        try:
            ret, code = self.__register_andor_upload_exp_aux_files(extensions, is_upload=False)
            if code >= 300:
                raise Exception('ERROR! Return Code = {}. Message = {}'.format(code, json.dumps(ret)))
            return ret
        except Exception as err:
            raise err

    
    def __upload_exp_aux_files(self, **kwargs):
        files = kwargs['files']

        try:
            ret, code = self.__register_andor_upload_exp_aux_files(files, is_upload=True)
            if code >= 300:
                raise Exception('ERROR! Return Code = {}. Message = {}'.format(code, json.dumps(ret)))
            return ret
        except Exception as err:
            raise err

#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################

    def __register_andor_upload_measurement_data(self, parent_id=None, row=None, files={}, is_upload=False):
        
        parent = self.get(self.tablename, self.id)
        if parent_id is None:
            parent_id = parent['id']

        if 'ALL' in files:
            return {'error:' 'the key ALL is forbidden for aux file upload!'}, 413
        
        if 'time_iso' not in row or parse_zulutime(row['time_iso']) is None:
            return {'error:' 'need to give the time_iso field as zulu style string in row!'.format(parent_id)}, 404

        if 'results_json' in parent:
            results = json.loads(parent['results_json'])
        elif 'results' in parent and isinstance(parent['results'], dict):
            results = parent['results']
        else:
            results = {}
            

        devices_parent = json.loads(parent['devices_json'])
        devices_new = []
        # meas_id = max([int(k) for k in results.keys()]) + 1 if results else 0
        
        main_file = None
        sub_files = {}
        for k, v in files.items():
            if k == 'ACU':
                main_file = v
            else:
                sub_files[k] = v

        if main_file is None:
            return {'error:' 'the key ACU was not found in the uploaded files!'}, 404
        
        tstart = parse_zulutime(row['time_iso'])    
        basedir = os.path.dirname(parent['script_out_path'])

        # -------------------------------------------------------------
        # STEP 1: make measurement_data row and upload ACU file
        # -------------------------------------------------------------

        # make a measurement_data table entry for the new file in order to get an ID
        meas_data_row = {
            "experiment_id": parent_id,
            "antenna_id": parent['antenna_id'],
            "meas_name": parent['script_name'], 
            "devices_json": parent['devices_json'],
            "status": 'INITIALIZED', 
            'aux_files_json': '{}'
        }

        for k in row.keys():
            if k not in meas_data_row:
                meas_data_row[k] = row[k]
        
        # get tag to add to aux file as well (only the first one, if there are many)
        tag = meas_data_row['tags']
        if tag and ',' in tag:
                tag = tag.split(',')[0]
        tag = tag.strip() if tag else tag
        
        meas_data_row = self.commit('measurement_data', meas_data_row)

        # now that we have the ID we can make and set a path for the ACU file
        pth_for_upload = filesys.get_exp_save_pth_datafile(basedir, 
                                                    tstart, 
                                                    parent_id, 
                                                    meas_data_row['id'], 
                                                    'ACU', 
                                                    extension='.csv', 
                                                    make_dir=is_upload)

        meas_data_row['filename'] = pth_for_upload

        # -------------------------------------------------------------
        # STEP 1.1: upload meas id and path to results_json of parent experiment
        # -------------------------------------------------------------
        
        meas_data_row = self.commit('measurement_data', meas_data_row)

        file_meas_new = {int(meas_data_row['id']): meas_data_row['filename']}
        _log.debug('adding {} to results_json in : {}'.format(len(file_meas_new), parent['id']))
        
        
        parent['results_json'] = add_to_json(parent['results_json'], file_meas_new)

        parent = self.commit('experiments', parent)

        # -------------------------------------------------------------
        # STEP 2: make aux_files rows for all aux files and upload them
        # -------------------------------------------------------------


        # iterate and save all aux files for my measurement data object
        dc = {}
        for key, f in sub_files.items():

            if is_upload:
                ext = os.path.splitext(f.filename)[-1]
            elif isinstance(f, str):
                ext = f
            else:
                ext = None

            ext = ext if ext and ext.startswith('.') else '.csv'

            # get a suitable filepath for the current aux file
            pth_for_upload = filesys.get_exp_save_pth_datafile(basedir, 
                                                    tstart, 
                                                    parent_id, 
                                                    meas_data_row['id'], 
                                                    key, 
                                                    extension=ext, 
                                                    make_dir=is_upload)
            
            # make a aux file table entry for the new aux file
            aux_row = {
                'id': 0,
                "parent_id": meas_data_row['id'], 
                "path": pth_for_upload,
                "parent_type": 'measurement_data', 
                'device': key,
                "tag": tag,
            }

            _log.debug('adding row: ' + json.dumps(aux_row))
            aux_row = self.commit('aux_files', aux_row)
            dc[key] = aux_row


            if key and key not in devices_parent:
                devices_new.append(key)

        # -------------------------------------------------------------
        # STEP 2.1: add new devices to devices in parent
        # -------------------------------------------------------------
        if devices_new: 
            parent['devices_json'] = json.dumps(devices_parent + devices_new)
            
        parent = self.commit('experiments', parent, parent_id)

        # -------------------------------------------------------------
        # STEP 2.2: upload AuxFiles to table and update row entry results
        # -------------------------------------------------------------
        if len(dc) > 0:
            
            # now the aux files should have ids
            # add complete aux files to measurement
            files_aux_new = {v['device']:v['path'] for v in dc.values()}
            meas_data_row['aux_files_json'] = add_to_json(meas_data_row['aux_files_json'], files_aux_new)
        
        aux_row = self.commit('measurement_data', meas_data_row)


        # -------------------------------------------------------------
        # STEP 3: make result return dictionary and return
        # -------------------------------------------------------------
        ret = { 'id': meas_data_row['id'], 
                'path': meas_data_row['filename'],
                'aux_files': [(k, v['id'], v['path']) for k, v in dc.items()]}
        
        return ret, 200
        
    def __register_measurement_data(self, **kwargs):
        dc = kwargs['json']
        experiment_id = dc['id']
        row = dc['row'] if 'row' in dc else {}
        extensions = dc['extensions']
        
        try:
            ret, code = self.__register_andor_upload_measurement_data(experiment_id, row, extensions, is_upload=False)
            if code >= 300:
                raise Exception('ERROR! Return Code = {}. Message = {}'.format(code, json.dumps(ret)))
            return ret
        except Exception as err:
            raise err
            

    def __upload_measurement_data(self, **kwargs):
        dc = kwargs['json']
        experiment_id = dc['id']
        row = dc['row'] if 'row' in dc else {}
        files = kwargs['files']

        try:
            ret, code = self.__register_andor_upload_measurement_data(experiment_id, row, files, is_upload=True)
            if code >= 300:
                raise Exception('ERROR! Return Code = {}. Message = {}'.format(code, json.dumps(ret)))
            return ret
        except Exception as err:
            raise err

#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################

        
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

        dc = self.__upload_measurement_data(json=payload, files=files)
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
            extensions = {k: '.csv' for k in devices_to_add}
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

        dc = self.__register_measurement_data(json=payload)
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

        dc = self.__register_exp_aux_files(json=payload)
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

        dc = self.__upload_exp_aux_files(json=payload, files=files)
        return dc['aux_files'] 



#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################


def get_new_id(folderpath):

    if os.path.exists(folderpath) and os.path.isdir(folderpath):
        subfolders = [ os.path.basename(f.path) for f in os.scandir(folderpath) if f.is_dir() ]

        def get_id_from_exp_path(s):
            if s.count('_') > 2 and len(s) > len('20220730_1112_1_'):
                return int(s.split('_')[2])
            else:
                return 0
        ids = [get_id_from_exp_path(s) for s in subfolders]
        new_id = max(ids) + 1
    else:
        new_id = 1

    return new_id


def get_default_dc(script_in_path, basedir, id=0, start_condition=None, antenna_id=None, kind='exp'):

            
    # get start time from db entry if available
    if start_condition is None:
        start_condition = make_zulustr(get_utcnow())

    if isinstance(start_condition, datetime.datetime):
        start_condition = make_zulustr(start_condition)
    

    dc = {
            "id": id,

            "caldav_uid": None,
            "caldav_calendar": None,

            "script_name": os.path.basename(script_in_path.split('.')[0]),
            "script_version": None,
            "script_in_path": script_in_path,
            "script_out_path": None,

            "antenna_id": antenna_id,
            "script_params_json": '{}',
            
            "results_json": '{}',

            "start_condition": start_condition,
            "time_initiated_iso": None,
            "duration_expected_hr_dec": 0.1,
            "time_started_iso": None,
            "time_finished_iso": None,

            "status": 'INITIALIZING',
            "errors": '',

            "devices_json": '["ACU"]',
            "needs_manual_upload": 0,
            "comments": None,
            "forecasted_oc": '',
            "papermill_json": '{}',
            "aux_files_json": '{}',
            
        }

    if not dc['script_version'] and os.path.exists(dc['script_in_path']):
        tlast_change = os.path.getmtime(dc['script_in_path'])
        dtlast_change = make_zulustr(datetime.datetime.fromtimestamp(tlast_change))
        with open(dc['script_in_path'],'rb') as f:
            dc['script_version'] = hashlib.md5(f.read()).hexdigest() + '_' + dtlast_change

    if not dc['script_out_path'] and start_condition is not None:
        # remove microseconds
        timed = parse_zulutime(start_condition)
        
        inpth = os.path.basename(dc['script_in_path'].split('.')[0])
        if inpth.startswith('script_'): inpth = inpth[len('script_'):]
        if inpth.startswith('exp_'): inpth = inpth[len('exp_'):]
        if inpth.startswith('experiment_'): inpth = inpth[len('experiment_'):]
        if inpth.startswith('test_'): inpth = inpth[len('test_'):]
        if inpth.startswith('ana_'): inpth = inpth[len('ana_'):]
        if inpth.startswith('analysis_'): inpth = inpth[len('analysis_'):]
        if inpth.startswith('base_'): inpth = inpth[len('base_'):]

        try:
            id = dc['id']
        except: 
            id = 0

        antenna = dc['antenna_id'] if dc['antenna_id'] else 'no_ant'
        name = inpth
        if kind == 'exp':
            pth_out = filesys.get_exp_save_filepath(basedir, timed, id, antenna, name, make_dir=False)
        elif kind == 'ana':
            pth_out = filesys.get_ana_save_filepath(basedir, timed, id, antenna, name, make_dir=False)
        else:
            raise Exception('script type neither experiment nor analysis. but instead ' + kind)

        if not filesys.is_pathname_valid(pth_out):
            # handle windows style volume descriptors starting with C: or similar
            if re.match(r"(^[A-Za-z]:).+", pth_out):
                pth_out = pth_out[:2] + re.sub(r'[\n\\\*>:<?\"|\t]', '', pth_out[2:])
            else:
                pth_out = re.sub(r'[\n\\\*>:<?\"|\t]', '', pth_out)
        
        if not filesys.is_pathname_valid(pth_out):
            raise Exception('The out script file path is invalid. GOT: "' + pth_out + '"')

        pth_out = pth_out.strip()

        dc['script_out_path'] = pth_out

    return dc

