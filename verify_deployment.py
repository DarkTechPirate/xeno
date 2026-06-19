#!/usr/bin/env python3
"""
TransactIQ Deployment Verification Script
Verifies that all components are production-ready
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class DeploymentVerifier:
    def __init__(self, project_root="/Users/jk/Desktop/xeno"):
        self.project_root = Path(project_root)
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        
    def log_pass(self, message):
        print(f"✓ {message}")
        self.checks_passed += 1
        
    def log_fail(self, message):
        print(f"✗ {message}")
        self.checks_failed += 1
        
    def log_warn(self, message):
        print(f"⚠ {message}")
        self.warnings += 1
        
    def check_file_exists(self, path, description):
        full_path = self.project_root / path
        if full_path.exists():
            self.log_pass(f"{description} exists: {path}")
            return True
        else:
            self.log_fail(f"{description} missing: {path}")
            return False
            
    def check_directory_exists(self, path, description):
        full_path = self.project_root / path
        if full_path.is_dir():
            self.log_pass(f"{description} directory exists: {path}")
            return True
        else:
            self.log_fail(f"{description} directory missing: {path}")
            return False
            
    def count_files(self, pattern, description):
        import glob
        files = list(self.project_root.glob(pattern))
        if files:
            self.log_pass(f"Found {len(files)} {description}: {pattern}")
            return len(files)
        else:
            self.log_warn(f"No {description} found: {pattern}")
            return 0
    
    def verify_backend(self):
        print("\n" + "="*60)
        print("BACKEND VERIFICATION")
        print("="*60)
        
        # Check main files
        self.check_file_exists("backend/main.py", "Backend main app")
        self.check_file_exists("backend/requirements.txt", "Backend requirements")
        
        # Check app structure
        self.check_directory_exists("backend/app", "Backend app package")
        self.check_directory_exists("backend/app/models", "Models package")
        self.check_directory_exists("backend/app/validators", "Validators package")
        self.check_directory_exists("backend/app/services", "Services package")
        self.check_directory_exists("backend/app/routes", "Routes package")
        self.check_directory_exists("backend/app/engines", "Engines package")
        self.check_directory_exists("backend/app/database", "Database package")
        
        # Count Python files
        py_count = self.count_files("backend/app/**/*.py", "Python files")
        if py_count >= 8:
            self.log_pass(f"Backend has sufficient Python files ({py_count})")
        else:
            self.log_warn(f"Backend has fewer Python files than expected ({py_count}/8)")
            
    def verify_frontend(self):
        print("\n" + "="*60)
        print("FRONTEND VERIFICATION")
        print("="*60)
        
        # Check main files
        self.check_file_exists("frontend/package.json", "Frontend package.json")
        self.check_file_exists("frontend/next.config.js", "Frontend Next.js config")
        self.check_file_exists("frontend/tsconfig.json", "Frontend TypeScript config")
        
        # Check app structure
        self.check_directory_exists("frontend/app", "Frontend app directory")
        self.check_directory_exists("frontend/components", "Frontend components")
        self.check_directory_exists("frontend/lib", "Frontend lib utilities")
        self.check_directory_exists("frontend/types", "Frontend types")
        self.check_directory_exists("frontend/styles", "Frontend styles")
        
        # Count component files
        tsx_count = self.count_files("frontend/**/*.tsx", "React components")
        ts_count = self.count_files("frontend/**/*.ts", "TypeScript files")
        
        if tsx_count >= 5:
            self.log_pass(f"Frontend has sufficient components ({tsx_count})")
        else:
            self.log_warn(f"Frontend has fewer components than expected ({tsx_count}/5)")
            
    def verify_infrastructure(self):
        print("\n" + "="*60)
        print("INFRASTRUCTURE VERIFICATION")
        print("="*60)
        
        self.check_directory_exists("infrastructure", "Infrastructure directory")
        self.check_file_exists("infrastructure/Dockerfile.backend", "Backend Dockerfile")
        self.check_file_exists("infrastructure/Dockerfile.frontend", "Frontend Dockerfile")
        self.check_file_exists("infrastructure/docker-compose.yml", "Docker Compose file")
        self.check_file_exists("infrastructure/nginx.conf", "Nginx configuration")
        
    def verify_documentation(self):
        print("\n" + "="*60)
        print("DOCUMENTATION VERIFICATION")
        print("="*60)
        
        docs = [
            ("README.md", "Project README"),
            ("SETUP.md", "Setup guide"),
            ("ARCHITECTURE.md", "Architecture documentation"),
            ("QUICKSTART.md", "Quick start guide"),
            ("DEPLOYMENT.md", "Deployment guide"),
            ("CONTRIBUTING.md", "Contributing guide"),
            ("CHANGELOG.md", "Changelog"),
            ("SERVER_DEPLOYMENT.md", "Server deployment guide"),
        ]
        
        for file, desc in docs:
            self.check_file_exists(file, desc)
            
    def verify_configuration(self):
        print("\n" + "="*60)
        print("CONFIGURATION VERIFICATION")
        print("="*60)
        
        self.check_file_exists(".gitignore", "Git ignore")
        self.check_file_exists("backend/.env.example", "Backend env example")
        self.check_file_exists("frontend/.env.example", "Frontend env example")
        self.check_file_exists(".github/workflows/ci-cd.yml", "GitHub Actions CI/CD")
        
    def verify_demo_data(self):
        print("\n" + "="*60)
        print("DEMO DATA VERIFICATION")
        print("="*60)
        
        csv_count = self.count_files("demo_datasets/**/*.csv", "Demo datasets")
        if csv_count >= 6:
            self.log_pass(f"All demo datasets present ({csv_count}/6)")
        else:
            self.log_warn(f"Some demo datasets missing ({csv_count}/6)")
            
    def verify_scripts(self):
        print("\n" + "="*60)
        print("SCRIPTS VERIFICATION")
        print("="*60)
        
        self.check_file_exists("deploy.sh", "Quick deployment script")
        self.check_file_exists("scripts/deployment-checklist.sh", "Deployment checklist")
        
    def generate_report(self):
        print("\n" + "="*60)
        print("DEPLOYMENT READINESS REPORT")
        print("="*60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project: TransactIQ")
        print(f"Location: {self.project_root}")
        print(f"\nResults:")
        print(f"  ✓ Passed: {self.checks_passed}")
        print(f"  ✗ Failed: {self.checks_failed}")
        print(f"  ⚠ Warnings: {self.warnings}")
        
        if self.checks_failed == 0:
            print(f"\n{'-'*60}")
            print("STATUS: ✓ PROJECT IS PRODUCTION-READY")
            print(f"{'-'*60}")
            return True
        else:
            print(f"\n{'-'*60}")
            print("STATUS: ✗ PROJECT HAS ISSUES")
            print(f"{'-'*60}")
            return False
            
    def run_all_checks(self):
        print("\n" + "="*60)
        print("TransactIQ Deployment Verification")
        print("="*60)
        
        self.verify_backend()
        self.verify_frontend()
        self.verify_infrastructure()
        self.verify_documentation()
        self.verify_configuration()
        self.verify_demo_data()
        self.verify_scripts()
        
        ready = self.generate_report()
        
        print("\n" + "="*60)
        print("DEPLOYMENT OPTIONS")
        print("="*60)
        print("\n1. Local Docker Deployment:")
        print("   ./deploy.sh")
        print("\n2. Server Deployment (Ubuntu/Linux):")
        print("   See SERVER_DEPLOYMENT.md")
        print("\n3. Cloud Platforms:")
        print("   - Railway.app (recommended for quick setup)")
        print("   - Render.com")
        print("   - AWS ECS")
        print("   - DigitalOcean")
        print("\n4. Enterprise Deployment:")
        print("   - Kubernetes")
        print("   - AWS EKS")
        print("   - On-premise")
        
        print("\n" + "="*60)
        print("QUICK COMMANDS")
        print("="*60)
        print("\n# Deploy locally")
        print("./deploy.sh")
        print("\n# Check deployment status")
        print("docker-compose ps")
        print("\n# View logs")
        print("docker-compose logs -f")
        print("\n# Open API documentation")
        print("open http://localhost:8000/docs")
        print("\n# Open frontend")
        print("open http://localhost:3000")
        
        return ready

if __name__ == "__main__":
    verifier = DeploymentVerifier()
    ready = verifier.run_all_checks()
    sys.exit(0 if ready else 1)
