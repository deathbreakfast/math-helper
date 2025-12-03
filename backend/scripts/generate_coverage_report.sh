#!/bin/bash
# Generate coverage report for backend tests
#
# Usage:
#   ./scripts/generate_coverage_report.sh
#   ./scripts/generate_coverage_report.sh html
#   ./scripts/generate_coverage_report.sh json

set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to backend directory
cd "$BACKEND_DIR"

# Report format (html, json, term, or all)
REPORT_FORMAT="${1:-html}"

echo "Generating coverage report (format: $REPORT_FORMAT)..."

# Run pytest with coverage
pytest \
    --cov=app \
    --cov-report=term \
    --cov-report=html:coverage/html \
    --cov-report=json:coverage/coverage.json \
    tests/

echo ""
echo "Coverage report generated!"
echo ""

# Display summary based on format
if [ "$REPORT_FORMAT" == "html" ] || [ "$REPORT_FORMAT" == "all" ]; then
    if [ -f "coverage/html/index.html" ]; then
        echo "HTML report: file://$BACKEND_DIR/coverage/html/index.html"
    fi
fi

if [ "$REPORT_FORMAT" == "json" ] || [ "$REPORT_FORMAT" == "all" ]; then
    if [ -f "coverage/coverage.json" ]; then
        echo "JSON report: $BACKEND_DIR/coverage/coverage.json"
    fi
fi

