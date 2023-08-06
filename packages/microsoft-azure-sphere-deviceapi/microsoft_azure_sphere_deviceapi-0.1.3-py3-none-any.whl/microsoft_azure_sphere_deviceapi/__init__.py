# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
__version__ = version = '0.1.3'
__version_tuple__ = version_tuple = (0, 1, 3)

import warnings

warnings.warn(
    "The 'microsoft_azure_sphere_deviceapi' package is deprecated and should not be used. Please import from 'azuresphere_device_api' package instead. If 'azuresphere_device_api' is not importable run 'pip install azuresphere-device-api'.")
