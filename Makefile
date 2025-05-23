# Day Trading Debunk Project
# Simple commands to run common tasks

.PHONY: help test backtest clean install lint format

help:  ## Show this help message
	@echo "Day Trading Debunk - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

test:  ## Run all tests with coverage
	python run_tests.py

test-unit:  ## Run only unit tests
	python run_tests.py unit

test-integration:  ## Run only integration tests  
	python run_tests.py integration

backtest:  ## Run strategy backtest comparison
	python run_backtest.py

stats-demo:  ## Run statistical analysis demo
	python -c "from src.statistical_analysis.advanced_stats import *; exec(open('src/statistical_analysis/advanced_stats.py').read().split('if __name__ == \"__main__\":')[1])"

lint:  ## Check code style
	@echo "Checking code style..."
	@python -m flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503 || true

format:  ## Format code with black
	@echo "Formatting code..."
	@python -m black src/ tests/ *.py --line-length=100 || echo "Install black with: pip install black"

clean:  ## Clean up generated files
	@echo "Cleaning up..."
	@rm -rf __pycache__/ */__pycache__/ */*/__pycache__/
	@rm -rf .pytest_cache/ htmlcov/ .coverage
	@rm -f *.png *.pdf *.log
	@echo "✅ Cleaned up temporary files"

structure:  ## Show project structure
	@echo "Project Structure:"
	@tree -I '__pycache__|.git|.venv|htmlcov|.pytest_cache' . || ls -la

quick-demo:  ## Run a quick demo of everything
	@echo "🚀 Running quick demo..."
	@make test-unit
	@make backtest
	@echo "✅ Demo complete! Check the generated plots." 