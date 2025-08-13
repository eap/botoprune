"""Tests for botoprune."""

import os
import pytest
import unittest

import botoprune._implementation as implementation


class TestBotoprune(unittest.TestCase):

    def test_list_installed_botocore_services(self):
        data_dir, services = implementation.list_installed_botocore_services()
        self.assertTrue(os.path.exists(data_dir))
        # Sanity check, the list of services should be non-empty and should contain
        # some well-known AWS services.
        self.assertTrue(len(services) > 100)
        self.assertIn('s3', services)
        self.assertIn('s3control', services)
        self.assertIn('ec2', services)
    
    def test_remove_services(self):
        targets = ['s3', 's3control', 'ec2']
        targets_check = [t for t in targets]
        kept, removed = implementation.remove_services(
            remove_targets=targets,
            dry_run=True,
        )
        self.assertCountEqual(removed, targets_check)
        self.assertNotIn('s3', kept)
        self.assertNotIn('s3control', kept)
        self.assertNotIn('ec2', kept)

    def test_whitelist_prune_services_prefix(self):
        whitelist = ['s3', 's3control', 'ec2']
        whitelist_check = [t for t in whitelist] + ['ec2-instance-connect', 's3outposts', 's3tables', 's3vectors']
        kept, removed = implementation.whitelist_prune_services(
            whitelist_targets=whitelist,
            keep_prefix=True,
            dry_run=True,
        )
        self.assertCountEqual(kept, whitelist_check)
    
    def test_whitelist_prune_services_no_prefix(self):
        whitelist = ['s3', 's3control', 'ec2']
        whitelist_check = [t for t in whitelist]
        kept, removed = implementation.whitelist_prune_services(
            whitelist_targets=whitelist,
            keep_prefix=False,
            dry_run=True,
        )
        self.assertCountEqual(kept, whitelist_check)
    
    @pytest.mark.destructive
    def test_whitelist_prune_services_destructive(self):
        """Run this test with the `pytest -m destructive`, note it will delete botocore data."""
        # Initial read on services
        _, services = implementation.list_installed_botocore_services()
        service_count = len(services)
        self.assertTrue(service_count > 100)

        # Prune services using a whitelist without prefix expansion.
        whitelist = ['s3', 's3control', 'ec2']
        whitelist_check = [t for t in whitelist]
        kept, removed = implementation.whitelist_prune_services(
            whitelist_targets=whitelist,
            keep_prefix=False,
            dry_run=False,
        )
        self.assertCountEqual(kept, whitelist_check)

        # Check that the services were actually removed.
        _, services = implementation.list_installed_botocore_services()
        self.assertTrue(len(services) == 3)
        self.assertCountEqual(services, whitelist_check)