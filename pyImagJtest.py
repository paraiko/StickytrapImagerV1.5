import imagej
import scyjava
import os

ijPath = "/home/paraiko/System/apps/fiji-linux64/Fiji.app"
scyjava.config.add_option('-Xmx64g')
#ij = imagej.init(ijPath)
ij = imagej.init('sc.fiji:fiji:2.14.0')
#print(ij.getVersion())

#img_path = "/NAS/BeeNas/VHL_Algemeen/Projecten/019_foto-setup/software/StickytrapImager/input/testij/"

#ij.IJ.openImage(img_path + "st_pos_00.jpg")
#dataset = ij.io().open(img_path + "st_pos_00.jpg")
#ij.py.show(dataset)

# def dump_info(image):
#     """A handy function to print details of an image object."""
#     name = image.name if hasattr(image, 'name') else None # xarray
#     if name is None and hasattr(image, 'getName'): name = image.getName() # Dataset
#     if name is None and hasattr(image, 'getTitle'): name = image.getTitle() # ImagePlus
#     print(f" name: {name or 'N/A'}")
#     print(f" type: {type(image)}")
#     print(f"dtype: {image.dtype if hasattr(image, 'dtype') else 'N/A'}")
#     print(f"shape: {image.shape}")
#     print(f" dims: {image.dims if hasattr(image, 'dims') else 'N/A'}")

#dump_info(dataset)

# imagedir /NAS/vhl_insect_ai/data/0033_Michella-RUG/test_2023-05-16/128006_030423_A/sw_bot
#baseimagedir = "/NAS/vhl_insect_ai/data/0033_Michella-RUG/Sync_folder/01_data"
#outputpath = "/NAS/vhl_insect_ai/data/0033_Michella-RUG/processing_pipeline/v03/macrotest/op"

baseimagedir = "/NAS/BeeNas/VHL_Algemeen/Projecten/006_plakplaten/0035_NIL/minor-IWM_Veenstra/ronde1"
outputpath = "/NAS/BeeNas/VHL_Algemeen/Projecten/006_plakplaten/0035_NIL/minor-IWM_Veenstra/ronde1_stitched"

filelist = os.scandir(baseimagedir)
ctr = 1

for each in filelist:
    if not os.path.isfile(each):
        if os.path.exists(each.path):
            stpartsfilelist = os.scandir(each.path)
            for stpart in stpartsfilelist:
                if not os.path.isfile(stpart):
                    imagedir = stpart.path
                    print (f'{ctr}: {imagedir}/{each.name}/{stpart.name}')

                    ij.py.run_plugin("MIST", f'imagedir={baseimagedir}/{each.name}/{stpart.name} ' + f'outfileprefix={each.name}_{stpart.name}_ ' +
                    f'outputpath={outputpath} ' +
                    "globalpositionsfile=/NAS/vhl_insect_ai/data/0033_Michella-RUG/test_2023-05-16/pos/128006_030423_A_no-topglobal-positions-0.txt \
                    filenamepattern=st_pos_{pp}.jpg planpath=/home/paraiko/lib/fftw/fftPlans fftwlibrarypath=/home/paraiko/lib/fftw stagerepeatability=0 \
                    unit=MICROMETER unitx=14.11 unity=14.11 programtype=AUTO numcputhreads=64 gridwidth=5 gridheight=5 starttile=0 \
                    filenamepatterntype=SEQUENTIAL gridorigin=UL assemblefrommetadata=true assemblenooverlap=false \
                    numberingpattern=HORIZONTALCOMBING startrow=0 startcol=0 extentwidth=5 extentheight=5 timeslices=0 istimeslicesenabled=false \
                    displaystitching=false outputfullimage=true outputmeta=true outputimgpyramid=false blendingmode=LINEAR blendingalpha=10.0 compressionmode=LZW \
                    loadfftwplan=true savefftwplan=true fftwplantype=MEASURE fftwlibraryname=libfftw3 fftwlibraryfilename=libfftw3.dll \
                    horizontaloverlap=36.0 verticaloverlap=39.0 numfftpeaks=10 overlapuncertainty=5.0 isusedoubleprecision=true \
                    isusebioformats=false issuppressmodelwarningdialog=false isenablecudaexceptions=false \
                    translationrefinementmethod=SINGLE_HILL_CLIMB numtranslationrefinementstartpoints=16 headless=false loglevel=MANDATORY debuglevel=NONE")

                    ctr += 1


# for each in filelist:
#     if not os.path.isfile(each):
#         if os.path.exists(each.path):
#             stpartsfilelist = os.scandir(each.path)
#             for stpart in stpartsfilelist:
#                 if not os.path.isfile(stpart):
#                     imagedir = stpart.path
#                     print (f'{ctr}: {imagedir}/{each.name}/{stpart.name}')
#
#                     ij.py.run_plugin("MIST", f'imagedir=/NAS/vhl_insect_ai/data/0033_Michella-RUG/Sync_folder/01_data/{each.name}/{stpart.name} ' + f'outfileprefix={each.name}_{stpart.name}_ ' +
#                     "outputpath=/NAS/vhl_insect_ai/data/0033_Michella-RUG/temp \
#                     globalpositionsfile=/NAS/vhl_insect_ai/data/0033_Michella-RUG/test_2023-05-16/pos/128006_030423_A_no-topglobal-positions-0.txt \
#                     filenamepattern=st_pos_{pp}.jpg planpath=/home/paraiko/lib/fftw/fftPlans fftwlibrarypath=/home/paraiko/lib/fftw stagerepeatability=0 \
#                     unit=MICROMETER unitx=14.11 unity=14.11 programtype=AUTO numcputhreads=64 gridwidth=5 gridheight=5 starttile=0 \
#                     filenamepatterntype=SEQUENTIAL gridorigin=UL assemblefrommetadata=true assemblenooverlap=false \
#                     numberingpattern=HORIZONTALCOMBING startrow=0 startcol=0 extentwidth=5 extentheight=5 timeslices=0 istimeslicesenabled=false \
#                     displaystitching=false outputfullimage=true outputmeta=true outputimgpyramid=false blendingmode=LINEAR blendingalpha=10.0 compressionmode=LZW \
#                     loadfftwplan=true savefftwplan=true fftwplantype=MEASURE fftwlibraryname=libfftw3 fftwlibraryfilename=libfftw3.dll \
#                     horizontaloverlap=36.0 verticaloverlap=39.0 numfftpeaks=10 overlapuncertainty=5.0 isusedoubleprecision=true \
#                     isusebioformats=false issuppressmodelwarningdialog=false isenablecudaexceptions=false \
#                     translationrefinementmethod=SINGLE_HILL_CLIMB numtranslationrefinementstartpoints=16 headless=false loglevel=MANDATORY debuglevel=NONE")
#
#                     ctr += 1
