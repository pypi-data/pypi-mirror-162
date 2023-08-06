"""
  New job class to run Prod6 for Paranal and La Palma
"""

__RCSID__ = "$Id$"

# generic imports
import json
import collections
# DIRAC imports
import DIRAC
from DIRAC.Interfaces.API.Job import Job
from CTADIRAC.Core.Utilities.tool_box import DATA_LEVEL_METADATA_ID


class Prod6MCPipeNSBJob(Job):
  """ Job extension class for Prod5 MC NSB simulations,
  takes care of running corsika piped into simtel
  2 output files are created for Dark and Moon NSB
  """

  def __init__(self, cpu_time=259200):
    """ Constructor takes almosst everything from base class

    Keyword arguments:
    cpuTime -- max cpu time allowed for the job
    """
    Job.__init__(self)
    self.setCPUTime(cpu_time)
    self.setName('Prod6MC_Generation')
    self.setType('MCSimulation')
    self.package = 'corsika_simtelarray'
    self.version = '2022-08-03'
    self.compiler = 'gcc83_matchcpu'
    self.program_category = 'tel_sim'
    self.prog_name = 'sim_telarray'
    self.configuration_id = 15
    self.output_data_level = DATA_LEVEL_METADATA_ID['DL0']
    self.base_path = '/vo.cta.in2p3.fr/MC/PROD6/'
    self.catalogs = json.dumps(['DIRACFileCatalog', 'TSCatalog'])
    self.metadata = collections.OrderedDict()

  def set_site(self, site):
    """ Set the site to simulate

    Parameters:
    site -- a string for the site name (LaPalma)
    """
    if site in ['Paranal', 'LaPalma']:
      DIRAC.gLogger.info('Set Corsika site to: %s' % site)
      self.cta_site = site
    else:
      DIRAC.gLogger.error('Site is unknown: %s' % site)
      DIRAC.exit(-1)

  def set_particle(self, particle):
    """ Set the corsika primary particle

    Parameters:
    particle -- a string for the particle type/name
    """
    if particle in ['gamma', 'gamma-diffuse', 'electron', 'proton', 'helium']:
      DIRAC.gLogger.info('Set Corsika particle to: %s' % particle)
      self.particle = particle
    else:
      DIRAC.gLogger.error('Corsika does not know particle type: %s' % particle)
      DIRAC.exit(-1)

  def set_pointing_dir(self, pointing):
    """ Set the pointing direction, North or South

    Parameters:
    pointing -- a string for the pointing direction
    """
    if pointing in ['North', 'South', 'East', 'West']:
      DIRAC.gLogger.info('Set Pointing dir to: %s' % pointing)
      self.pointing_dir = pointing
    else:
      DIRAC.gLogger.error('Unknown pointing direction: %s' % pointing)
      DIRAC.exit(-1)

  def set_meta_data(self):
    """ define the common meta data of the application
    """
    # The order of the metadata dictionary is important,
    # since it's used to build the directory structure
    self.metadata['array_layout'] = 'Alpha'
    self.metadata['site'] = self.cta_site
    self.metadata['particle'] = self.particle
    # for air shower simulation means North=0 and South=180
    # but here piped into tel_sim so North=180 and South=0
    if self.pointing_dir == 'North':
      self.metadata['phiP'] = 180
    if self.pointing_dir == 'South':
      self.metadata['phiP'] = 0
    self.metadata['thetaP'] = float(self.zenith_angle)
    self.metadata[self.program_category + '_prog'] = self.prog_name
    self.metadata[self.program_category + '_prog_version'] = self.version
    self.metadata['data_level'] = self.output_data_level
    self.metadata['configuration_id'] = self.configuration_id
    # self.metadata['sct'] = False

  def setupWorkflow(self, debug=False):
    """ Override the base class job workflow to adapt to NSB test simulations
        All parameters shall have been defined before that method is called.
    """
    # step 1 - debug only
    i_step = 1
    if debug:
      ls_step = self.setExecutable('/bin/ls -alhtr', logFile='LS_Init_Log.txt')
      ls_step['Value']['name'] = 'Step%i_LS_Init' % i_step
      ls_step['Value']['descr_short'] = 'list files in working directory'
      i_step += 1

      env_step = self.setExecutable('/bin/env', logFile='Env_Log.txt')
      env_step['Value']['name'] = 'Step%i_Env' % i_step
      env_step['Value']['descr_short'] = 'Dump environment'
      i_step += 1
    
    # step 2 : use new CVMFS repo
    sw_step = self.setExecutable('cta-prod-setup-software',
                                 arguments='-p %s -v %s -a simulations -g %s -r /cvmfs/sw.cta-observatory.org/software' %
                                 (self.package, self.version, self.compiler),
                                 logFile='SetupSoftware_Log.txt')
    sw_step['Value']['name'] = 'Step%i_SetupSoftware' % i_step
    sw_step['Value']['descr_short'] = 'Setup software'
    i_step += 1

    # step 3 run corsika+sim_telarray
    prod_exe = './dirac_prod6_run'
    prod_args = '--start_run %s --run %s --align-b-field --with-full-moon %s %s %s %s' % \
                (self.start_run_number, self.run_number,
                 self.cta_site, self.particle, self.pointing_dir,
                 self.zenith_angle)

    cs_step = self.setExecutable(prod_exe, arguments=prod_args,
                                 logFile='CorsikaSimtel_Log.txt')
    cs_step['Value']['name'] = 'Step%i_CorsikaSimtel' % i_step
    cs_step['Value']['descr_short'] = 'Run Corsika piped into simtel'
    i_step += 1

    # step 4 verify the number of events in the simtel file
    data_output_pattern = 'Data/*.simtel.zst'
    mgv_step = self.setExecutable('dirac_simtel_check',
                                  arguments="'%s'" %
                                  (data_output_pattern),
                                  logFile='Verify_n_showers_Log.txt')
    mgv_step['Value']['name'] = 'Step%i_VerifyNShowers' % i_step
    mgv_step['Value']['descr_short'] = 'Verify number of showers'
    i_step += 1

    # step 5 - define meta data, upload file on SE and register in catalogs
    self.set_meta_data()
    md_json = json.dumps(self.metadata)

    meta_data_field = {'array_layout': 'VARCHAR(128)', 'site': 'VARCHAR(128)',
                       'particle': 'VARCHAR(128)',
                       'phiP': 'float', 'thetaP': 'float',
                       self.program_category + '_prog': 'VARCHAR(128)',
                       self.program_category + '_prog_version': 'VARCHAR(128)',
                       'data_level': 'int', 'configuration_id': 'int', 'merged': 'int'}
    md_field_json = json.dumps(meta_data_field)

    # Upload and register data - NSB=1 dark
    file_meta_data = {'runNumber': self.run_number, 'nsb': 1}
    file_md_json = json.dumps(file_meta_data)
    data_output_pattern = 'Data/*dark*.simtel.zst'

    dm_step = self.setExecutable('cta-prod-managedata',
                                 arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Data" %
                                 (md_json, md_field_json, file_md_json,
                                  self.base_path, data_output_pattern, self.package,
                                  self.program_category, self.catalogs),
                                 logFile='DataManagement_dark_Log.txt')
    dm_step['Value']['name'] = 'Step%s_DataManagement' % i_step
    dm_step['Value']['descr_short'] = 'Save data files to SE and register them in DFC'
    i_step += 1

    # Upload and register log and histo file - NSB=1
    file_meta_data = {}
    file_md_json = json.dumps(file_meta_data)
    log_file_pattern = 'Data/*dark*.log_hist.tar'
    log_step = self.setExecutable('cta-prod-managedata',
                                  arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Log" %
                                  (md_json, md_field_json, file_md_json,
                                   self.base_path, log_file_pattern, self.package,
                                   self.program_category, self.catalogs),
                                  logFile='LogManagement_dark_Log.txt')
    log_step['Value']['name'] = 'Step%s_LogManagement' % i_step
    log_step['Value']['descr_short'] = 'Save log to SE and register them in DFC'
    i_step += 1

    # Now switching to half moon NSB
    # Upload and register data - NSB=5 half moon
    file_meta_data = {'runNumber': self.run_number, 'nsb': 5}
    file_md_json = json.dumps(file_meta_data)
    data_output_pattern = 'Data/*-moon*.simtel.zst'

    dm_step = self.setExecutable('cta-prod-managedata',
                                 arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Data" %
                                 (md_json, md_field_json, file_md_json,
                                  self.base_path, data_output_pattern, self.package,
                                  self.program_category, self.catalogs),
                                 logFile='DataManagement_moon_Log.txt')
    dm_step['Value']['name'] = 'Step%s_DataManagement' % i_step
    dm_step['Value']['descr_short'] = 'Save data files to SE and register them in DFC'
    i_step += 1

    # Upload and register log file - NSB=5
    file_meta_data = {}
    file_md_json = json.dumps(file_meta_data)
    log_file_pattern = 'Data/*-moon*.log_hist.tar'
    log_step = self.setExecutable('cta-prod-managedata',
                                  arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Log" %
                                  (md_json, md_field_json, file_md_json,
                                   self.base_path, log_file_pattern, self.package,
                                   self.program_category, self.catalogs),
                                  logFile='LogManagement_moon_Log.txt')
    log_step['Value']['name'] = 'Step%s_LogManagement' % i_step
    log_step['Value']['descr_short'] = 'Save log to SE and register them in DFC'
    i_step += 1

    # Now switching to full moon NSB
    # Upload and register data - NSB=19 full moon
    file_meta_data = {'runNumber': self.run_number, 'nsb': 19}
    file_md_json = json.dumps(file_meta_data)
    data_output_pattern = 'Data/*-fullmoon*.simtel.zst'

    dm_step = self.setExecutable('cta-prod-managedata',
                                 arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Data" %
                                 (md_json, md_field_json, file_md_json,
                                  self.base_path, data_output_pattern, self.package,
                                  self.program_category, self.catalogs),
                                 logFile='DataManagement_fullmoon_Log.txt')
    dm_step['Value']['name'] = 'Step%s_DataManagement' % i_step
    dm_step['Value']['descr_short'] = 'Save data files to SE and register them in DFC'
    i_step += 1

    # Upload and register log file - NSB=19
    file_meta_data = {}
    file_md_json = json.dumps(file_meta_data)
    log_file_pattern = 'Data/*-fullmoon*.log_hist.tar'
    log_step = self.setExecutable('cta-prod-managedata',
                                  arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Log" %
                                  (md_json, md_field_json, file_md_json,
                                   self.base_path, log_file_pattern, self.package,
                                   self.program_category, self.catalogs),
                                  logFile='LogManagement_fullmoon_Log.txt')
    log_step['Value']['name'] = 'Step%s_LogManagement' % i_step
    log_step['Value']['descr_short'] = 'Save log to SE and register them in DFC'
    i_step += 1
   
    # Step 6 - debug only
    if debug:
      ls_step = self.setExecutable('/bin/ls -Ralhtr', logFile='LS_End_Log.txt')
      ls_step['Value']['name'] = 'Step%s_LSHOME_End' % i_step
      ls_step['Value']['descr_short'] = 'list files in Home directory'
      i_step += 1

    # Number of showers is passed via an environment variable
    self.setExecutionEnv({'NSHOW': '%s' % self.n_shower})
