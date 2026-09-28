import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_project.settings')
    try:
        import django
        django.setup()
        from django.core.management import call_command
        
        print("Making migrations for accounts and transactions...")
        call_command('makemigrations', 'accounts')
        call_command('makemigrations', 'transactions')
        
        print("Applying migrations to database...")
        call_command('migrate')
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
