import os
import sys

os.environ['IS_TESTING'] = 'True'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yaksync_project.settings')

import django
django.setup()

from django.core.management import call_command

print("1. Running django system check...")
try:
    call_command('check')
    print("SUCCESS: Django system check completed successfully!")
except Exception as e:
    print(f"FAILED: Django system check failed: {e}")
    sys.exit(1)

print("\n2. Checking migrations (makemigrations)...")
try:
    call_command('makemigrations', dry_run=True)
    print("SUCCESS: Migrations check dry-run completed successfully!")
except Exception as e:
    print(f"FAILED: Migrations dry-run failed: {e}")
    sys.exit(1)

print("\n3. Running ALL unit tests...")
try:
    failures = call_command('test', interactive=False)
    if failures:
        print(f"FAILED: Tests had {failures} failure(s)!")
        sys.exit(failures)
    else:
        print("SUCCESS: All unit tests passed successfully!")
except Exception as e:
    print(f"FAILED: Test execution encountered an error: {e}")
    sys.exit(1)

print("\nAll checks completed successfully!")
