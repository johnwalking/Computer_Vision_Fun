import sys
import os
from PIL import Image, ImageOps
Larger_Ratio = 3
Tile_Size = 50
Target_Path = './target1.jpg'
Tile_Path = './cat'

class TargetProcess:
    def __init__(self, targetpath):
        self.path = targetpath
    def getTarget(self):
        print("try to open the target image.")
        img = Image.open(self.path)
        width = img.size[0]*Larger_Ratio
        height = img.size[1]*Larger_Ratio
        larger_img = img.resize((width, height), Image.ANTIALIAS)
        #裁切無法整除的部分
        margin_w = (width % Tile_Size)/2
        margin_h = (height % Tile_Size)/2
        if margin_w >0 or margin_h>0:
            large_img = larger_img.crop((margin_w, margin_h, width - margin_w, height- margin_h))
        image_data = large_img.convert('RGB')
        
        print("open correct and get the bigger image")
        return image_data
        
        
class TileProcess:
    def __init__(self, tilepath):
        self.path = tilepath
    
    def process_tile(self, tile_path):
        try:
            img = Image.open(tile_path)
            width = img.size[0]
            height = img.size[1]
            min_length  = min(width, height)
            w_crop = (width - min_length) / 2
            h_crop = (height - min_length) / 2
            img = img.crop((w_crop, h_crop, width - w_crop, height - h_crop))
            tile_img = img.resize((Tile_Size, Tile_Size), Image.ANTIALIAS)
            return  tile_img.convert('RGB')
        except:
            return None
    
    def get_tiles(self):
        tiles = []

        print('Reading tiles from {}...'.format(self.path))
        # search the tiles directory recursively
        for root, subFolders, files in os.walk(self.path):
            for tile_name in files:
                print('Reading {:40.40}'.format(tile_name))

                tile_path = os.path.join(root, tile_name)
                tile  = self.process_tile(tile_path)
                if tile != None:
                    tiles.append(tile)

        print('Processed {} tiles.'.format(len(tiles)))
        return tiles
        
class MosaicImage:
    def __init__(self, original_img):
        self.image = Image.new(original_img.mode, original_img.size)
        self.x_tile_count = int(original_img.size[0] / Tile_Size)
        self.y_tile_count = int(original_img.size[1] / Tile_Size)
        self.total_tiles  = self.x_tile_count * self.y_tile_count

    def add_tile(self, tile_data, coords):
        img = Image.new('RGB', (Tile_Size, Tile_Size))
        img.putdata(tile_data)
        self.image.paste(img, coords)

    def save(self, path):
        self.image.save(path)
        

class TileFitter:
    def __init__(self, tiles_data):
        self.tiles_data = tiles_data

    def __get_tile_diff(self, t1, t2, bail_out_value):
        diff = 0
        for i in range(len(t1)):
            diff += ((t1[i][0] - t2[i][0])**2 + (t1[i][1] - t2[i][1])**2 + (t1[i][2] - t2[i][2])**2)
        return diff
    def get_best_fit_tile(self, img_data):
        best_fit_tile_index = None
        min_diff = sys.maxsize
        tile_index = 0

        # 逐一比對
        for tile_data in self.tiles_data:
            diff = self.__get_tile_diff(img_data, tile_data.getdata(), min_diff)
            if diff < min_diff:
                min_diff = diff
                best_fit_tile_index = tile_index
            tile_index += 1

        return best_fit_tile_index
        
def Generate_Mosaic(target, tiles):
    print("start to generate the mosaic image ：）")
    New_Balnk_Image = MosaicImage(target)
    tile_function = TileFitter(tiles)
    all_tile  =  [list(tile.getdata()) for tile in tiles]
    count = 0 
    for x in range(New_Balnk_Image.x_tile_count):
        for y in range(New_Balnk_Image.y_tile_count):
            boxCoord = (x * Tile_Size, y * Tile_Size, (x + 1) * Tile_Size, (y + 1) * Tile_Size)
            index = tile_function.get_best_fit_tile( target.crop(boxCoord).getdata())
            New_Balnk_Image.add_tile(tiles[index].getdata(), boxCoord)
            count +=1
            print("It is processing on "+str(count)+'/'+str(New_Balnk_Image.x_tile_count*New_Balnk_Image.y_tile_count))
    #存檔
    New_Balnk_Image.save('./here.jpg')
    
big = TargetProcess(Target_Path).getTarget()
tiles = TileProcess(Tile_Path).get_tiles()
Generate_Mosaic(big,tiles)