# a greedy bin-packing approach with adaptive vertical spanning optimization
# L+P, P+P, L alone, P can sit in 2 rows so two single-height portraits can sit next to it

from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict

class PhotoCollage:
    def __init__(self, target_width=1200, row_height=400):
        self.target_width = target_width
        self.row_height = row_height
    
    def create_layout(self, num_landscape, num_portrait):
        # special case - single portrait
        if num_landscape == 0 and num_portrait == 1:
            return [{'label': 'P1', 'orientation': 'portrait', 'row': 0, 'col': 'full', 'row_span': 1}]
        
        items = []
        l_idx = 1
        p_idx = 1
        curr_row = 0
        remaining_l = num_landscape
        remaining_p = num_portrait
        
        # first, pair landscapes with portraits
        while remaining_l > 0 and remaining_p > 0:
            items.append({
                'label': f'L{l_idx}',
                'orientation': 'landscape',
                'row': curr_row,
                'col': 'left',
                'row_span': 1
            })
            items.append({
                'label': f'P{p_idx}',
                'orientation': 'portrait',
                'row': curr_row,
                'col': 'right',
                'row_span': 1
            })
            l_idx += 1
            p_idx += 1
            curr_row += 1
            remaining_l -= 1
            remaining_p -= 1
        
        # handle remaining portraits
        if remaining_p > 0:
            while remaining_p >= 2:
                items.append({
                    'label': f'P{p_idx}',
                    'orientation': 'portrait',
                    'row': curr_row,
                    'col': 'left',
                    'row_span': 1
                })
                
                if remaining_p == 3:
                    # use vertical stacking for odd portrait
                    items.append({
                        'label': f'P{p_idx + 1}',
                        'orientation': 'portrait',
                        'row': curr_row,
                        'col': 'right',
                        'row_span': 2
                    })
                    p_idx += 2
                    curr_row += 1
                    
                    items.append({
                        'label': f'P{p_idx}',
                        'orientation': 'portrait',
                        'row': curr_row,
                        'col': 'left',
                        'row_span': 1
                    })
                    p_idx += 1
                    curr_row += 1
                    remaining_p -= 3
                else:
                    items.append({
                        'label': f'P{p_idx + 1}',
                        'orientation': 'portrait',
                        'row': curr_row,
                        'col': 'right',
                        'row_span': 1
                    })
                    p_idx += 2
                    curr_row += 1
                    remaining_p -= 2
            
            if remaining_p == 1:
                items.append({
                    'label': f'P{p_idx}',
                    'orientation': 'portrait',
                    'row': curr_row,
                    'col': 'left',
                    'row_span': 1
                })
                curr_row += 1
        
        # add remaining landscapes
        while remaining_l > 0:
            items.append({
                'label': f'L{l_idx}',
                'orientation': 'landscape',
                'row': curr_row,
                'col': 'full',
                'row_span': 1
            })
            l_idx += 1
            curr_row += 1
            remaining_l -= 1
        
        return items
    
    def create_placeholder_image(self, width, height, label, orientation):
        bg_color = (100, 149, 237) if orientation == 'landscape' else (255, 160, 122)
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            font_size = min(width, height) // 6
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        x = (width - text_w) // 2
        y = (height - text_h) // 2
        
        draw.text((x+2, y+2), label, fill=(0, 0, 0), font=font)
        draw.text((x, y), label, fill=(255, 255, 255), font=font)
        draw.rectangle([0, 0, width-1, height-1], outline=(255, 255, 255), width=3)
        
        return img
    
    def create_collage(self, num_landscape, num_portrait, output_path='collage.jpg', spacing=4):
        if num_landscape == 0 and num_portrait == 0:
            raise ValueError("Need at least one image")
        
        items = self.create_layout(num_landscape, num_portrait)
        max_row = max(item['row'] + item['row_span'] for item in items)
        total_height = max_row * self.row_height + (max_row - 1) * spacing
        
        collage = Image.new('RGB', (self.target_width, total_height), 'white')
        
        print("\nCollage Layout:")
        print("=" * 50)
        
        for item in items:
            label = item['label']
            orientation = item['orientation']
            row = item['row']
            col = item['col']
            row_span = item['row_span']
            
            y_pos = row * (self.row_height + spacing)
            height = row_span * self.row_height + (row_span - 1) * spacing
            
            if col == 'full':
                x_pos = 0
                width = self.target_width
                print(f"Row {row + 1}: {label} (full width)")
            elif col == 'left':
                x_pos = 0
                width = (self.target_width * 2) // 3 if orientation == 'landscape' else self.target_width // 2
                span_txt = f", spans {row_span} rows" if row_span > 1 else ""
                print(f"Row {row + 1}: {label} (left{span_txt})")
            else:  # right
                left_item = next((i for i in items if i['row'] == row and i['col'] == 'left'), None)
                if left_item and left_item['orientation'] == 'landscape':
                    x_pos = (self.target_width * 2) // 3 + spacing
                    width = self.target_width - x_pos
                else:
                    x_pos = self.target_width // 2 + spacing
                    width = self.target_width - x_pos
                
                span_txt = f", spans {row_span} rows" if row_span > 1 else ""
                print(f"         {label} (right{span_txt})")
            
            img = self.create_placeholder_image(width, height, label, orientation)
            collage.paste(img, (x_pos, y_pos))
        
        print("=" * 50)
        collage.save(output_path, quality=95)
        print(f"\n✓ Collage saved to {output_path}")
        print(f"✓ Dimensions: {self.target_width}x{total_height}px")
        print(f"✓ Total rows: {max_row}")
        print(f"✓ Total images: {num_landscape + num_portrait}")


def main():
    print("=" * 50)
    print("Smart Photo Collage Generator")
    print("=" * 50)
    
    try:
        num_landscape = int(input("\nEnter number of landscape images: "))
        num_portrait = int(input("Enter number of portrait images: "))
        
        if num_landscape < 0 or num_portrait < 0:
            print("Error: Numbers must be non-negative!")
            return
        
        if num_landscape == 0 and num_portrait == 0:
            print("Error: At least one image is required!")
            return
        
        collage_maker = PhotoCollage(target_width=1200, row_height=400)
        
        output_file = input("\nEnter output filename (default: collage.jpg): ").strip()
        if not output_file:
            output_file = "collage.jpg"
        
        collage_maker.create_collage(num_landscape, num_portrait, output_path=output_file, spacing=4)
        
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")


if __name__ == "__main__":
    main()
