# This is prepared plugin DB for test purpuses
from markupsafe import Markup

plugins = [
    {'name': 'lund_reader', 'type': 'reader'},
    {'name': 'beagle_reader', 'type': 'reader'},
    {'name': 'hepmc_reader', 'type': 'reader'},
    {'name': 'g4e_reader', 'type': 'reader'},
    {'name': 'gemc_reader', 'type': 'reader'},
    {'name': 'jana', 'type': ''},
    {'name': 'eic_smear', 'type': ''},
    {'name': 'event_writer', 'type': ''},
    {'name': 'vmeson', 'type': ''},
    {'name': 'open_charm', 'type': ''},
]

plugins_by_name = {p['name']: p for p in plugins}

def prepare_plugins():
    """Sets predefined values for plugins set"""

    # all plugins have some help and verbosity level
    for plugin in plugins:
        plugin['help'] = plugin['name'] + " help"
        plugin['config'] = [
            {'name': 'verbose', 'type': 'int', 'value': 0, 'help': Markup('verbosity level: 0 - silent, 2 - print all')}
        ]

    #
    # === jana - general flags ===
    plugins_by_name['jana']['help'] = Markup("""
          General configuration for JANA2 framework itself<br>          
          <br>
          <a href="https://jeffersonlab.github.io/JANA2/Installation.html" target='_blank'>More documentation</a>
          """)

    plugins_by_name['jana']['config'].extend(
        [
            {'name': 'nevents',  'type': 'int',   'value': 0,  'help': Markup('Number of events to process. 0 = all')},
            {'name': 'nskip',    'type': 'int',   'value': 0,  'help': Markup('Number of events to skip')},
            # {'name': 'nthreads', 'type': 'int',    'value': 1,  'help': Markup('Number of processing threads')},
            {'name': 'output',   'type': 'string', 'value': 'out.root', 'help': Markup('Output file name')},
        ]
    )

    #
    # === beagle_reader ===
    plugins_by_name['beagle_reader']['help'] = Markup("""
       Opens files from BeAGLE event generator as a data source<br>
       <strong>BeAGLE</strong> - <strong>Be</strong>nchmark <strong>eA</strong> <strong>G</strong>enerator for <strong>LE</strong>ptoproduction 
       <br>
       <a href="https://wiki.bnl.gov/eic/index.php/BeAGLE" target='_blank'>Documentation</a>

       """)

    # === lund_reader ===
    plugins_by_name['lund_reader']['help'] = Markup("""
       Opens files in LUND format. <br>
       The format has many flavours,  
       <a href="https://gemc.jlab.org/gemc/html/documentation/generator/lund.html"> original pythia6 </a> or 
       <a href="https://wiki.bnl.gov/eic/index.php/PYTHIA">BNL pythia 6</a> are examples      
       """)

    plugins_by_name['g4e_reader']['help'] = Markup("""
           Opens files from Geant4EIC (G4E) root flattened format.
           <a href="https://gitlab.com/jlab-eic/g4e/">G4E Official GitLab page </a>
           """)

    plugins_by_name['gemc_reader']['help'] = Markup("""
               <strong>(!) deprecated </strong> and not guaranteed to work. 
               <a href="https://gemc.jlab.org/gemc/html/index.html">GEMC page</a>
               """)

    # === EIC-smear ===
    plugins_by_name['eic_smear']['help'] = Markup("""
               Enables smearing based on EIC-Smear and JLEIC smear procedures<br>
               parameter 'detector' must be set to enable smearing               
               """)

    plugins_by_name['eic_smear']['config'].append(
        {'name': 'detector', 'type': 'string', 'value': 'jleic', 'help': Markup('Detector: beast, jleic, zeus, ephoenix ')}
    )

    # === Event writer ===
    plugins_by_name['event_writer']['help'] = Markup("""
                   Create TTree with flattened Event data. (Create branches according to data available)
                   """)

    # === Open charm analysis ===
    plugins_by_name['open_charm']['help'] = Markup("""
           Makes analysis on charm particles. Extracting basic invariant masses and other parameters with or without smearing
           """)

    plugins_by_name['open_charm']['config'].extend(
        [
            {'name': 'e_beam_energy', 'type': 'float', 'value': 5, 'help': Markup('electron beam energy GeV')},
            {'name': 'ion_beam_energy', 'type': 'float', 'value': 100, 'help': Markup('ion beam energy GeV ')},
        ]
    )

    plugins_by_name['vmeson']['config'].extend(
        [
            {'name': 'e_beam_energy', 'type': 'float', 'value': 5, 'help': Markup('electron beam energy GeV')},
            {'name': 'ion_beam_energy', 'type': 'float', 'value': 100, 'help': Markup('ion beam energy GeV ')},
        ]
    )

    return plugins