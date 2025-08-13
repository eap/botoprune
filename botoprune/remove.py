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

from botoprune._implementation import remove_services, BotoPruneError
import sys


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog='python -m botoprune.remove',
        description='Remove specified API definitions from botocore data.',
    )
    # Positional arguments are a list of services to keep separated by spaces
    parser.add_argument(
        'remove_targets',
        nargs='+',
        help='List of AWS services to remove from botocore data.',
    )
    parser.add_argument(
        '--dry-run',
        default=False,
        action=argparse.BooleanOptionalAction,
        help='Do not actually delete any services, just print what would be deleted.',
    )

    args = parser.parse_args()

    try:
        kept_services, removed_services = remove_services(
            remove_targets=args.remove_targets,
            dry_run=args.dry_run,
        )
    except BotoPruneError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

    # Print summary.
    dry_run_str = ''
    if args.dry_run:
        dry_run_str = '(DRY RUN, NO SERVICES DELETED) '
    print(f'{dry_run_str}Deleted service definitions {repr(removed_services)}, '
          f'Kept {len(kept_services)} services')

    # Exit with success code.
    sys.exit(0)
