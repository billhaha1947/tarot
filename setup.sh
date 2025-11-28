#!/bin/bash

# Tarot AI Oracle Hub - Setup Script
# Chạy script này để setup toàn bộ project

echo "🔮 TAROT AI ORACLE HUB - SETUP"
echo "=================================="
echo ""

# Màu sắc
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${CYAN}Kiểm tra Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 chưa được cài đặt!${NC}"
    echo "Vui lòng cài Python 3.8+ từ: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Create virtual environment
echo -e "${CYAN}Tạo virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}! Virtual environment đã tồn tại, bỏ qua${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Đã tạo virtual environment${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${CYAN}Kích hoạt virtual environment...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/MacOS
    source venv/bin/activate
fi
echo -e "${GREEN}✓ Virtual environment đã được kích hoạt${NC}"
echo ""

# Upgrade pip
echo -e "${CYAN}Nâng cấp pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip đã được nâng cấp${NC}"
echo ""

# Install dependencies
echo -e "${CYAN}Cài đặt dependencies...${NC}"
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Đã cài đặt tất cả dependencies${NC}"
else
    echo -e "${RED}✗ Có lỗi khi cài đặt dependencies${NC}"
    exit 1
fi
echo ""

# Create directories
echo -e "${CYAN}Tạo thư mục cần thiết...${NC}"
mkdir -p static/avatar
mkdir -p static/js
mkdir -p templates
mkdir -p models
echo -e "${GREEN}✓ Đã tạo thư mục${NC}"
echo ""

# Create default avatar
echo -e "${CYAN}Tạo avatar mặc định...${NC}"
python3 create_default_avatar.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Đã tạo avatar mặc định${NC}"
else
    echo -e "${YELLOW}! Không thể tạo avatar, sẽ dùng placeholder${NC}"
fi
echo ""

# Check if all files exist
echo -e "${CYAN}Kiểm tra files...${NC}"
FILES=(
    "app.py"
    "database.py"
    "model_manager.py"
    "pseudo_ai.py"
    "requirements.txt"
    "templates/layout.html"
    "templates/login.html"
    "templates/register.html"
    "templates/chat.html"
    "templates/settings.html"
    "static/js/app.js"
)

MISSING=0
for FILE in "${FILES[@]}"; do
    if [ -f "$FILE" ]; then
        echo -e "${GREEN}✓${NC} $FILE"
    else
        echo -e "${RED}✗${NC} $FILE ${RED}(MISSING)${NC}"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    echo ""
    echo -e "${RED}✗ Thiếu $MISSING file(s)!${NC}"
    echo "Vui lòng đảm bảo tất cả files đã được tạo."
    exit 1
fi
echo ""

# Initialize database
echo -e "${CYAN}Khởi tạo database...${NC}"
python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("✓ Database đã được khởi tạo")
EOF
echo ""

# Success message
echo ""
echo -e "${GREEN}=================================="
echo "✅ SETUP HOÀN TẤT!"
echo "==================================${NC}"
echo ""
echo -e "${CYAN}Để chạy ứng dụng:${NC}"
echo ""
echo "  1. Kích hoạt virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "     ${YELLOW}venv\\Scripts\\activate${NC}"
else
    echo "     ${YELLOW}source venv/bin/activate${NC}"
fi
echo ""
echo "  2. Chạy server:"
echo "     ${YELLOW}python app.py${NC}"
echo ""
echo "  3. Mở trình duyệt:"
echo "     ${YELLOW}http://localhost:5000${NC}"
echo ""
echo -e "${CYAN}Hoặc dùng Docker:${NC}"
echo "     ${YELLOW}docker build -t tarot-oracle .${NC}"
echo "     ${YELLOW}docker run -p 5000:5000 tarot-oracle${NC}"
echo ""
echo -e "${CYAN}Deploy lên Render.com:${NC}"
echo "     Xem hướng dẫn trong ${YELLOW}DEPLOY_RENDER.md${NC}"
echo ""
echo -e "${GREEN}Chúc bạn may mắn với Oracle! 🔮✨${NC}"
echo ""
