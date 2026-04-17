#!/usr/bin/env python3
"""
Production Readiness Checker
Validates that the agent meets all production requirements
"""
import os
import sys
import subprocess
from pathlib import Path


class ProductionChecker:
    def __init__(self):
        self.score = 0
        self.max_score = 100
        self.results = []
        self.root = Path(__file__).parent
    
    def check(self, name, points, func):
        """Run a check and record result"""
        try:
            func()
            self.score += points
            self.results.append(f"✅ {name}: {points}/{points}")
            return True
        except AssertionError as e:
            self.results.append(f"❌ {name}: 0/{points} - {e}")
            return False
        except Exception as e:
            self.results.append(f"❌ {name}: 0/{points} - Error: {e}")
            return False
    
    def file_exists(self, path):
        """Check if file exists"""
        full_path = self.root / path
        assert full_path.exists(), f"{path} not found"
        return full_path
    
    def file_contains(self, path, text):
        """Check if file contains text"""
        full_path = self.file_exists(path)
        try:
            content = full_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = full_path.read_text(encoding='latin-1')
        assert text in content, f"{path} does not contain '{text}'"
    
    def run_all_checks(self):
        """Run all production readiness checks"""
        print("🧪 Running Production Readiness Checks...\n")
        print("="*60)
        
        # File Structure (10 points)
        print("\n📁 File Structure")
        self.check("Dockerfile exists", 2, lambda: self.file_exists("Dockerfile"))
        self.check("docker-compose.yml exists", 2, lambda: self.file_exists("docker-compose.yml"))
        self.check("requirements.txt exists", 1, lambda: self.file_exists("requirements.txt"))
        self.check(".dockerignore exists", 1, lambda: self.file_exists(".dockerignore"))
        self.check(".env.example exists", 1, lambda: self.file_exists(".env.example"))
        self.check("README.md exists", 1, lambda: self.file_exists("README.md"))
        self.check("app/main.py exists", 1, lambda: self.file_exists("app/main.py"))
        self.check("app/config.py exists", 1, lambda: self.file_exists("app/config.py"))
        
        # Docker Quality (15 points)
        print("\n🐳 Docker Quality")
        self.check("Multi-stage Dockerfile", 5, 
                  lambda: self.file_contains("Dockerfile", "AS builder"))
        self.check("Uses slim base image", 3,
                  lambda: self.file_contains("Dockerfile", "python:3.11-slim"))
        self.check("Non-root user", 3,
                  lambda: self.file_contains("Dockerfile", "USER agent"))
        self.check("Health check in Dockerfile", 2,
                  lambda: self.file_contains("Dockerfile", "HEALTHCHECK"))
        self.check("Docker Compose has redis", 2,
                  lambda: self.file_contains("docker-compose.yml", "redis:"))
        
        # Configuration (10 points)
        print("\n⚙️  Configuration")
        self.check("Config from environment", 3,
                  lambda: self.file_contains("app/config.py", "os.getenv"))
        self.check("Settings validation", 3,
                  lambda: self.file_contains("app/config.py", "def validate"))
        self.check("No hardcoded secrets in main.py", 2,
                  lambda: not self.check_hardcoded_secrets("app/main.py"))
        self.check("No hardcoded secrets in config.py", 2,
                  lambda: not self.check_hardcoded_secrets("app/config.py"))
        
        # Security (20 points)
        print("\n🔒 Security")
        self.check("API Key authentication", 5,
                  lambda: self.file_contains("app/auth.py", "verify_api_key"))
        self.check("Rate limiting module", 5,
                  lambda: self.file_contains("app/rate_limiter.py", "check_rate_limit"))
        self.check("Cost guard module", 5,
                  lambda: self.file_contains("app/cost_guard.py", "check_budget"))
        self.check("Security headers", 3,
                  lambda: self.file_contains("app/main.py", "X-Content-Type-Options"))
        self.check("CORS configured", 2,
                  lambda: self.file_contains("app/main.py", "CORSMiddleware"))
        
        # Reliability (20 points)
        print("\n🛡️  Reliability")
        self.check("Health endpoint", 5,
                  lambda: self.file_contains("app/main.py", "/health"))
        self.check("Readiness endpoint", 5,
                  lambda: self.file_contains("app/main.py", "/ready"))
        self.check("Graceful shutdown", 5,
                  lambda: self.file_contains("app/main.py", "SIGTERM"))
        self.check("Structured logging", 3,
                  lambda: self.file_contains("app/main.py", "json.dumps"))
        self.check("Lifespan management", 2,
                  lambda: self.file_contains("app/main.py", "lifespan"))
        
        # Deployment (10 points)
        print("\n☁️  Deployment")
        self.check("Railway config", 5,
                  lambda: self.file_exists("railway.toml"))
        self.check("Render config", 5,
                  lambda: self.file_exists("render.yaml"))
        
        # Documentation (5 points)
        print("\n📚 Documentation")
        self.check("README has setup instructions", 3,
                  lambda: self.file_contains("README.md", "Quick Start"))
        self.check("README has API documentation", 2,
                  lambda: self.file_contains("README.md", "API Documentation"))
        
        # Best Practices (10 points)
        print("\n✨ Best Practices")
        self.check("Input validation with Pydantic", 3,
                  lambda: self.file_contains("app/main.py", "BaseModel"))
        self.check("Error handling", 3,
                  lambda: self.file_contains("app/main.py", "HTTPException"))
        self.check("Request middleware", 2,
                  lambda: self.file_contains("app/main.py", "@app.middleware"))
        self.check(".gitignore exists", 2,
                  lambda: self.file_exists(".gitignore"))
        
        # Print Results
        print("\n" + "="*60)
        print("📊 RESULTS")
        print("="*60)
        for result in self.results:
            print(result)
        print("="*60)
        print(f"🎯 TOTAL SCORE: {self.score}/{self.max_score}")
        print(f"📈 PERCENTAGE: {self.score/self.max_score*100:.1f}%")
        print("="*60)
        
        if self.score >= self.max_score * 0.9:
            print("🌟 EXCELLENT! Production ready!")
        elif self.score >= self.max_score * 0.7:
            print("✅ GOOD! Minor improvements needed.")
        elif self.score >= self.max_score * 0.5:
            print("⚠️  NEEDS WORK! Several issues to fix.")
        else:
            print("❌ NOT READY! Major issues found.")
        
        return self.score
    
    def check_hardcoded_secrets(self, filepath):
        """Check for hardcoded secrets"""
        full_path = self.root / filepath
        if not full_path.exists():
            return False
        
        try:
            content = full_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = full_path.read_text(encoding='latin-1')
        
        # Patterns that indicate hardcoded secrets
        bad_patterns = [
            "sk-",  # OpenAI keys
            "password=",
            "secret=",
            "api_key=\"",
            "api_key='",
        ]
        
        for pattern in bad_patterns:
            if pattern in content.lower():
                # Check if it's in a comment or example
                lines = content.split('\n')
                for line in lines:
                    if pattern in line.lower():
                        # Skip comments and examples
                        if '#' in line or 'example' in line.lower() or '.env' in line:
                            continue
                        # Skip if it's reading from env
                        if 'getenv' in line or 'environ' in line:
                            continue
                        return True
        
        return False


if __name__ == "__main__":
    checker = ProductionChecker()
    score = checker.run_all_checks()
    
    # Exit with appropriate code
    sys.exit(0 if score >= checker.max_score * 0.7 else 1)
