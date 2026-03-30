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

### 핵심 라이브러리
```
Python >= 3.13
ezdxf >= 1.4.3      # DXF 파일 생성
openpyxl >= 3.1.5   # Excel 파일 읽기
pandas >= 3.0.1     # 데이터 처리
```

### 렌더러별 요구사항
- **Blender 렌더러**: Blender 4.0+ (Blender Python API)
- **KeyShot 렌더러**: KeyShot 13+ (렉서 API 포함)
- **Open Cascade 렌더러**: pythonocc-core 7.7+
- **Three.js 웹 뷰어**: Node.js 16+, npm

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

### 2️⃣ Blender 렌더러 (고급 3D 렌더링)

Blender 렌더러는 가장 고도화된 시각화 솔루션으로, 실사적인 3D 렌더링을 제공합니다.

#### 기본 실행

```bash
cd renderers/blender

# PowerShell을 통한 자동 실행
./render.ps1

# Blender Python API로 직접 실행 (권장)
blender --background --python render_dxf.py -- \
  ../../sample/generated_floor_plan.dxf output.png
```

#### 주요 고도화 기능

| 기능 | 설명 |
|------|------|
| **동적 재료 시스템** | 레이어별 물리 기반 렌더링 (PBR) |
| **선반 모델링** | 현실적인 슈퍼마켓 선반 구조 시뮬레이션 |
| **스마트 텍스트** | 길이 기반 자동 스케일링 및 회전 |
| **색상 매핑** | DXF 색상 정보 자동 인식 |
| **투명도 처리** | 유리, 창문 등 투명 재료 |
| **3D 그림자** | 현실적인 그림자 및 조명 |
| **고급 조명** | Sun + Area light 이중 조명 시스템 |

#### 상세 옵션

```bash
blender --background --python render_dxf.py -- \
  input.dxf output.png \
  --cam-dist 1.5 \
  --cam-pitch 45.0 \
  --cam-yaw 20.0 \
  --unit-scale 1.0 \
  --text-size 12.0 \
  --text-thickness 0.5 \
  --text-shadow 0.2 \
  --color \
  --material \
  --clip-end 100000.0
```

**파라미터 설명:**

| 옵션 | 기본값 | 범위 | 설명 |
|------|-------|------|------|
| `--cam-dist` | 1.5 | 0.5~5.0 | 카메라 거리 배수 (장면 크기 대비) |
| `--cam-pitch` | 45.0 | 0~90 | 카메라 높이 각도 (도) |
| `--cam-yaw` | 20.0 | -180~180 | 카메라 회전 각도 (도) |
| `--unit-scale` | 1.0 | 0.001~1000 | 좌표 스케일 변환 (cm→m: 0.01) |
| `--text-size` | 12.0 | 1~100 | 텍스트 기본 높이 |
| `--text-thickness` | 0.0 | 0~2.0 | 텍스트 2D 굵기 (선택) |
| `--text-shadow` | 0.2 | 0~1.0 | 텍스트 3D 깊이/그림자 |
| `--clip-end` | 100000.0 | 100~1000000 | 카메라 원거리 클리핑 |
| `--color` | 비활성 | - | DXF 색상 정보 적용 (플래그) |
| `--material` | 비활성 | - | DXF 재료/투명도 적용 (플래그) |

#### 재료 자동 매핑

Blender는 DXF 레이어명을 기반으로 자동 재료를 할당합니다:

```
GLASS, WINDOW    → 유리 (반투명, 낮은 러프니스)
METAL, SHELVES   → 금속 (메탈릭 0.8, 러프니스 0.2)
WALL             → 벽 (높은 러프니스 0.9)
TEXT, MTEXT      → 골드 텍스트 (반짝임)
```

#### 선반 시뮬레이션 (SHELVES 레이어)

SHELVES 또는 ISLAND 레이어의 entity는 현실적인 슈퍼마켓 선반으로 렌더링됩니다:

```
고급 기능:
- 다단 선반 (기본 4단계)
- 하단 킥보드 (두꺼운 베이스)
- 중앙 디바이더
- 양측 돌출 플래터
```

**예제: 현실적인 선반 렌더링**
```bash
blender --background --python render_dxf.py -- \
  blueprint.dxf shelf_render.png \
  --cam-pitch 30.0 \
  --cam-yaw 45.0 \
  --material \
  --text-size 10.0
```

#### 카메라 위치 정밀 제어

카메라는 3D 각도와 거리로 제어됩니다:

```
cam-pitch (높이):  0도 = 정측면, 45도 = 사시도, 90도 = 평면도
cam-yaw (방향):   0도 = 정면, 90도 = 좌측, 180도 = 후면, -90도 = 우측
cam-dist (거리):  1.0 = 가까움, 2.0 = 표준, 3.0 = 멀음
```

**시각화 예제:**
```
정면도 (고도):
  --cam-pitch 0 --cam-yaw 0 --cam-dist 2.0

사시도 (입체):
  --cam-pitch 35 --cam-yaw 45 --cam-dist 1.8

평면도 (탑뷰):
  --cam-pitch 89 --cam-yaw 0 --cam-dist 1.0
```

#### 텍스트 라벨 자동화

- **스마트 회전**: 자동으로 0도 또는 90도로 정렬 (가독성 최적화)
- **길이 기반 축소**: 긴 텍스트는 자동으로 축소
- **3D 그림자**: extrude 파라미터로 깊이감 조절
- **수동 굵기**: thickness로 2D 굵기 조절

**텍스트 옵션 조합 예:**
```bash
--text-size 14.0 --text-thickness 1.0 --text-shadow 0.5
```

#### 출력 품질

- **해상도**: 자동으로 1920×1080 Full HD
- **포맷**: PNG (알파 채널 포함 가능)
- **배경**: 다크 스튜디오 배경 (전문 렌더링 스타일)
- **안티앨리어싱**: 자동 활성화

### 3️⃣ Open Cascade 3D 렌더러 (CAD 엔진 기반)

Open Cascade는 전문 CAD 엔진을 기반으로 한 정밀한 3D 렌더링을 제공합니다.

#### 설치 및 실행

```bash
cd renderers/open-cascade
uv sync  # 또는 pip install pythonocc-core

# 기본 사용
python renderer.py <input.dxf> <output.png>

# 예제
python renderer.py ../../sample/generated_floor_plan.dxf output.png
```

#### 기능

| 기능 | 설명 |
|------|------|
| **정밀 CAD 렌더링** | OpenCASCADE 기하학 커널 기반 |
| **레이어별 색상** | DXF 레이어 자동 인식 및 색상 적용 |
| **높이 기반 3D** | 레이어별로 정의된 높이에 따라 자동 3D화 |
| **프리즘 생성** | 2D 선을 3D 솔리드로 압출 |
| **안티앨리어싱** | 고품질 렌더링 자동 활성화 |

#### 레이어별 설정

내부적으로 정의된 레이어별 높이:

```python
STRUCT_WALLS  → 높이: 100 단위, 색상: 흰색
SHELVES       → 높이:  60 단위, 색상: 강철파란색
RETAIL_ISLANDS → 높이:  40 단위, 색상: 주황색
CHECKOUT     → 높이:  30 단위, 색상: 초록색
PILLARS      → 높이: 120 단위, 색상: 회색
기본값       → 높이:   1 단위, 색상: 흰색
```

#### 동작 방식

1. DXF 파일에서 LINE entity 추출
2. 레이어별로 그룹화
3. 각 line을 gp_Vec로 지정된 높이만큼 압출 (Prism)
4. AIS_Shape로 렌더링
5. 출력 포맷으로 저장

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

### 5️⃣ KeyShot 렌더러 (전문 건축 시각화)

KeyShot은 건축 및 제품 시각화 분야의 최고 품질 렌더러입니다.

#### 설치 및 실행

```bash
cd renderers/keyshot

# PowerShell 스크립트로 자동 실행
./render.ps1

# 또는 KeyShot API로 직접 실행
python render_dxf.py [dxf_path] [output_path]
```

#### 기능

| 기능 | 설명 |
|------|------|
| **환경 시뮬레이션** | 프리미엄 스튜디오 환경 자동 설정 |
| **자재 라이브러리** | 현실적인 건축 자재 자동 매핑 |
| **지면 반사** | 프로페셔널 리얼리즘을 위한 반사 활성화 |
| **자동 정렬** | 기하학 자동 중앙 정렬 및 접지 |
| **고해상도 출력** | 1920×1080 기본, 커스텀 해상도 지원 |

#### 자재 자동 매핑

DXF 레이어별 자재 자동 할당:

```
STRUCT_WALLS      → "Plaster White"          (석고 흰색)
SHELVES          → "Blue Anodized Aluminum" (파란 알루미늄)
RETAIL_ISLANDS   → "Orange Gloss"           (광택 주황색)
PILLARS          → "Brushed Aluminum"       (헤어라인 알루미늄)
CHECKOUT        → "Green Light Emission"   (발광 초록색)
```

#### 환경 설정

자동으로 적용되는 설정:
- **환경**: Interior_Studio.hdz (실내 스튜디오 조명)
- **배경색**: (0.05, 0.05, 0.08) - 중립적인 다크 배경
- **스냅-투-그라운드**: 자동으로 지면에 정렬
- **감마 보정**: 자동 색감 조정
- **지면 반사**: 활성화 (프리미엄 룩)

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

## 💡 실전 사용 예제

### 예제 1: 기본 파이프라인 (Excel → 모든 렌더러)

```bash
# 1단계: Excel을 DXF로 변환
python src/excel_to_dxf.py \
  --input sample/excel_blueprint2.xlsx \
  --output floor_plan.dxf \
  --cell-width 30 \
  --cell-height 30 \
  --unit cm

# 2단계: 웹에서 빠르게 확인
cd renderers/dxf-threejs
npm install && npm run dev
# → 브라우저: http://localhost:5173

# 3단계: Blender로 프리미엄 렌더링
cd ../blender
blender --background --python render_dxf.py -- \
  ../../floor_plan.dxf final_render.png \
  --cam-pitch 35 --cam-yaw 45 --material --color
```

### 예제 2: Blender 고급 렌더링 (다양한 앵글)

```bash
cd renderers/blender

# 정면도 렌더링 (높이감 있는 정면)
blender --background --python render_dxf.py -- \
  ../../floor_plan.dxf front_view.png \
  --cam-pitch 15 --cam-yaw 0 --cam-dist 1.5 \
  --material --color --text-size 12

# 사시도 렌더링 (입체감 최고)
blender --background --python render_dxf.py -- \
  ../../floor_plan.dxf isometric_view.png \
  --cam-pitch 35 --cam-yaw 45 --cam-dist 1.8 \
  --material --color

# 평면도 렌더링 (탑뷰)
blender --background --python render_dxf.py -- \
  ../../floor_plan.dxf top_view.png \
  --cam-pitch 85 --cam-yaw 0 --cam-dist 1.2 \
  --material

# 상세 선반 뷰 (가까운 거리)
blender --background --python render_dxf.py -- \
  ../../floor_plan.dxf shelf_detail.png \
  --cam-pitch 30 --cam-yaw 30 --cam-dist 0.8 \
  --material --text-size 14 --text-shadow 0.3
```

### 예제 3: 단위 변환 (mm → meters)

```bash
# Excel 입력: 모든 치수가 mm 단위
python src/excel_to_dxf.py \
  --input blueprint_mm.xlsx \
  --output blueprint_m.dxf \
  --unit cm \
  --cell-width 30 \
  --cell-height 30

# Blender에서 mm 단위 파일을 meters로 스케일
blender --background --python render_dxf.py -- \
  blueprint_m.dxf output.png \
  --unit-scale 0.01  # mm → cm 변환 (1/100)
```

### 예제 4: 텍스트 라벨 정밀 조정

```bash
blender --background --python render_dxf.py -- \
  floor_plan.dxf with_labels.png \
  --text-size 10.0 \          # 텍스트 높이
  --text-thickness 0.5 \      # 2D 굵기 (선택)
  --text-shadow 0.25 \        # 3D 깊이 (그림자)
  --material \
  --color
```

### 예제 5: Python API 직접 사용

```python
from src.excel_to_dxf import convert_excel_to_dxf

# 1. Excel 변환
convert_excel_to_dxf(
    input_excel='supermarket_layout.xlsx',
    output_dxf='floor_plan.dxf',
    cell_width=40.0,      # 40cm 격자
    cell_height=40.0,
    unit='cm'
)

# 2. 다른 프로그램에서 DXF 임포트
# 또는 Blender/Open Cascade로 자동 처리
```

### 예제 6: 배치 처리 (다중 렌더링)

```bash
#!/bin/bash
# 여러 뷰를 동시에 생성

INPUT="floor_plan.dxf"
OUTPUT_DIR="renders"
mkdir -p $OUTPUT_DIR

# Blender 배치 처리
for PITCH in 0 30 45 60; do
  for YAW in 0 45 90 135; do
    OUTPUT="${OUTPUT_DIR}/view_p${PITCH}_y${YAW}.png"
    blender --background --python renderers/blender/render_dxf.py -- \
      $INPUT $OUTPUT \
      --cam-pitch $PITCH --cam-yaw $YAW \
      --material --color
  done
done
```

### 예제 7: Open Cascade로 정확한 기하학 렌더링

```bash
cd renderers/open-cascade

# 기본 렌더링
python renderer.py ../../floor_plan.dxf blueprint_occ.png

# 또는 다른 엔지니어링 소프트웨어에서 사용할 정밀 데이터 생성
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

## 📝 Excel 입력 형식 상세 가이드

### 셀 데이터 구조

각 셀은 **2줄 형식**으로 구성됩니다:

```
┌──────────────────────┬──────────────────────┐
│ 아동언더웨어         │ 여성향내의           │
│ 3000, 800           │ 2500, 900           │
├──────────────────────┼──────────────────────┤
│ 스포츠용품           │ 신발                 │
│ 4000, 1000          │ 3500, 800           │
└──────────────────────┴──────────────────────┘
```

- **첫 번째 줄**: 영역명/상품명 (텍스트)
- **두 번째 줄**: 가로세로 치수 (숫자)

### 치수 입력 규칙

#### 형식
| 형식 | 예시 | 설명 |
|------|------|------|
| 쉼표 구분 | `3000, 800` | 가로 3000, 세로 800 |
| 공백만 | `3000 800` | 공백으로 분리 |
| x 기호 | `3000 x 800` | x를 구분자로 사용 |
| 혼합 | `3000, 800` | 모든 형식 자동 인식 |

#### 단위
- DXF 변환 시 지정한 단위를 적용 (기본값: cm)
- 모든 치수는 일관된 단위 사용 필요
- 예: `--unit mm` 사용 시 모든 값을 mm으로 입력

### 병합된 셀 (Merged Cells)

합쳐진 셀은 자동으로 인식되어 확대된 entity로 표시됩니다:

```
┌──────────────────────────────┐
│ 대형 상품 영역               │  ← 2x2 병합 셀
│ 5000, 2000                  │
└──────────────────────────────┘
```

**동작 방식:**
- 병합된 셀의 span 크기를 계산
- 각 행/열의 cell_width/height에 span 수를 곱함
- 결과: 넓은 entity가 생성됨

### Excel 파일 읽기 규칙

1. **셀 형식**: `name\n치수` 형태로 자동 파싱
2. **빈 셀**: 무시됨 (None 또는 공백)
3. **불완전한 데이터**: 무시됨 (치수 정보 없음)
4. **다국어 지원**: 한글, 영어, 기타 유니코드 문자 모두 지원
5. **텍스트 표현**: DXF의 MTEXT로 중앙 정렬 자동 적용

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
