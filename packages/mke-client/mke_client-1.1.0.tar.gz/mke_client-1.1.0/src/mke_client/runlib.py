import json



import mke_client.rimlib as rim
import mke_client.locallib as loc
import mke_client.filesys_storage_api as filesys
import mke_client.remexlib as rem

# import those under a new name instead of writing wrappers
from mke_client.remexlib import test_script as test_remote
from mke_client.remexlib import add_script as add_script_remote


def get_runner(script_in_path, antenna_id, out_folder='meas', start_condition=None, uri=None):
    """get a file to save a script under (e.G when running with papermill) as well as the default row as dict

    Args:
        script_in_path (str): the path of the original script file
        antenna_id (str): any antenna_id which an be looked up on the server or locally
        out_folder (str, optional): Only needed for local operation. The folder path to save results under. Defaults to 'meas'.
        start_condition (str, optional): The start time as zulu stype iso datetime string. Defaults to None.
        uri (str, optional): the URI under which to use ping a db server. Defaults to None.

    Returns:
        script_out_path: the path, where to save an output script
        dc: the dictionary containing all default values for the row
    """

    tablename = 'experiments'

    if uri:
        exp = rim.Experiment(-1, uri=uri)
        has_con = exp.ping_test()
    else:
        has_con = False

    if has_con:
        api = rem.RemexApiAccessor(uri=uri, scriptype=tablename)

        dc, status = rem.test_script(uri, tablename, script_in_path, antenna_id, start_condition)

        if not status == 'OK':
            raise Exception('invalid script given!')
        dc = api.post(dc)
    else:
        
        folderpath = filesys.join(out_folder, antenna_id)
        id = loc.get_new_id(folderpath)

        dc = loc.get_default_dc(script_in_path, 
                                    basedir=out_folder,
                                    id=id, 
                                    start_condition=start_condition,
                                    antenna_id=antenna_id, 
                                    kind='exp')

    return dc['script_out_path'], dc



def fill_script_params(params:dict, row:dict, dbserver_uri='<fallback-local>', fallback_local_basepath='meas'):
    """given a dictionary of parameters for a jupyter script to run, as well as 
    a dictionary containing the meta information for a script, this function will join the script parameters
    with all the default meta parameters needed.

    Args:
        params (dict): dictionary holding the default script parameters
        row (dict): dictionary holding all the sript meta information
        dbserver_uri (str, optional): The dbserver url to add as additional meta parameter. Defaults to '<fallback-local>'.
        fallback_local_basepath (str, optional): The local fallback folder for saving results, in case the server can not be reached. Defaults to 'meas'.

    Returns:
        dict: combined dictionary holding all needed paramaters for running an experiment
    """
    dc0 = dict(dbserver_uri=dbserver_uri, fallback_local_basepath = fallback_local_basepath)
    keys = 'antenna_id script_in_path script_out_path script_version script_name duration_expected_hr_dec comments forecasted_oc needs_manual_upload'.split()
    dc1 = {'experiment_id': row['id'], 'devices': json.loads(row['devices_json'])}
    dc2 = {k:row[k] for k in keys}            
    dc = {**dc2, **params, **dc1, **dc0}
    for k, v in dc0.items():
        dc[k] = v
    for k, v in dc1.items():
        dc[k] = v
    for k, v in dc1.items():
        dc[k] = v

    return dc




