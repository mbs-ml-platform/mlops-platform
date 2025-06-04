#!/bin/bash
# Script to clone all MLOps platform repositories

# Tạo thư mục chứa các repo nếu chưa có
TARGET_DIR="../my-mlops-platform-workspace"
mkdir -p $TARGET_DIR
cd $TARGET_DIR

echo "Cloning repositories into $(pwd)..."

git clone git@github.com:your-organization/feature-store-management.git
git clone git@github.com:your-organization/ml-model-development.git
git clone git@github.com:your-organization/ml-model-services.git
git clone git@github.com:your-organization/mlops-orchestration-pipelines.git
git clone git@github.com:your-organization/mlops-platform-infrastructure.git
git clone git@github.com:your-organization/ml-reporting-and-monitoring-logic.git

echo "All repositories cloned."

# Hướng dẫn thiết lập môi trường (có thể thêm vào script hoặc in ra màn hình)
echo "Next steps:"
echo "1. cd into each repository."
echo "2. Create a virtual environment: python -m venv .venv && source .venv/bin/activate"
echo "3. Install dependencies: pip install -r requirements.txt"
