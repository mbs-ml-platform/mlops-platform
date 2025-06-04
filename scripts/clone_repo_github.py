#!/usr/bin/env python3
"""
Script to clone tất cả các MLOps platform repositories và chuyển sang nhánh 'dev'.
Chạy được trên Windows, macOS và Linux (miễn là đã cài Python và Git trong PATH).
- Nếu thư mục repo chưa tồn tại: clone về rồi chuyển sang 'dev'.
- Nếu repo đã tồn tại: vẫn fetch & checkout sang 'dev'.
- Nếu local chưa có 'dev' mà remote origin/dev tồn tại: tạo local tracking từ origin/dev.
- Nếu remote cũng không có 'dev': in cảnh báo và bỏ qua.
"""

import os
import subprocess
import sys

# Danh sách URL các repo cần clone.
# Nếu đã có SSH key, có thể đổi sang git@github.com:mbs-ml-platform/...
REPOS = [
    "https://github.com/mbs-ml-platform/mlops-feature-store.git",
    "https://github.com/mbs-ml-platform/mlops-model-development.git",
    "https://github.com/mbs-ml-platform/mlops-model-services.git",
    "https://github.com/mbs-ml-platform/mlops-orchestration-pipelines.git",
    "https://github.com/mbs-ml-platform/mlops-platform-infrastructure.git",
    "https://github.com/mbs-ml-platform/mlops-reporting-and-monitoring.git",
]

def is_git_available() -> bool:
    """
    Kiểm tra xem lệnh `git` đã nằm trong PATH hay chưa.
    """
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

def derive_local_dir(repo_url: str) -> str:
    """
    Lấy tên thư mục mặc định từ URL, ví dụ ".../mlops-feature-store.git" -> "mlops-feature-store"
    """
    return os.path.splitext(os.path.basename(repo_url))[0]

def switch_to_dev(repo_dir: str):
    """
    Chuyển (checkout) repo tại đường dẫn repo_dir về nhánh 'dev'.
    - Nếu local đã có branch 'dev': checkout luôn.
    - Nếu chưa có mà remote origin/dev tồn tại: tạo local dev tracking origin/dev.
    - Ngược lại: in cảnh báo.
    """
    cwd = os.getcwd()
    os.chdir(repo_dir)
    print(f"    → Đang chuyển sang nhánh 'dev' trong {repo_dir} ...")

    # 1. git fetch origin (đảm bảo có thông tin remote mới nhất)
    subprocess.run(["git", "fetch", "origin"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Kiểm tra local branch 'dev' đã tồn tại chưa
    result_local = subprocess.run(
        ["git", "rev-parse", "--verify", "dev"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    if result_local.returncode == 0:
        # local có sẵn 'dev'
        subprocess.run(["git", "checkout", "dev"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("      ✔ Đã chuyển sang nhánh local 'dev'.")
        os.chdir(cwd)
        return

    # 3. Nếu chưa có local, kiểm tra remote origin/dev
    result_remote = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", "dev"],
        capture_output=True, text=True
    )

    if result_remote.stdout.strip():
        # remote có nhánh dev, tạo local tracking
        subprocess.run(
            ["git", "checkout", "-b", "dev", "origin/dev"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print("      ✔ Đã tạo và chuyển sang nhánh local 'dev' từ 'origin/dev'.")
    else:
        # remote cũng không có dev -> cảnh báo
        print("      ⚠ Không tìm thấy nhánh 'dev' trên remote; bỏ qua chuyển đổi.", file=sys.stderr)

    os.chdir(cwd)

def clone_and_prepare(target_dir: str, repos: list):
    """
    Di chuyển vào target_dir, clone (nếu cần), rồi switch từng repo sang nhánh 'dev'.
    """
    os.makedirs(target_dir, exist_ok=True)
    os.chdir(target_dir)
    print(f"> Đang xử lý thư mục chứa các repo: {os.getcwd()}")

    for url in repos:
        repo_name = derive_local_dir(url)  # ví dụ: "mlops-feature-store"
        repo_path = os.path.join(target_dir, repo_name)

        # Nếu thư mục repo chưa tồn tại -> clone
        if not os.path.isdir(repo_path):
            print(f"  • Cloning {url} ...")
            try:
                subprocess.run(["git", "clone", url], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print(f"    ✔ Đã clone xong: {repo_name}")
            except subprocess.CalledProcessError as e:
                print(f"    ✘ Lỗi khi clone {url} (exit code {e.returncode})", file=sys.stderr)
                # Nếu clone thất bại, sang repo kế tiếp
                continue
        else:
            print(f"  • [{repo_name}] đã tồn tại, bỏ qua clone, chỉ chuyển nhánh.")

        # Dù mới clone hay đã tồn tại, đều thực hiện bước switch sang 'dev'
        switch_to_dev(repo_path)

def main():
    # 1. Kiểm tra Git đã cài chưa
    if not is_git_available():
        print("Error: 'git' không tìm thấy trong PATH. Vui lòng cài đặt Git trước khi chạy script này.", file=sys.stderr)
        sys.exit(1)

    # 2. Xác định thư mục đích: một cấp cha của scripts (tương đương TARGET_DIR="..")
    here = os.path.dirname(os.path.realpath(__file__))
    target_dir = os.path.normpath(os.path.join(here, ".."))

    # 3. Thực hiện clone (nếu cần) và chuyển sang 'dev'
    clone_and_prepare(target_dir, REPOS)

    # 4. In hướng dẫn tiếp theo (nếu cần)
    print("\nTất cả các repo đã được xử lý xong.")
    print("\nBạn có thể vào từng thư mục và tiếp tục làm việc trên nhánh 'dev', ví dụ:")
    print("  cd mlops-feature-store  && git branch  # xác nhận đang ở nhánh 'dev'")
    print("  cd mlops-model-development  && git branch  # ...")
    print("Nếu muốn pull/push, đảm bảo remote đã có nhánh 'dev' (nếu cần tạo mới trên remote, bạn có thể dùng:")
    print("  git push -u origin dev")
    print(")")

if __name__ == "__main__":
    main()
