import argparse
import openpyxl
import ezdxf
import re
import os

def cm_to_dxf_units(unit_str):
    """Map common unit strings to ezdxf units"""
    unit_map = {
        'mm': ezdxf.units.MM,
        'cm': ezdxf.units.CM,
        'm': ezdxf.units.M,
        'in': ezdxf.units.IN,
        'ft': ezdxf.units.FT
    }
    return unit_map.get(unit_str.lower(), ezdxf.units.CM)

def parse_cell(cell_value):
    """
    Parses a cell string like '아동언더웨어\n3000, 800'
    Returns: name(str), width(float), height(float) or None if parsing fails.
    """
    if cell_value is None:
        return None
    val = str(cell_value).strip()
    if not val:
        return None
        
    parts = val.split('\n')
    if len(parts) >= 2:
        name = parts[0].strip()
        dims_str = parts[-1].strip()
        # Parse numbers like "3000, 800", "3000,800", or "3000 x 800"
        dims = re.findall(r"[\d\.]+", dims_str)
        if len(dims) >= 2:
            return name, float(dims[0]), float(dims[1])
    
    return val, 0.0, 0.0

def convert_excel_to_dxf(input_excel, output_dxf, cell_width=30, cell_height=30, unit='cm'):
    # Load Excel file natively with openpyxl to access merged cells info
    wb = openpyxl.load_workbook(input_excel, data_only=True)
    sheet = wb.active
    
    # Store merged ranges: key is (row, col) of top-left cell, value is (span_rows, span_cols)
    merged_dict = {}
    skip_cells = set()
    
    for merged_range in sheet.merged_cells.ranges:
        min_col, min_row, max_col, max_row = merged_range.bounds
        merged_dict[(min_row, min_col)] = (max_row - min_row + 1, max_col - min_col + 1)
        
        # Add all cells EXCEPT the top-left one to skip_cells
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                if r == min_row and c == min_col:
                    continue
                skip_cells.add((r, c))
    
    # Create DXF
    doc = ezdxf.new('R2010')
    doc.header['$INSUNITS'] = cm_to_dxf_units(unit)
    
    # Add layer for shelves
    doc.layers.add("SHELVES", color=3) # 3 = Green
    
    msp = doc.modelspace()
    
    for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
        for col_idx, cell_value in enumerate(row, start=1):
            if (row_idx, col_idx) in skip_cells:
                continue
                
            parsed = parse_cell(cell_value)
            if not parsed:
                continue
                
            name, rect_w, rect_h = parsed
            
            # Position calculation (0-indexed logic)
            r_idx = row_idx - 1
            c_idx = col_idx - 1
            
            x_min = c_idx * cell_width
            y_max = -(r_idx * cell_height)
            
            # Check if this cell is part of a merged range
            span_rows, span_cols = merged_dict.get((row_idx, col_idx), (1, 1))
            
            # Use merged cell span size
            draw_w = span_cols * cell_width
            draw_h = span_rows * cell_height
            
            x_max = x_min + draw_w
            y_min = y_max - draw_h
            
            # Draw rectangle (LWPOLYLINE)
            points = [
                (x_min, y_min),
                (x_max, y_min),
                (x_max, y_max),
                (x_min, y_max),
                (x_min, y_min)
            ]
            msp.add_lwpolyline(points, dxfattribs={'closed': True, 'elevation': 0, 'layer': 'SHELVES', 'color': 256})
            
            # Add text (MTEXT) centered in the rectangle
            # Adjust char height so it fits well within the block
            text = msp.add_mtext(name, dxfattribs={'char_height': min(draw_h, draw_w) * 0.15, 'layer': 'SHELVES', 'color': 256})
            center_x = x_min + draw_w / 2
            center_y = y_max - draw_h / 2
            text.set_location((center_x, center_y), attachment_point=5) # 5 = Middle center
            
    doc.saveas(output_dxf)
    print(f"DXF saved to {output_dxf}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Excel blueprint to DXF")
    parser.add_argument("--input", default="sample/excel_blueprint2.xlsx", help="Input Excel file path")
    parser.add_argument("--output", default="sample/generated_floor_plan.dxf", help="Output DXF file path")
    parser.add_argument("--cell-width", type=float, default=30.0, help="Grid cell width")
    parser.add_argument("--cell-height", type=float, default=30.0, help="Grid cell height")
    parser.add_argument("--unit", type=str, default="cm", help="Unit (cm, mm, m, in, ft)")
    
    args = parser.parse_args()
    convert_excel_to_dxf(args.input, args.output, args.cell_width, args.cell_height, args.unit)
