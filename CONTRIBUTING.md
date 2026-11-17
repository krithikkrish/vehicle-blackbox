# Contributing to the Autonomous Vehicle Black Box Project

Thank you for your interest in contributing! This project is an open-source embedded Event Data Recorder (EDR) and telematics telemetry hub developed for the Raspberry Pi 4B.

---

## 🛠️ Development Workflow

### 1. Fork & Clone
```bash
git clone https://github.com/<your-username>/vehicle-blackbox.git
cd vehicle-blackbox
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create a Feature Branch
```bash
git checkout -b feat/your-feature-name
# or for bugfixes:
git checkout -b fix/issue-description
```

---

## 🧪 Testing Guidelines

Before committing or opening a Pull Request, verify that all files compile and all automated unit tests pass:

```bash
# 1. Check Python syntax
python3 -m py_compile *.py src/*.py tests/*.py scripts/*.py

# 2. Run automated test suite
python3 -m unittest tests/test_unit.py -v

# 3. Verify standalone test scripts in mock mode
python3 tests/test_gsm_sms.py
```

---

## 📝 Commit Conventions

We follow Conventional Commits formatting:
- `feat:` New capability or sensor integration
- `fix:` Bug fix or sensor threshold calibration
- `docs:` Documentation improvements or report updates
- `test:` Adding or updating test cases
- `chore:` Maintenance, dependency updates, or configuration

---

## 📬 Submitting a Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feat/your-feature-name
   ```
2. Open a Pull Request against the `main` branch.
3. Ensure the automated GitHub Actions CI tests pass.
4. Describe the change, the problem it solves, and the hardware or simulation environment tested.
