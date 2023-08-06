module_description = """
--- telenvi.GeoIm ---
Use GeoIm objects to read only once a raster file array.
then make crops, compute optical indexes or statisticals
data from this array, with geo attributes under the hand
"""

# telenvi modules
import raster_tools as rt

# Standard libraries
import os

# Data libraries
import numpy as np
from matplotlib import pyplot as plt

# Geo libraries
import shapely
import geopandas as gpd

# Image processing libraries
from PIL import Image, ImageEnhance

class GeoIm:

    def __init__(self, target, array=None):

        if type(array) != np.ndarray :
            self.ds = rt.getDs(target)
            self._array = self.ds.ReadAsArray()

        elif type(array) == np.ndarray:
            ds = rt.getDs(target)

            # First we check dataset and array compatibility
            if not rt.getShape(ds) == rt.getShape(array):
                print(f"dataset shape {rt.getShape(ds)} != array shape {rt.getShape(array)}")
                return None

            # Then we assign ds and array as geoim instance attributes
            self.ds = ds
            self._array = array

    def getArray(self):
        return self._array        

    def updateDs(self, newArray):
        new_ds = rt.create(
            newArray,
            "",
            self.getOrigin()[0],
            self.getOrigin()[1],
            self.getPixelSize()[0],
            self.getPixelSize()[1],
            self.ds.GetProjection())
        self.ds = new_ds

    def setArray(self, newArray):
        """
        this method is called each time we change the geoim instance array
        """

        # If the geoim array change, the array contained in the instance.dataset must change to
        # So, we create a new dataset from this new array
        self.updateDs(newArray)
        self._array = newArray

    def delArray(self):
        pass

    array = property(getArray, setArray, delArray)
    
    def __add__(self, n):
        if type(n) == GeoIm:
            n = n.array
        return GeoIm(self.ds, self.array + n)

    def __sub__(self, n):
        if type(n) == GeoIm:
            n = n.array
        return GeoIm(self.ds, self.array - n)
    
    def __mul__(self, n):
        if type(n) == GeoIm:
            n = n.array
        return GeoIm(self.ds, self.array * n)
    
    def __truediv__(self, n):
        if type(n) == GeoIm:
            n = n.array
        return GeoIm(self.ds, self.array / n)

    def __pow__(self, n):
        if type(n) == GeoIm:
            n = n.array
        return GeoIm(self.ds, self.array ** n)

    def __repr__(self):
        print(
f"""pixel size : {self.getPixelSize()}
origin     : {self.getOrigin()}
bands      : {self.getShape()[0]}
rows       : {self.getShape()[1]}
columns    : {self.getShape()[2]}
SCR epsg   : {self.getEpsg()}
SCR name   : {self.getProjName()}
array type : {self.array.dtype}""")
        return ""

    def copy(self):
        return GeoIm(self.ds, self.array)

    def getOrigin(self):
        return rt.getOrigin(self.ds)

    def getGeoBounds(self):
        return rt.getGeoBounds(self.ds)

    def getPixelSize(self):
        return rt.getPixelSize(self.ds)
    
    def getShape(self):
        return rt.getShape(self.ds)
    
    def drawGeomExtent(self):
        return rt.drawGeomExtent(self.ds)
    
    def getEpsg(self):
        return rt.getEpsg(self.ds)
    
    def getProjName(self):
        return rt.getProjName(self.ds)
    
    def getJsonProj(self):
        return rt.getJsonProj(self.ds)

    def cropFromVector(self, vector, polygon = 0, verbose = False, inplace=False):
        """
        vector : shapely.Geometry.Polygon or str - path to a shapefile
        polygon : id of the feature, if vector is a shapefile
        """

        # We get the polygon geo extent
        if type(vector) == str:
            layer = gpd.read_file(vector)
            bounds = layer["geometry"][polygon].bounds
        
        elif type(vector) == tuple:
            bounds = vector

        elif type(vector) == shapely.geometry.polygon.Polygon:
            bounds = vector.bounds

        # And we cut the geoim on it
        return self.cropFromBounds(bounds, verbose = verbose, inplace = inplace)

    def cropFromRaster(self, model, verbose = False, inplace=False):

        # We get the croper dataset and his geo extent
        modelBounds = rt.getGeoBounds(rt.getDs(model))

        # And we cut the geoim on it
        return self.cropFromBounds(modelBounds, verbose = verbose, inplace = inplace)

    def cropFromBounds(self, bounds, verbose = False, inplace=False):

        # We get the matrixian coordinates of the intersection area between the raster and the box
        crop_indexes = rt.spaceBox_to_arrayBox(bounds, self.ds, self.array)

        # And we cut the geoim on it
        return self.cropFromIndexes(crop_indexes, verbose = verbose, inplace = inplace)

    def cropFromIndexes(self, indexes, verbose=False, inplace=False):
        """
        indexes : tuple - (row1, col1, row2, col2)
        """        

        # We create a copy of the geoim instance if not inplace arg
        target = self
        if not inplace:
            target = self.copy()

        # Give a name to the indexes
        row1, col1, row2, col2 = indexes

        # Extract the array part between thoses indexes
        new_array = target.array[row1:row2, col1:col2]

        # Assign this new array to the geoim
        target.setArray(new_array)

        return target        

    def makeMosaic(self, thumbsY=2, thumbsX=2):
        """
        build many geoims side by side from the instance
        :params:
            nbSquaresByAx : int
                default : 2
                the number of cells to cells along the X size and the Y size
                from the current instance. 2 means you will have 4 GeoIms in
                return. The current instance will be split in 2 lines and 2 cols.

        :returns:
            mosaic : list
                a list of GeoIms
        """

        cells_nRows=int(self.getShape()[1]/thumbsY)
        cells_nCols=int(self.getShape()[2]/thumbsX)

        mosaic=[]
        for row in range(thumbsY):
            for col in range(thumbsX):
                row1=cells_nRows * row
                col1=cells_nCols * col
                row2=row1 + cells_nRows
                col2=col1 + cells_nCols
                mosaic.append(self.cropFromIndexes((col1, row1, col2, row2)))

        return mosaic

    def splitBands(self):
        """
        send a list of geoims monospectral for each band in the current instance
        """
        nBands=self.getShape()[0]

        if nBands == 1:
            return self.copy()

        elif nBands > 1:
            bands=[]
            for band in self.array:
                new=GeoIm(self.ds, band)
                new.updateDs()
                bands.append(new)

            return bands

    def show(self, index=None, band=0, colors="viridis"):

        """
        :descr:
            display one band of the GeoIm
        
        :params:
            index : tuple
                default : None - all the image is displayed.
                alternative : (firstColumn, firstRow, lastColumn, lastRow)
                described a matrixian area to display

            band : int
                default=0
                the index of the band to display if the geoim is multispectral

        :returns:
            None
        """

        # Compute nCols and nRows
        nBands, nRows, nCols=self.getShape()
        if index == None:
            col1, row1, col2, row2=0, 0, nCols-1, nRows-1
        else:
            col1, row1, col2, row2=index

        # Plot
        if nBands > 1:
            plt.imshow(self.array[band][row1:row2, col1:col2], cmap=colors)

        else:
            plt.imshow(self.array[row1:row2, col1:col2], cmap=colors)

        plt.show()
        plt.close()
        return None

    def save(self, outpath, driverName="GTiff"):
        rt.write(self.ds, outpath, driverName)

    def rgbVisual(self, colorMode=[0,1,2], resize_factor=1, brightness=1, show=False, path=None):

        """
        :descr:
            display 3 bands of the GeoIm in RGB mode
        
        :params:
            colorMode : list or tuple
                the order of the 3 bands to display

            resize_factor : int
                default : 1
                allow to "zoom" on the image if the area is to 
                small to be correctly visualized

            brightness : int
                default : 1
                allow to improve the RGB composition brightness. 

            show : boolean
                default : False
                if True,the image is displayed in the os system image reader.
                when this method is called from a Jupyter Notebook, 
                there's no need to set it on True
            
            path : str
                default : None
                if not None, the image is not displayed but saved to this path

        :returns:
            rgb : PIL.Image
                a RGB image        
        """

        _, nRows, nCols=self.getShape()

        if len(self.array.shape) != 3:
            raise AttributeError("You need a GeoIm in 3 dimensions to display a GeoIm in RGB")

        if self.array.shape[0] < 3:
            raise AttributeError("The GeoIm have only {} channel and we need 3 channels to display it in RGB")

        # Convert array into RGB array

        # Unpack the RGB components is separates arrays
        r=self.array[colorMode[0]]
        g=self.array[colorMode[1]]
        b=self.array[colorMode[2]]

        # data normalization between [0-1]
        r_norm=(r - r[r!=0].min()) / (r.max() - r[r!=0].min()) * 255
        g_norm=(g - g[g!=0].min()) / (g.max() - g[g!=0].min()) * 255
        b_norm=(b - b[b!=0].min()) / (b.max() - b[b!=0].min()) * 255

        # RGB conversion
        # --------------

        # Create a target array
        rgb_ar= np.zeros((nRows, nCols, 3))

        # For each cell of the "board"
        for row in range(nRows):
            for col in range(nCols):

                # We get the separate RGB values in each band
                r=r_norm[row][col]
                g=g_norm[row][col]
                b=b_norm[row][col]

                # We get them together in little array
                rgb_pixel= np.array([r,g,b])

                # And we store this little array on the board position
                rgb_ar[row][col]=rgb_pixel

        rgb=Image.fromarray(np.uint8(rgb_ar))

        # Adjust size
        rgb=rgb.resize((nCols * resize_factor, nRows * resize_factor))

        # Adjust brightness
        enhancer=ImageEnhance.Brightness(rgb)
        rgb=enhancer.enhance(brightness)

        # Display
        if show:
            rgb.show()

        # Save
        if path != None:
            rgb.save(path)

        # Return PIL.Image instance
        return rgb
