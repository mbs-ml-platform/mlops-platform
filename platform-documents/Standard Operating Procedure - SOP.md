## 📄 Hướng dẫn Vận hành Mã nguồn Polyrepo cho Nền tảng MLOps

### 🎯 Mục tiêu

Tài liệu này hướng dẫn cách thiết lập, quản lý và làm việc với cấu trúc polyrepo cho dự án Nền tảng MLOps. Mục tiêu là đảm bảo sự nhất quán, dễ dàng cộng tác và quản lý hiệu quả các thành phần mã nguồn riêng biệt.

---

### 1. Khởi tạo Polyrepo (Thực hiện một lần bởi Quản trị viên/Lead)

"Polyrepo" bản chất là một tập hợp các repo Git độc lập. Việc "khởi tạo polyrepo" nghĩa là tạo ra từng repo con này trên nền tảng quản lý mã nguồn của bạn (ví dụ: GitHub, GitLab).

**Các bước:**

1. **Đăng nhập vào Nền tảng Quản lý Mã nguồn:** Truy cập GitHub, GitLab, hoặc Bitbucket với tài khoản có quyền tạo repository.
2. **Tạo từng Repo con:** Với mỗi repo đã được định nghĩa trong kiến trúc (ví dụ: `feature-store-management`, `ml-model-development`, v.v.), thực hiện các bước sau:
    - Nhấn nút "New repository" (hoặc tương tự).
    - **Đặt tên Repo:** Sử dụng chính xác tên đã thống nhất (ví dụ: `feature-store-management`).
    - **Mô tả (Description):** Thêm mô tả ngắn gọn về mục đích của repo (ví dụ: "Quản lý định nghĩa features, pipelines dữ liệu cho Feature Store, và cấu hình Feast.").
    - **Visibility:** Chọn "Private" (nếu là dự án nội bộ) hoặc "Public" (nếu là mã nguồn mở).
    - **Initialize this repository with:**
        - ✅ **Add a README file:** Luôn tạo file README ban đầu.
        - ✅ **Add .gitignore:** Chọn template phù hợp (ví dụ: Python). Bạn sẽ tùy chỉnh sau.
        - **Choose a license:** Chọn giấy phép phù hợp nếu cần (ví dụ: MIT, Apache 2.0).
    - Nhấn "Create repository".
3. **Lặp lại:** Lặp lại bước 2 cho tất cả các repo con đã được xác định trong kiến trúc.
    - `feature-store-management`
    - `ml-model-development`
    - `ml-model-services`
    - `mlops-orchestration-pipelines`
    - `mlops-platform-infrastructure`
    - `ml-reporting-and-monitoring-logic`
4. **(Tùy chọn) Tạo một "Meta" hoặc "Manifest" Repo (Không bắt buộc nhưng hữu ích):**
    - Bạn có thể tạo một repo riêng, ví dụ `mlops-platform-manifest`, không chứa code thực thi mà chỉ chứa:
        - Tài liệu tổng quan về kiến trúc polyrepo.
        - Link đến tất cả các repo con.
        - Hướng dẫn chung về cách clone và thiết lập môi trường.
        - Các script tiện ích để clone tất cả các repo con một lúc (xem phần dưới).
    - Điều này giúp người mới dễ dàng nắm bắt cấu trúc tổng thể.

---

### 2. Clone và Thiết lập Môi trường (Dành cho Lập trình viên)

Mỗi lập trình viên sẽ clone những repo mà họ cần làm việc.

**Cách 1: Clone từng Repo một (Thủ công)**

1. **Tạo thư mục gốc cho dự án:** Trên máy tính của bạn, tạo một thư mục chính để chứa tất cả các repo con của dự án MLOps.
    
    Bash
    
    ```
    mkdir my-mlops-platform
    cd my-mlops-platform
    ```
    
2. **Lấy URL của Repo:** Từ GitHub/GitLab, vào trang của repo con bạn muốn clone (ví dụ: `feature-store-management`) và copy HTTPS hoặc SSH URL.
3. **Clone Repo:**
    
    Bash
    
    ```
    git clone <URL_CUA_REPO_CON>
    ```
    
    Ví dụ:
    
    Bash
    
    ```
    git clone git@github.com:your-organization/feature-store-management.git
    git clone git@github.com:your-organization/ml-model-development.git
    # ... và các repo khác bạn cần
    ```
    
4. **Thiết lập môi trường cho từng Repo:**
    - Di chuyển vào thư mục của repo vừa clone: `cd feature-store-management`
    - **Tạo môi trường ảo (khuyến nghị):**
        
        Bash
        
        ```
        python -m venv .venv
        source .venv/bin/activate  # Linux/macOS
        # .venv\Scripts\activate    # Windows
        ```
        
    - **Cài đặt dependencies:**
        
        Bash
        
        ```
        pip install -r requirements.txt
        ```
        
    - Thực hiện các bước thiết lập khác theo README của repo đó (ví dụ: copy file config template, thiết lập biến môi trường).
    - Lặp lại cho các repo khác.

**Cách 2: Dùng Script để Clone nhiều Repo (Nếu có Manifest Repo)**

Nếu bạn đã tạo `mlops-platform-manifest` repo với một script, quy trình sẽ đơn giản hơn:

1. **Clone Manifest Repo:**
    
    Bash
    
    ```
    git clone git@github.com:your-organization/mlops-platform-manifest.git
    cd mlops-platform-manifest
    ```
    
2. **Chạy Script Clone (Ví dụ):**
    - Script này có thể là một file shell (`.sh`) hoặc Python (`.py`) liệt kê và clone tất cả các repo con vào một thư mục được chỉ định.
    - Ví dụ `clone_all_repos.sh`:
        
        Bash
        
        ```
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
        ```
        
    - Chạy script: `bash clone_all_repos.sh`
3. **Thiết lập môi trường cho từng Repo:** Vẫn thực hiện như Cách 1, bước 4.

---

### 3. Workflow Làm việc Hàng ngày (Git Flow cơ bản)

Workflow này áp dụng cho **từng repo con một cách độc lập**. Chúng ta sẽ sử dụng một quy trình Git Flow đơn giản hóa.

**Các nhánh chính:**

- **`main` (hoặc `master`):** Nhánh ổn định, phản ánh code đã được kiểm thử và sẵn sàng cho production hoặc đã deploy lên production. Không bao giờ commit trực tiếp lên `main`.
- **`develop`:** Nhánh tích hợp các tính năng đã hoàn thành. Đây là nhánh cơ sở để tạo các nhánh feature.

**Quy trình phát triển một tính năng mới hoặc sửa lỗi:**

1. **Đảm bảo Repo được cập nhật:**
    - Chuyển vào thư mục của repo bạn đang làm việc (ví dụ: `cd feature-store-management`).
    - Chuyển sang nhánh `develop`:
        
        Bash
        
        ```
        git checkout develop
        ```
        
    - Kéo những thay đổi mới nhất từ remote:
        
        Bash
        
        ```
        git pull origin develop
        ```
        
2. **Tạo nhánh Feature/Bugfix mới:**
    - Tạo nhánh mới từ `develop`:
        
        Bash
        
        ```
        git checkout -b feature/ten-tinh-nang  # Ví dụ: feature/add-new-user-feature-view
        # Hoặc cho bugfix:
        # git checkout -b bugfix/mo-ta-loi      # Ví dụ: bugfix/fix-dbt-model-null-pointer
        ```
        
    - **Quy ước đặt tên nhánh:** `type/short-description` (ví dụ: `feature/user-authentication`, `bugfix/incorrect-calculation`, `chore/update-dependencies`).
3. **Thực hiện thay đổi (Code & Commit):**
    - Viết code, thêm file mới, sửa file hiện có.
    - **Commit thường xuyên với thông điệp rõ ràng:**
        
        Bash
        
        ```
        git add .  # Hoặc git add <ten-file-cu-the>
        git commit -m "feat: Thêm định nghĩa UserProfile FeatureView"
        # Hoặc: git commit -m "fix: Sửa lỗi chia cho không trong tính toán A"
        # Hoặc: git commit -m "docs: Cập nhật README cho phần cài đặt"
        ```
        
    - **Quy ước Commit Message (Khuyến nghị sử dụng Conventional Commits):**
        - `feat: A new feature`
        - `fix: A bug fix`
        - `docs: Documentation only changes`
        - `style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)`
        - `refactor: A code change that neither fixes a bug nor adds a feature`
        - `perf: A code change that improves performance`
        - `test: Adding missing tests or correcting existing tests`
        - `build: Changes that affect the build system or external dependencies`
        - `ci: Changes to our CI configuration files and scripts`
        - `chore: Other changes that don't modify src or test files`
4. **Push nhánh Feature/Bugfix lên Remote:**
    
    Bash
    
    ```
    git push origin feature/ten-tinh-nang
    ```
    
5. **Tạo Pull Request (PR) / Merge Request (MR):**
    - Truy cập GitHub/GitLab.
    - Bạn sẽ thấy gợi ý tạo Pull Request cho nhánh vừa push.
    - **Base branch (Đích):** `develop`
    - **Compare branch (Nguồn):** `feature/ten-tinh-nang`
    - Điền tiêu đề và mô tả rõ ràng cho PR.
    - Gán người review (reviewer).
6. **Review Code và Thảo luận:**
    - Reviewer sẽ xem xét code, đưa ra nhận xét.
    - Bạn có thể cần push thêm commit để sửa đổi theo feedback.
7. **Merge Pull Request:**
    - Sau khi PR được chấp thuận (approved) và các CI checks (tests, linting) đều pass.
    - Người có quyền (thường là bạn hoặc reviewer) sẽ merge PR vào nhánh `develop`.
    - **Khuyến nghị sử dụng "Squash and merge"** nếu có nhiều commit nhỏ, không cần thiết trong lịch sử của `develop`, để giữ cho lịch sử commit của `develop` sạch sẽ. Hoặc "Rebase and merge" để có lịch sử tuyến tính.
    - Xóa nhánh feature sau khi merge (GitHub/GitLab thường có tùy chọn này).
        
        Bash
        
        ```
        git branch -d feature/ten-tinh-nang # Xóa nhánh ở local (nếu muốn)
        ```
        
8. **Cập nhật nhánh `develop` ở local (nếu người khác vừa merge):**
    
    Bash
    
    ```
    git checkout develop
    git pull origin develop
    ```
    

**Quy trình Release (Chuyển từ `develop` sang `main`):**

Quy trình này thường được thực hiện bởi Lead/Quản trị viên hoặc tự động hóa bằng CI/CD khi đến kỳ release.

1. **Đảm bảo `develop` ổn định:** Tất cả các tính năng cho release đã được merge và kiểm thử kỹ lưỡng trên môi trường staging (nếu có).
2. **Tạo Pull Request từ `develop` sang `main`:**
    - **Base branch:** `main`
    - **Compare branch:** `develop`
3. **Review cẩn thận:** Đây là bước quan trọng trước khi đưa code lên production.
4. **Merge PR vào `main`:**
5. **Tạo Tag cho Release:**
    
    Bash
    
    ```
    git checkout main
    git pull origin main
    git tag -a v1.0.0 -m "Release version 1.0.0"
    git push origin v1.0.0
    ```
    
    Tag này sẽ được CI/CD pipeline sử dụng để build và deploy phiên bản production.

---

### 4. Làm việc với các Repo có Liên quan (Cross-Repo Dependencies)

Trong một hệ thống MLOps, các thành phần thường có sự phụ thuộc lẫn nhau (ví dụ: `ml-model-services` phụ thuộc vào model từ `ml-model-development` thông qua MLFlow Model Registry).

**Cách quản lý:**

- **Phiên bản hóa Artifacts:**
    - **Models:** MLFlow Model Registry quản lý phiên bản của model. Khi `ml-model-services` build, nó sẽ lấy một _phiên bản cụ thể_ (hoặc một stage như "Production") của model từ registry.
    - **Libraries/Packages nội bộ:** Nếu bạn tạo ra các thư viện Python dùng chung (ví dụ: trong `common_utils`của `ml-model-development` hoặc `common_service_libs` của `ml-model-services`) và muốn các repo khác sử dụng chúng như một dependency, bạn có thể:
        - **Cách 1 (Đơn giản, cho dự án nhỏ):** Sử dụng Git submodules hoặc copy code trực tiếp (ít khuyến khích vì khó quản lý phiên bản).
        - **Cách 2 (Tốt hơn):** Đóng gói thư viện đó thành một package Python và public lên một private Python Package Index (PyPI) server (ví dụ: Nexus, Artifactory, GitLab Package Registry, GitHub Packages). Sau đó, các repo khác sẽ khai báo dependency này trong `requirements.txt` với phiên bản cụ thể.
        - **Cách 3 (Monorepo tools for Polyrepo context):** Một số công cụ như `meta` (by Facebook) hoặc các script tùy chỉnh có thể giúp quản lý dependencies giữa các repo trong một "workspace" polyrepo, nhưng chúng tăng thêm độ phức tạp.
- **Giao tiếp qua APIs hoặc Message Queues:** Các service nên giao tiếp với nhau qua các API được định nghĩa rõ ràng hoặc qua message queues, thay vì phụ thuộc trực tiếp vào code của nhau.
- **CI/CD và Integration Testing:**
    - Khi một repo cung cấp artifact (ví dụ: `ml-model-development` tạo model), CI/CD của nó nên thông báo (ví dụ: qua webhook, hoặc cập nhật một "bill of materials") cho các repo phụ thuộc.
    - CI/CD của repo phụ thuộc (ví dụ: `ml-model-services`) có thể được trigger để build lại với artifact mới và chạy integration tests.

**Ví dụ Workflow khi model mới được duyệt trong `ml-model-development`:**

1. **`ml-model-development`:**
    - Data Scientist huấn luyện model, log vào MLFlow Model Registry.
    - Model được đánh giá, chuyển sang stage "Staging" hoặc "Production" trong MLFlow Model Registry.
2. **Trigger (Có thể tự động hoặc thủ công):**
    - Một webhook từ MLFlow (nếu có) hoặc một job Jenkins được lên lịch có thể phát hiện model mới ở stage "Production".
3. **`ml-model-services` (CI/CD Pipeline được trigger):**
    - Pipeline của `ml-model-services` cho một service cụ thể (ví dụ: `fraud_detection_api`) được kích hoạt.
    - Pipeline này sẽ:
        - Đọc cấu hình để biết cần lấy model "fraud_detection_model" với stage "Production" từ MLFlow.
        - Build Docker image mới cho service, nhúng model mới vào.
        - Deploy lên môi trường Staging, chạy integration tests (gửi request thử nghiệm, kiểm tra response).
        - Nếu Staging OK, chờ duyệt hoặc tự động deploy lên Production.

---

### 5. Quản lý Dependencies của từng Repo

- **Mỗi repo con phải có `requirements.txt` (hoặc `conda.yaml`, `poetry.lock`, `Pipfile.lock`) riêng.**
- Sử dụng môi trường ảo (`venv`, `conda env`) cho từng repo để tránh xung đột thư viện.
- Thường xuyên cập nhật dependencies và kiểm tra tương thích, đặc biệt là các vấn đề bảo mật. Công cụ như `pip-audit` hoặc `safety` có thể hữu ích.

---

### 6. Công cụ Hỗ trợ (Tùy chọn)

- **`pre-commit` hooks:** Tự động chạy linters (Flake8, Black, Pylint), formatters (Black, isort), và các checks khác trước khi commit. Điều này giúp đảm bảo chất lượng code và tính nhất quán. Cấu hình trong file `.pre-commit-config.yaml` ở gốc mỗi repo.
- **IDE Integration:** Các IDE như VS Code, PyCharm có tích hợp Git rất tốt, giúp việc commit, branch, merge dễ dàng hơn.
- **Docker:** Để đóng gói ứng dụng và đảm bảo môi trường nhất quán giữa development, staging, và production.

---

### 7. Nguyên tắc Vàng

- **Mỗi Repo một Trách nhiệm:** Giữ cho mỗi repo tập trung vào một phần cụ thể của hệ thống.
- **Giao tiếp Rõ ràng:** Thông qua commit messages, PR descriptions, và tài liệu.
- **Tự động hóa Tối đa:** CI/CD là bạn đồng hành không thể thiếu.
- **Review Kỹ lưỡng:** Đặc biệt là các PR vào `develop` và `main`.
- **Không Commit trực tiếp vào `main` hoặc `develop` (ngoại trừ merge PR).**
- **Luôn `pull` trước khi bắt đầu công việc mới trên một nhánh chia sẻ.**
