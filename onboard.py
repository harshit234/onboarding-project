"""Developer onboarding script to validate environment setup."""

import sys
import time
import argparse
import shutil
import os
import subprocess
from importlib import metadata # standard library

import requests

REPORT = []


def check_python_version():
    """Check Python version >= 3.10"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        return True, f"{version.major}.{version.minor}"
    return False, f"{version.major}.{version.minor}"


def check_virtual_env():
    """Check if running in virtual environment (Windows friendly)"""
    if "VIRTUAL_ENV" in os.environ:
        return True, os.environ["VIRTUAL_ENV"]
    return False, "Not in virtual env"


def check_disk_space():
    """Check if free disk space is at least 1GB"""
    total, used, free = shutil.disk_usage("/")
    if free < 1e9:
        return False, f"Low disk space: {round(free / 1e9, 2)} GB"
    return True, f"Free space: {round(free / 1e9, 2)} GB"


def check_package_installed(package_name):
    """Check if package is installed"""
    try:
        metadata.version(package_name)
        return True
    except metadata.PackageNotFoundError:
        return False


def check_internet():
    """Check internet connectivity"""
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def run_check(name, func, verbose=False):
    """Run check and measure time"""
    if verbose:
        print(f"Running check: {name}")

    start = time.time()
    status, info = func()
    end = time.time()

    result = "[PASS]" if status else "[FAIL]"
    msg = f"{result} {name}: {info} ({round(end - start, 2)}s)"
    REPORT.append(msg)
    print(msg)

    return status


def save_report():
    """Save report to file"""
    with open("setup_report.txt", "w", encoding="utf-8") as file:
        file.write("=== Developer Onboarding Check ===\n\n")
        for line in REPORT:
            file.write(line + "\n")
    print("Report saved to setup_report.txt")


def install_package(package_name):
    """Install package using pip"""
    print(f"[FIX] Installing {package_name}...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", package_name],
        check=False,
    )


def main():
    """Main execution function"""

    parser = argparse.ArgumentParser(description="Developer Onboarding Script")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--fix", action="store_true", help="Install missing packages"
    )

    args = parser.parse_args()

    print("=== Developer Onboarding Check ===")

    start_time = time.time()

    total = 0
    passed = 0

    # Core checks
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("Disk Space", check_disk_space),
    ]

    for name, func in checks:
        total += 1
        if run_check(name, func, args.verbose):
            passed += 1

    # Package checks
    for pkg in ["pylint", "black", "numpy", "requests"]:
        total += 1
        status = check_package_installed(pkg)

        if not status and args.fix:
            install_package(pkg)
            status = check_package_installed(pkg)

        msg = f"[{'PASS' if status else 'FAIL'}] {pkg} installed"
        print(msg)
        REPORT.append(msg)

        if status:
            passed += 1

    # Internet check
    total += 1
    if check_internet():
        print("[PASS] Internet connectivity: OK")
        REPORT.append("[PASS] Internet connectivity: OK")
        passed += 1
    else:
        print("[FAIL] Internet connectivity")
        REPORT.append("[FAIL] Internet connectivity")

    print("\n---")
    print(f"Result: {passed}/{total} checks passed")

    end_time = time.time()
    print(f"Total Execution Time: {round(end_time - start_time, 2)} seconds")

    save_report()


if __name__ == "__main__":
    main()
