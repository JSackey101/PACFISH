# BSD 3-Clause License
#
# Copyright (c) 2020, IPASC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
File converter/adapter
Converts into IPASC HDF5 format

Lawson Optics Lab
Lawson Health Research Institute
Western University
London, ON, Canada

Created by: Lawrence Yip
Last Modified 2020-09-25
"""
import numpy as np


from ipasc_tool import BaseAdapter, MetaDatum
from ipasc_tool import MetadataAcquisitionTags
from ipasc_tool import DeviceMetaDataCreator, DetectionElementCreator, IlluminationElementCreator
# from ipasc_tool import read_LOL_import_module
from ipasc_tool.api.adapters.LawsonOptics import read_LOL_import_module


class LOLFileConverter(BaseAdapter):

    def __init__(self, raw_data_folder_path, scan_log_file_path, signal_inv=True, left_shift=12,
                 thresholding=0, photodiode=65, CheckAveraging=True, end_remove=80):
        super().__init__() 
        self.raw_data_folder_path = raw_data_folder_path
        self.scan_log_file_path = scan_log_file_path
        self.signal_inv = signal_inv
        self.left_shift = left_shift
        self.thresholding = thresholding
        self.photodiode = photodiode
        self.CheckAveraging = CheckAveraging
        self.end_remove = end_remove
        
        
        

    def generate_binary_data(self) -> np.ndarray:
        return self.data

    def generate_meta_data_device(self) -> dict:
        device_creator = DeviceMetaDataCreator()

        device_creator.set_general_information(uuid="97cc5c0d-2a83-4935-9820-2aa2161ff703",
                                               fov=np.asarray([0, 0.0500, 0.0500]))

        all_positions, time_taken = read_LOL_import_module.load_scan_log(self.scan_log_file_path)
        all_positions_metres = all_positions/1000
        

        for scan_position in range(np.shape(all_positions)[2]):
            for detector_position in range(np.shape(all_positions)[0]):
                
                detection_element_creator = DetectionElementCreator()
                detection_element_creator.set_detector_position(all_positions_metres[detector_position,0:3,scan_position])
                orientation = findVec(all_positions_metres[detector_position, 0:3, scan_position],all_positions_metres[detector_position, 3:6, scan_position], unitSphere = True)
                detection_element_creator.set_detector_orientation(np.asarray(orientation))
                detection_element_creator.set_detector_size(np.asarray([0.0127, 0.0127, 0.0001]))
                # detection_element_creator.set_frequency_response(np.stack([np.linspace(700, 900, 100),
                #                                                            np.ones(100)]))
                # detection_element_creator.set_angular_response(np.stack([np.linspace(700, 900, 100),
                #                                                          np.ones(100)]))
    
                device_creator.add_detection_element("detection_element_scan" + str(scan_position) + "_detector" = str(detector_position)),
                                                     detection_element_creator.get_dictionary())

        for y_idx in range(2):
            # illumination_element_creator = IlluminationElementCreator()
            # illumination_element_creator.set_beam_divergence_angles(0.20944)
            # illumination_element_creator.set_wavelength_range(np.asarray([700, 950, 1]))
            # if y_idx == 0:
            #     illumination_element_creator.set_illuminator_position(np.asarray([0.0083, 0.0192, -0.001]))
            #     illumination_element_creator.set_illuminator_orientation(np.asarray([0, -0.383972, 0]))
            # elif y_idx == 1:
            #     illumination_element_creator.set_illuminator_position(np.asarray([-0.0083, 0.0192, -0.001]))
            #     illumination_element_creator.set_illuminator_orientation(np.asarray([0, 0.383972, 0]))
            # illumination_element_creator.set_illuminator_shape(np.asarray([0, 0.0245, 0]))

            # illumination_element_creator.set_laser_energy_profile(np.stack([np.linspace(700, 900, 100),
            #                                                                 np.ones(100)]))
            # illumination_element_creator.set_laser_stability_profile(np.stack([np.linspace(700, 900, 100),
            #                                                                    np.ones(100)]))
            # illumination_element_creator.set_pulse_width(7e-9)
            # device_creator.add_illumination_element("illumination_element_" + str(y_idx),
            #                                         illumination_element_creator.get_dictionary())

        return device_creator.finalize_device_meta_data()

    def set_metadata_value(self, metadata_tag: MetaDatum) -> object:
        if metadata_tag == MetadataAcquisitionTags.UUID:
            return "TestUUID"
        elif metadata_tag == MetadataAcquisitionTags.DATA_TYPE:
            return self.meta['type']
        elif metadata_tag == MetadataAcquisitionTags.AD_SAMPLING_RATE:
            return float(self.meta['space directions'][1][1]) / 50000000
        elif metadata_tag == MetadataAcquisitionTags.ACOUSTIC_COUPLING_AGENT:
            return "Water"
        elif metadata_tag == MetadataAcquisitionTags.ACQUISITION_OPTICAL_WAVELENGTHS:
            return np.asarray([700])
        elif metadata_tag == MetadataAcquisitionTags.COMPRESSION:
            return "None"
        elif metadata_tag == MetadataAcquisitionTags.DIMENSIONALITY:
            return "3D"
        elif metadata_tag == MetadataAcquisitionTags.ENCODING:
            return "raw"
        elif metadata_tag == MetadataAcquisitionTags.SCANNING_METHOD:
            return "Robotic"
        elif metadata_tag == MetadataAcquisitionTags.PHOTOACOUSTIC_IMAGING_DEVICE:
            return "97cc5c0d-2a83-4935-9820-2aa2161ff703"
        elif metadata_tag == MetadataAcquisitionTags.SIZES:
            return np.asarray(self.meta['sizes'])
        else:
            return None
