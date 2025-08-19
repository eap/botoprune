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

from botoprune._implementation import whitelist_prune_services, BotoPruneError
import sys


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog='python -m botoprune.whitelist',
        description='Prune botocore data to only include the specified services.',
    )
    # Positional arguments are a list of services to keep separated by spaces
    parser.add_argument(
        'keep_services',
        nargs='+',
        help='List of AWS services to keep in botocore data.',
    )
    parser.add_argument(
        '--dry-run',
        default=False,
        action=argparse.BooleanOptionalAction,
        help='Do not actually delete any services, just print what would be deleted.',
    )

    args = parser.parse_args()

    try:
        kept_services, pruned_services = whitelist_prune_services(
            whitelist_targets=args.keep_services,
            dry_run=args.dry_run,
        )
    except BotoPruneError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

    # Print summary.
    dry_run_str = ''
    if args.dry_run:
        dry_run_str = '(DRY RUN, NO SERVICES DELETED) '
    print(f'{dry_run_str}Deleted {len(pruned_services)} service definitions, '
          f'Kept services {repr(kept_services)}')

    # Exit with success code.
    sys.exit(0)
