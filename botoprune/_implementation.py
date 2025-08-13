# Copyright 2025 Evan A. Parker
#
# Distributed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import botocore
import os
import shutil
from collections import defaultdict

try:
    import botocore.data as botocore_data
except ImportError:
    botocore_data = None


class BotoPruneError(Exception):
    """Base class for botoprune errors."""
    pass


def list_installed_botocore_services():
    """Returns a tuple of (botocore data directory, sorted list of botocore services)."""
    # Accessing the data directory for botocore can differ between versions and
    # installation methods. This casts a wide net but may still fail in some cases.
    if botocore_data:
        data_dir = botocore_data.__path__[0]
    else:
        data_dir = os.path.join(os.path.dirname(botocore.__file__), "data")

    # Check if the directory exists. Raises FileNotFoundError if the directory does not exist.
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Botoprune: Botocore data directory not found: {data_dir}.")
    services = os.listdir(data_dir)
    if not services:
        raise FileNotFoundError(f"Botoprune: No services found in {data_dir}.")

    # Filter out any files, only keep directories
    filtered_services = []
    for service in services:
        if os.path.isdir(os.path.join(data_dir, service)):
            filtered_services.append(service)
    return data_dir, sorted(filtered_services)


def remove_services(remove_targets: list[str], dry_run: bool):
    """Remove botocore data for the specified services.

    Args:
        remove_targets: List of services to remove.
        dry_run: If set to true, then do not actually delete any services, just
                 print what would be deleted.

    Returns:
        A 2-tuple of the following values:
        - List of services that were kept.
        - List of services that were removed.
    """
    data_dir, botocore_services = list_installed_botocore_services()

    # Check that all remove targets are in botocore.
    remove_failures = [s for s in remove_targets if s not in botocore_services]
    if remove_failures:
        raise BotoPruneError(f'botoprune.remove services {repr(remove_failures)}'
                             ' not found in botocore.')

    # Remove the targeted services. This is done sort of "backwards" by evaluating the list of
    # all services even though we already know the list of services to remove because it allows
    # us to save the list of services that were kept.
    kept_services = []
    removed_services = []
    for service in botocore_services:
        if service in remove_targets:
            if not dry_run:
                shutil.rmtree(os.path.join(data_dir, service))
            removed_services.append(service)
        else:
            kept_services.append(service)

    return kept_services, removed_services


def whitelist_prune_services(whitelist_targets: list[str], keep_prefix: bool, dry_run: bool):
    """Prune botocore data to only include the specified services.

    Args:
        whitelist_targets: List of services to keep.
        keep_prefix: If set to true, then any whitelisted service will also
                     whitelist services with the same prefix. For example s3
                     would transitively whitelist s3control, s3outposts, etc.
        dry_run: If set to true, then do not actually delete any services, just
                 print what would be deleted.

    Returns:
        A 2-tuple of the following values:
        - List of services that were kept.
        - List of services that were removed.
    """
    data_dir, botocore_services = list_installed_botocore_services()

    # Create dict to find prefix whitelisted services. This takes advantage of
    # the alphabetical ordering of the services to create a dictionary of
    # services with the same prefix.
    if keep_prefix:
        prefix_whitelist = defaultdict(list)
        for i in range(len(botocore_services)):
            service_prefix = botocore_services[i]
            j = i + 1
            while j < len(botocore_services) and botocore_services[j].startswith(service_prefix):
                prefix_whitelist[service_prefix].append(botocore_services[j])
                j += 1
    else:
        prefix_whitelist = {}

    # Create set of services to keep including transitive whitelist members.
    full_whitelist = list(whitelist_targets)
    for service in whitelist_targets:
        if service in prefix_whitelist:
            full_whitelist.extend(prefix_whitelist[service])
    full_whitelist = set(full_whitelist)

    # Set of services that were whitelisted but not found in botocore.
    whitelist_failures = [s for s in full_whitelist if s not in botocore_services]
    if whitelist_failures:
        raise BotoPruneError(f'botoprune.whitelist services {repr(whitelist_failures)}'
                             ' not found in botocore.')

    # Prune botocore data.
    removed_services = []
    for service in botocore_services:
        if service not in full_whitelist:
            if not dry_run:
                shutil.rmtree(os.path.join(data_dir, service))
            removed_services.append(service)

    # Note that all whitelist services are already verified to be in botocore.
    kept_services = sorted(list(full_whitelist))
    return kept_services, removed_services
