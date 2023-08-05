# Protocol Buffer structure for Speos
Python package containing protocol buffer structure for Speos APIs.
## Directory structure
    - ansys
        |---- api
        |       |---- speos
        |       |       |-- api-example1
        |       |       |       |-- v1
        |       |       |       |   |-- service1_pb2.py
        |       |       |       |   |-- service1_pb2_grpc.py
        |       |       |       |   |-- service2_pb2.py
        |       |       |       |   |-- service2_pb2_grpc.py
        |       |       |       |-- v2
        |       |       |       |   |-- service2_pb2.py
        |       |       |       |   |-- service2_pb2_grpc.py

## What's new
### 4.1.0

### 4.1.0
* `simulation` - service to create, delete, open, save, run multiple .speos simulation
`simulation API v1` available in *ansys/api/speos/simulation/v1*

With the following services:
 * `SpeosSimulationsManager` - Service to manage (create, delete, list, serialize) Speos Simulations
 * `SpeosSimulation` - Service to load, save, get name, run, get results paths of a Speos Simulation
 * `SpeosSimulationRunFromFile` - Service that concatenate load and run of a .speos file

### 4.0.0
`lpf API v1` expansion in *ansys/api/speos/lpf/v1*

New information in RayPath : sensor_contributions
New rpc : GetInformation to retrieve number_of_xmps, number_of_traces, has_sensor_contributions, sensor_names

### 3.1.0
`file API v1` available in *ansys/api/speos/file/v1*

With the following service:
* `file_transfer` - service to transfer file

### 3.0.0
`gRPC` update to version 1.46.3

### 2.0.0
`LTF API v1` expansion in *ansys/api/speos/LTF/v1*

With the addition of spectral dependency

### 1.0.0
`LTF API v1` available in *ansys/api/speos/LTF/v1*

With the following service:
* `LTF` - service to create, open, modify and save *.OPTDistortion files


`lpf API v1` available in *ansys/api/speos/lpf/v1*

With the following service:
 * `lpf_file_reader` - service to read lpf file and get all its RayPath


`xmp API v1` available in *ansys/api/speos/xmp/v1*

With the following service:
 * `xmp_file` - service to manage xmp file


`bsdf API v1` available in *ansys/api/speos/bsdf/v1*

With the following services:
 * `anisotropic_bsdf` - service to create, open, modify and save *.anisotropicbsdf files
 * `bsdf_creation` - service to create, open, modify and save *.brdf files
 * `spectral_bsdf` - service to assemble *.anisotropicbsdf or *.brdf files into .bsdf180 files<br/>
   or isotropic *.anisotropicbsdf to anisotropic *.anisotropicbsdf files<br/>
   or isotropic *.anisotropicbsdf to spectral *.brdf files

