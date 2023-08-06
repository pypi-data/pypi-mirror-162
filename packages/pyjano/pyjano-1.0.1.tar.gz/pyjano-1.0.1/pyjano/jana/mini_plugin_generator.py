import os

mini_smear_analysis = """
#include <JANA/JEventProcessor.h>
#include <JANA/Services/JGlobalRootLock.h>
#include <TH1D.h>
#include <TFile.h>
#include <Math/Vector4D.h>
#include <ejana/MainOutputRootFile.h>
#include <MinimalistModel/McGeneratedParticle.h>
#include <fmt/core.h>


class {{class_name}}Processor: public JEventProcessor {
private:
    std::shared_ptr<ej::MainOutputRootFile> m_file;
    int m_verbose;                /// verbosity level. 0-none, 1-some, 2-all
    TDirectory* m_plugin_dir;     /// Virtual sub-folder inside root file used for this specific plugin

    /// Declare histograms here
    TH1D* h1d_pt;

public:
    explicit {{class_name}}Processor() {
    }

    void Init() override {
        auto app = GetApplication();

        // Get main ROOT output file 
        m_file = app->GetService<ej::MainOutputRootFile>();

        // Set parameters that can be controlled from command line
        m_verbose = 1;
        app->SetDefaultParameter("{{plugin_name}}:verbose", m_verbose, "Verbosity level 0=none, 1=some, 2=all");

        if(m_verbose) {
            fmt::print("{{class_name}}Processor::Init()\\n  {{plugin_name}}:verbose={}\\n", m_verbose);
        }

        // Setup histograms
        m_plugin_dir = m_file->mkdir("{{plugin_name}}"); // Create a subdir inside dest_file for these results
        m_plugin_dir->cd();
        h1d_pt = new TH1D("e_pt", "electron pt", 100,0,10);
    }

    void Process(const std::shared_ptr<const JEvent>& event) override {
        // This function is called every event
        if(m_verbose == 2) fmt::print("Begin of event {} \\n", event->GetEventNumber());

        // Check if smearing factory exists and take particles from smearing factory
        bool has_smearing = event->GetFactory<minimodel::McGeneratedParticle>("smear"); 
        auto particles = has_smearing 
                         ? event->Get<minimodel::McGeneratedParticle>("smear")
                         : event->Get<minimodel::McGeneratedParticle>();

        // Acquire any results you need for your analysis
         event->Get<minimodel::McGeneratedParticle>();

        // Go through particles
        for(auto& particle: particles) {

            // select electron
            if(std::abs(particle->pdg) != 11) continue;            
            if(!particle->is_stable) continue;
             
            // smearing check, that particle has momentum
            // First, if particle has smearing it has
            // gen_part->has_smear_info == true
            // So if particle is smeared we ask it to have momentum smeared
            if(gen_part->has_smear_info && !particle->smear.has_p) continue;
            
            // Smeared values
            ROOT::Math::PxPyPzMVector p(particle->px, particle->py, particle->pz, particle->m);
            
            // Original values
            ROOT::Math::PxPyPzMVector orig_p(particle->smear.orig_px, particle->smear.orig_py, particle->smear.orig_pz, particle->m);
        
            // Fill histogram   
            h1d_pt->Fill(p.pt());

            if(m_verbose == 2) {
                fmt::print("e E = {:<15}  pt = {:<15}  theta = {:<15.1f} \\n", p.e(), p.pt(), p.theta()*180/3.1415);
            }
        }
    }

    void Finish() override {
        fmt::print("{{class_name}}Processor::Finish(). Cleanup\\n");
    }
};

extern "C" {
    void InitPlugin(JApplication *app) {
        InitJANAPlugin(app);
        app->Add(new {{class_name}}Processor);
    }
}
"""

mini_analysis_cpp = """
#include <JANA/JEventProcessor.h>
#include <JANA/Services/JGlobalRootLock.h>
#include <TH1D.h>
#include <TFile.h>
#include <Math/Vector4D.h>
#include <ejana/MainOutputRootFile.h>
#include <MinimalistModel/McGeneratedParticle.h>
#include <fmt/core.h>


class {{class_name}}Processor: public JEventProcessor {
private:
    std::shared_ptr<ej::MainOutputRootFile> m_file;
    int m_verbose;                /// verbosity level. 0-none, 1-some, 2-all
    TDirectory* m_plugin_dir;     /// Virtual sub-folder inside root file used for this specific plugin

    /// Declare histograms here
    TH1D* h1d_pt;

public:
    explicit {{class_name}}Processor() {
    }

    void Init() override {
        auto app = GetApplication();
        
        // Get main ROOT output file 
        m_file = app->GetService<ej::MainOutputRootFile>();

        // Set parameters that can be controlled from command line
        m_verbose = 1;
        app->SetDefaultParameter("{{plugin_name}}:verbose", m_verbose, "Verbosity level 0=none, 1=some, 2=all");

        if(m_verbose) {
            fmt::print("{{class_name}}Processor::Init()\\n  {{plugin_name}}:verbose={}\\n", m_verbose);
        }

        // Setup histograms
        m_plugin_dir = m_file->mkdir("{{plugin_name}}"); // Create a subdir inside dest_file for these results
        m_plugin_dir->cd();
        h1d_pt = new TH1D("e_pt", "electron pt", 100,0,10);
    }

    void Process(const std::shared_ptr<const JEvent>& event) override {
        // This function is called every event
        if(m_verbose == 2) fmt::print("Begin of event {} \\n", event->GetEventNumber());
                
         
        // Acquire any results you need for your analysis
        auto particles = event->Get<minimodel::McGeneratedParticle>();

        // Go through particles
        for(auto& particle: particles) {

            // select electron
            if(std::abs(particle->pdg) != 11) continue;
            if(particle->charge != -1) continue;
            if(!particle->is_stable) continue; 
            
            ROOT::Math::PxPyPzMVector p(particle->px, particle->py, particle->pz, particle->m);
            h1d_pt->Fill(p.pt());

            if(m_verbose == 2) {
                fmt::print("e E = {:<15}  pt = {:<15}  theta = {:<15.1f} \\n", p.e(), p.pt(), p.theta()*180/3.1415);
            }
        }
    }

    void Finish() override {
        fmt::print("{{class_name}}Processor::Finish(). Cleanup\\n");
    }
};

extern "C" {
    void InitPlugin(JApplication *app) {
        InitJANAPlugin(app);
        app->Add(new {{class_name}}Processor);
    }
}
"""

mini_plugin_python_example = """
# Make sure pyjano is installed in your system
# do:
#     pip install --upgrade pyjano          # for conda, venv or root install
#     pip install --user --upgrade pyjano   # for user local install
#
# Please, wget 
from pyjano.jana import Jana, PluginFromSource

my_plugin = PluginFromSource('./', name='{{plugin_name}}')

jana = Jana(nevents=1000, output='min_ex_output.root')
jana.plugin('lund_reader') \\
    .plugin(my_plugin, verbose=1) \\
    .source('/home/romanov/Downloads/pipi.lund') \\
    .run()
"""

mini_plugin_cmake = """
cmake_minimum_required(VERSION 3.9)

set(PLUGIN_NAME "{{plugin_name}}")

# => ADD Sources here:
set(PLUGIN_SOURCES {{class_name}}.cc )

#   Most of the time you are not interested in lines below
# ==========================================================

project(${PLUGIN_NAME})

set(PLUGIN_TARGET_NAME "${PLUGIN_NAME}_plugin")
add_library(${PLUGIN_TARGET_NAME} SHARED ${PLUGIN_SOURCES})

find_package(ROOT)

# ============ FIND JANA ===============
include(FindPackageHandleStandardArgs)

#  TODO it will be replaced when JANAConfig.cmake is finalized
if (DEFINED JANA_HOME)
    set(JANA_ROOT_DIR ${JANA_HOME})
    message(STATUS "Using JANA_HOME = ${JANA_ROOT_DIR} (From CMake JANA_HOME variable)")
elseif (DEFINED ENV{JANA_HOME})
    set(JANA_ROOT_DIR $ENV{JANA_HOME})
    message(STATUS "Using JANA_HOME = ${JANA_ROOT_DIR} (From JANA_HOME environment variable)")
else()
    message(FATAL_ERROR "Missing $JANA_HOME")
endif()

set(JANA_VERSION 2)
find_path(JANA_INCLUDE_DIR NAMES "JANA/JApplication.h" PATHS ${JANA_ROOT_DIR}/include)
find_library(JANA_LIBRARY NAMES "JANA" PATHS ${JANA_ROOT_DIR}/lib)
set(JANA_LIBRARIES ${JANA_LIBRARY})
set(JANA_INCLUDE_DIRS ${JANA_ROOT_DIR}/include)
find_package_handle_standard_args(JANA FOUND_VAR JANA_FOUND VERSION_VAR JANA_VERSION REQUIRED_VARS JANA_ROOT_DIR JANA_INCLUDE_DIR JANA_LIBRARY)

# ============ FIND EJANA ===============
#  TODO it will be replaced when EJANAConfig.cmake is finalized
if (DEFINED EJANA_HOME)
    set(EJANA_ROOT_DIR ${EJANA_HOME})
    message(STATUS "Using EJANA_HOME = ${EJANA_ROOT_DIR} (From CMake EJANA_HOME variable)")
elseif (DEFINED ENV{EJANA_HOME})
    set(EJANA_ROOT_DIR $ENV{EJANA_HOME})
    message(STATUS "Using EJANA_HOME = ${EJANA_ROOT_DIR} (From EJANA_HOME environment variable)")
else()
    message(FATAL_ERROR "Missing $EJANA_HOME")
endif()

set(EJANA_VERSION 1)
find_path(EJANA_INCLUDE_DIR NAMES "ejana/EJanaRootApplication.h" PATHS ${EJANA_ROOT_DIR}/include)
find_library(EJANA_LIBRARY NAMES "ejana" PATHS ${EJANA_ROOT_DIR}/lib)
find_library(EJANA_FMT_LIBRARY NAMES "ejana_fmt" PATHS ${EJANA_ROOT_DIR}/lib)
set(EJANA_LIBRARIES ${EJANA_LIBRARY})
set(EJANA_INCLUDE_DIRS ${EJANA_ROOT_DIR}/include)

find_package_handle_standard_args(EJANA FOUND_VAR EJANA_FOUND VERSION_VAR EJANA_VERSION REQUIRED_VARS EJANA_ROOT_DIR EJANA_INCLUDE_DIR EJANA_LIBRARY EJANA_FMT_LIBRARY)

target_include_directories(${PLUGIN_TARGET_NAME} PUBLIC ${JANA_INCLUDE_DIR} ${ROOT_INCLUDE_DIRS} ${EJANA_INCLUDE_DIR})
target_link_libraries(${PLUGIN_TARGET_NAME} ${JANA_LIB} ${ROOT_LIBRARIES} ${EJANA_FMT_LIBRARY} ${EJANA_LIBRARY})
set_target_properties(${PLUGIN_TARGET_NAME} PROPERTIES PREFIX "" OUTPUT_NAME "${PLUGIN_NAME}" SUFFIX ".so")
install(TARGETS ${PLUGIN_TARGET_NAME} LIBRARY DESTINATION "./")
"""

mini_plugin_gitignore = """
# usual build dir
cmake-build-debug/
compile/
cmake-build/

# resulting plugin
{{plugin_name}}.so

# resulting files
*.root

# IntelliJ IDEs dir
.idea/
"""

mini_plugin_readme = """

# {{plugin_name}}

## Python

Look at [pyjano_example.py](pyjano_example.py) to see the code.

**pyjano** automatically setups everything and re/builds a plugin when the code is changed. 


## Manual build and run from command line:

1. Build:

```bash
cd {{plugin_name}}
mkdir build && cd build
cmake ../
make
```

2. Jana searches compiled plugins using JANA_PLUGIN_PATH environment variable or in the current directory. 
Make sure you are running ejana where resulting .so file is located or set JANA_PLUGIN_PATH

3. Run 
```bash
ejana 
-Pplugins={{plugin_name}},hepmc_reader,open_charm
-Popen_charm:verbose=0
-Popen_charm:e_beam_energy=18
-Popen_charm:ion_beam_energy=275
-Pjana:DEBUG_PLUGIN_LOADING=1
<source >.hepmc
```
"""


def generate_mini_analysis_plugin(plugin_name, class_name, path=""):
    """Generates mini plugin"""
    plugin_dir = os.path.join(path, plugin_name) if path else plugin_name
    os.makedirs(plugin_dir, exist_ok=False)

    # Cmake file lists
    with open(os.path.join(plugin_dir, r"CMakeLists.txt"), "w+") as f:
        f.write(mini_plugin_cmake
                .replace("{{plugin_name}}", plugin_name)
                .replace("{{class_name}}", class_name))

    with open(os.path.join(plugin_dir, class_name+".cc"), "w+") as f:
        f.write(mini_analysis_cpp
                .replace("{{plugin_name}}", plugin_name)
                .replace("{{class_name}}", class_name))

    with open(os.path.join(plugin_dir, "python_example.py"), "w+") as f:
        f.write(mini_plugin_python_example
                .replace("{{plugin_name}}", plugin_name)
                .replace("{{class_name}}", class_name))

    with open(os.path.join(plugin_dir, ".gitignore"), "w+") as f:
        f.write(mini_plugin_gitignore
                .replace("{{plugin_name}}", plugin_name)
                .replace("{{class_name}}", class_name))

    with open(os.path.join(plugin_dir, "README.md"), "w+") as f:
        f.write(mini_plugin_readme
                .replace("{{plugin_name}}", plugin_name)
                .replace("{{class_name}}", class_name))

    return plugin_dir


