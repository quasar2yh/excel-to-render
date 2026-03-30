# BluePrint - Excel to CAD Rendering Platform

Excel 도면을 DXF(CAD) 형식으로 변환하고, 여러 렌더러를 통해 2D/3D 시각화하는 플랫폼입니다.

## 🎯 주요 기능

### 1. **Excel → DXF 변환**
- Excel 스프레드시트의 격자 데이터를 CAD 형식으로 변환
- 병합된 셀(Merged Cells) 자동 인식 및 처리
- 셀 치수 정보 파싱 (예: "아동언더웨어\n3000, 800")
- 커스텀 격자 크기 설정 가능
- 다양한 단위 지원 (mm, cm, m, in, ft)

### 2. **다중 렌더러 지원**
- **Blender**: 고품질 3D 렌더링 및 재료 시뮬레이션
- **KeyShot**: 건축/제품 시각화용 전문 렌더러
- **Open Cascade**: 3D CAD 커널 기반 렌더링
- **Three.js (Web)**: 인터랙티브 브라우저 기반 뷰어

### 3. **레이어 기반 조직화**
- 벽(STRUCT_WALLS), 선반(SHELVES), 섬(RETAIL_ISLANDS) 등 분류
- 각 레이어별 색상 및 높이 자동 설정
- CAD 소프트웨어에서 선택적 표시 가능

## 📋 요구사항

```
Python >= 3.13
ezdxf >= 1.4.3      # DXF 파일 생성
openpyxl >= 3.1.5   # Excel 파일 읽기
pandas >= 3.0.1     # 데이터 처리
```

렌더러별 추가 요구사항:
- **Blender**: Blender 4.0+
- **KeyShot**: KeyShot 13+
- **Open Cascade**: pythonocc-core
- **Three.js**: Node.js 16+, npm

## 🚀 설치 및 사용

### 기본 설정

```bash
# 의존성 설치 (uv 사용 권장)
uv sync
```

### 1️⃣ Excel to DXF 변환

**입력 Excel 형식 예시:**
```

```

**기본 변환:**
```bash
uv run src/excel_to_dxf.py \
  --input sample/excel_blueprint2.xlsx \
  --output sample/generated_floor_plan.dxf
```

**옵션 지정:**
```bash
uv run src/excel_to_dxf.py \
  --input sample/excel_blueprint2.xlsx \
  --output output.dxf \
  --cell-width 30.0 \
  --cell-height 30.0 \
  --unit cm
```

**파라미터:**
- `--input`: 입력 Excel 파일 경로
- `--output`: 출력 DXF 파일 경로
- `--cell-width`: 격자 셀 너비 (기본값: 30)
- `--cell-height`: 격자 셀 높이 (기본값: 30)
- `--unit`: 단위 선택 (mm/cm/m/in/ft, 기본값: cm)

### 2️⃣ Blender 렌더러

```bash
cd renderers/blender
# Blender 스크립트 실행 (PowerShell)
./render.ps1

# 또는 Python에서 직접
python render_dxf.py --input ../../sample/generated_floor_plan.dxf
```

**주요 기능:**
- 자동 재료 할당 (메탈릭, 러프니스)
- 텍스트 라벨 자동 생성
- 고해상도 렌더링 출력
- 카메라 각도 조정 가능

### 3️⃣ Open Cascade 3D 렌더러

```bash
cd renderers/open-cascade
uv sync

python renderer.py ../../sample/generated_floor_plan.dxf
```

**기능:**
- 실시간 3D 인터랙션
- 레이어별 색상 자동 적용
- 높이 기반 3D 렌더링
- GUI 창에서 회전/확대 가능

### 4️⃣ Web 기반 Three.js 뷰어

```bash
cd renderers/dxf-threejs
npm install
npm run dev

# 브라우저에서 접속: http://localhost:5173
```

**기능:**
- 마우스로 3D 회전/확대/축소
- 터치 제스처 지원
- 실시간 렌더링
- WebGL 기반 고성능

### 5️⃣ KeyShot 렌더러

```bash
cd renderers/keyshot
./render.ps1
```

전문적인 건축 시각화를 위한 렌더러입니다.

## 📊 프로젝트 구조

```
blueprint/
├── src/
│   └── excel_to_dxf.py          # 핵심 변환 로직
├── renderers/
│   ├── blender/                 # Blender 렌더러
│   ├── keyshot/                 # KeyShot 렌더러
│   ├── open-cascade/            # Open Cascade 3D 렌더러
│   └── dxf-threejs/             # 웹 기반 Three.js 뷰어
├── sample/                      # 테스트 샘플 파일
│   ├── excel_blueprint.xlsx
│   └── excel_blueprint2.xlsx
└── main.py                      # 메인 진입점
```

## 💡 사용 예제

### 전체 워크플로우

```bash
# 1. Excel을 DXF로 변환
python src/excel_to_dxf.py \
  --input sample/excel_blueprint2.xlsx \
  --output floor_plan.dxf \
  --unit cm

# 2. 웹 뷰어에서 확인
cd renderers/dxf-threejs
npm install && npm run dev

# 3. Blender에서 고급 렌더링
cd ../blender
python render_dxf.py --input ../../floor_plan.dxf
```

### Python API 사용

```python
from src.excel_to_dxf import convert_excel_to_dxf

# Excel을 DXF로 변환
convert_excel_to_dxf(
    input_excel='sample/excel_blueprint2.xlsx',
    output_dxf='output.dxf',
    cell_width=30.0,
    cell_height=30.0,
    unit='cm'
)
```

## 🔧 지원하는 단위

| 단위 | 코드 | 용도 |
|------|------|------|
| 밀리미터 | mm | 정밀 제도 |
| 센티미터 | cm | 기본값 - 소형 도면 |
| 미터 | m | 건축 도면 |
| 인치 | in | 북미 표준 |
| 피트 | ft | 건축 도면 |

## 🎨 레이어별 색상 (Open Cascade)

| 레이어 | 색상 | 높이 |
|--------|------|------|
| STRUCT_WALLS | 흰색 | 100 |
| SHELVES | 강철파란색 | 60 |
| RETAIL_ISLANDS | 주황색 | 40 |
| CHECKOUT | 초록색 | 30 |
| PILLARS | 회색 | 120 |

## 📝 Excel 파일 형식

### 기본 형식
```
┌─────────────────┬──────────────┐
│ 아동언더웨어    │ 여성향내의   │
│ 3000, 800      │ 2500, 900   │
├─────────────────┼──────────────┤
│ 스포츠용품      │ 신발         │
│ 4000, 1000     │ 3500, 800   │
└─────────────────┴──────────────┘
```

### 파일 읽기 규칙
1. **첫 번째 행**: 상품명 또는 영역명
2. **두 번째 행**: 치수 정보 (너비, 높이)
3. **구분자**: 쉼표, 공백, 'x' 모두 지원
4. **병합된 셀**: 자동으로 인식되어 확대된 영역으로 표시

## 🐛 트러블슈팅

### DXF 파일이 생성되지 않음
```bash
# 입력 파일 경로 확인
python src/excel_to_dxf.py --input sample/excel_blueprint2.xlsx

# 권한 확인
# Windows: 관리자 권한으로 실행
# Linux/Mac: chmod +x 확인
```

### Blender에서 임포트 실패
```python
# Blender 콘솔에서 ezdxf 설치 확인
import ezdxf
print(ezdxf.__version__)
```

### Three.js 뷰어가 로드되지 않음
```bash
cd renderers/dxf-threejs
npm cache clean --force
npm install
npm run dev
```




## 🔄 업데이트 로그

### v0.1.0
- ✅ Excel to DXF 기본 변환
- ✅ Blender 렌더러 구현
- ✅ Open Cascade 3D 렌더링
- ✅ Three.js 웹 뷰어
- ✅ KeyShot 렌더러 통합

---

**작성일**: 2026-03-30
**버전**: 0.1.0
