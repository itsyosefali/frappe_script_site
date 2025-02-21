import os
import pexpect
import sys
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("HOST")
ssh_password = os.getenv("SSH_PASSWORD")
bench_path = os.getenv("BENCH_PATH", "~/erp15")
site_name = os.getenv("SITE_NAME")
backup_source = os.getenv("BACKUP_SOURCE")
db_root_password = os.getenv("DB_ROOT_PASSWORD")
files = os.getenv("FILES", "")

restore_commands = (
    f"cd {bench_path} && "
    f"if [ ! -d sites/{site_name} ]; then "
        f"bench new-site {site_name} --db-root-password {db_root_password} --admin-password 123; "
    f"else "
        f"echo \"[DEBUG] Site {site_name} already exists, skipping site creation\"; "
    f"fi && "
    f"latest_db=$(ls -t {backup_source}/*-database.sql.gz 2>/dev/null | head -1) && "
    f"latest_files=$(ls -t {backup_source}/*-files.tar 2>/dev/null | grep -v 'private' | head -1) && "
    f"latest_private=$(ls -t {backup_source}/*-private-files.tar 2>/dev/null | head -1) && "
    f"echo \"[DEBUG] Selected backups: DB='$latest_db', Files='$latest_files', Private='$latest_private'\" && "
    f"if [ -z \"$latest_db\" ]; then "
        f"echo \"[ERROR] No backup file found in {backup_source}\" && exit 1; "
    f"fi && "
    f"if [ -n \"$latest_files\" ]; then "
        f"bench --site {site_name} restore $latest_db --force --db-root-password {db_root_password}; "
    f"else "
        f"bench --site {site_name} restore $latest_db --force --db-root-password {db_root_password}; "
    f"fi && "
    f"sudo -H bench setup lets-encrypt {site_name}"  
)

ssh_command = f"sshpass -p '{ssh_password}' ssh -t -o StrictHostKeyChecking=no {host} \"{restore_commands}\""

print("🚀 Starting restore process...\n")

child = pexpect.spawn(ssh_command, encoding='utf-8', timeout=3600)
child.logfile = sys.stdout

patterns = [
    r"\[sudo\] password for .*:",
    "Do you want to continue?",    
    "nginx.conf already exists and this will overwrite it. Do you want to continue?",
    pexpect.EOF
]

try:
    while True:
        index = child.expect(patterns)
        if index == 0:
            print("\n🔑 Detected sudo prompt. Sending password...")
            child.sendline(ssh_password)
        elif index == 1:
            print("\n✅ Confirming prompt with 'y'...")
            child.sendline("y")
        elif index == 2:
            print("\n✅ Confirming nginx prompt with 'y'...")
            child.sendline("y")
        elif index == 3:
            break

except pexpect.TIMEOUT:
    print("\n⌛ Timeout: The process took too long.")
except Exception as e:
    print(f"\n⚠️ Unexpected error: {str(e)}")

print("\n🔌 Session closed")
