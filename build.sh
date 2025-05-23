#!/bin/bash
# Build script for the day-trading-debunk project

echo "🚀 Building Day Trading Debunk Project..."

# Install dependencies
echo "📦 Installing dependencies..."
make install

# Run all tests
echo "🧪 Running tests..."
make test

# Run a backtest comparison
echo "📊 Running backtest demonstration..."
make backtest

# Show project structure
echo "📁 Project structure:"
make structure

# Clean up generated files
echo "🧹 Cleaning up..."
make clean

# Quick demo of everything
echo "🎯 Running quick demo..."
make quick-demo

echo "✅ Build complete! Your day trading debunk project is ready to go."
echo ""
echo "Available commands:"
echo "  make help       - Show all available commands"
echo "  make test       - Run all tests"
echo "  make backtest   - Run strategy comparison"
echo "  make clean      - Clean up generated files"
