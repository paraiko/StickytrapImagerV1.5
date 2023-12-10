import imagej
import scyjava
import os
import cv2


ijPath = "/home/paraiko/System/apps/fiji-linux64/Fiji.app"
scyjava.config.add_option('-Xmx64g')
scyjava.config.add_option('-Dplugins.dir=/home/paraiko/System/apps/fiji-linux64/Fiji.app')

#ij = imagej.init('sc.fiji:fiji:2.14.0')

ij = imagej.init(ijPath)
#ij = imagej.init('sc.fiji:fiji:2.14.0')
#ij = imagej.init('net.imagej:imagej+net.imagej:imagej-legacy')
print(ij.getVersion())

#baseimagedir = "/NAS/vhl_insect_ai/data/0035_NIL/minor-IWM_Veenstra/stickytraps/ronde1/0_fotos"
#outputdir = "/NAS/vhl_insect_ai/data/0035_NIL/minor-IWM_Veenstra/stickytraps/ronde1"
#baseimagedir = "/NAS/BeeNas/VHL_Algemeen/Projecten/006_plakplaten/0000_process_pp/fotos"
#outputdir = "/NAS/BeeNas/VHL_Algemeen/Projecten/006_plakplaten/0000_process_pp"
baseimagedir = "/mnt/data_raid10/stproc/0000_process_pp/fotos"
outputdir = "/mnt/data_raid10/stproc/0000_process_pp/0000_process_pp"
includeqr = False


filelist = os.scandir(baseimagedir)
ctr = 1

#cropCoordX = [1950, 9550, 17000]
cropCoordX = [1950, 9550, 17000]
w = 7050
h = 16500
qrposlist = [0, 1, 3]
#qrposlist = [1, 3, 4]

for each in filelist:
    if not os.path.isfile(each):
        if os.path.exists(each.path):
            stpartsfilelist = os.scandir(each.path)
            for stpart in stpartsfilelist:
                if not os.path.isfile(stpart):
                    imagedir = stpart.path
                    print (f'{ctr}: {imagedir}/{each.name}/{stpart.name}')

                    # get the qrcodes (based on current imaging sequence with 25 images, the qrs are in st_pos_00 , 02 and 03
                    imagelist = os.scandir(imagedir)
                    imgctr = 0
                    #qrposlist = [0, 1, 3]
                    qrlist = []

                    for img in imagelist:
                        if imgctr in qrposlist:
                            if includeqr:
                                qrimg = cv2.imread(img.path)
                                qrimg = cv2.cvtColor(qrimg, cv2.COLOR_BGR2GRAY)
                                #print (qrimg.shape)
                                #scale_down = 0.08  # scale down to improve qr decoding
                                qrimg = cv2.GaussianBlur(qrimg, (51, 51), cv2.BORDER_DEFAULT)
                                ret, qrimg = cv2.threshold(qrimg, 140, 255, cv2.THRESH_BINARY)
                                scale_down = 0.5  # scale down to improve qr decoding
                                #qrimg_crop = cv2.resize(qrimg[1900:4100, 2900:4912], None, fx=scale_down, fy=scale_down,
                                #                 interpolation=cv2.INTER_LINEAR)
                                #qrimg_crop = cv2.resize(qrimg[1000:5000, 2900:4912], None, fx=scale_down, fy=scale_down,
                                qrimg_crop = cv2.resize(qrimg[400:6400, 2900:4912], None, fx=scale_down, fy=scale_down,
                                                    interpolation=cv2.INTER_LINEAR)
                                #cv2.imshow("qrcrop", qrimg_crop)
                                #cv2.waitKey(500)
                                #cv2.imwrite(f'output/temp/{stpart.name}_{img.name}', qrimg_crop)
                                detect = cv2.QRCodeDetector()
                                qr, points, straight_qrcode = detect.detectAndDecode(qrimg_crop)
                                if len(qr) == 0:
                                    uuid = f'{stpart.name}_{img.name}_no-or-unreadable_qr'
                                else:
                                    uuid = f'{stpart.name}_{img.name}_{qr}'

                            else:
                                uuid = f'{stpart.name}_{img.name}'
                            print (uuid)
                            qrlist.append(uuid)
                        imgctr += 1

                    print(qrlist)

                    ij.py.run_plugin("MIST", f'imagedir={baseimagedir}/{each.name}/{stpart.name} ' + f'outfileprefix={each.name}_{stpart.name}_ ' +
                    f'outputpath={outputdir}/stitched ' +
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

                    stimg = cv2.imread(f'{outputdir}/stitched/{each.name}_{stpart.name}_stitched-0.ome.tif')
                    cv2.imwrite(f'{outputdir}/stitched/{stpart.name}_stitched-0.ome.jpg', stimg, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    print(stimg.shape)

                    stctr = 0

                    for qr in qrlist:
                        print(f'--> {qr}')
                        crpimg = stimg[0:h, cropCoordX[stctr]:cropCoordX[stctr]+w]
                        #1200dpi
                        scale_down = 0.71  # scale down to improve qr decoding
                        crpimg = stimg[0:h, cropCoordX[stctr]:cropCoordX[stctr]+w]
                        crpimg1200dpi = cv2.resize(crpimg, None, fx=scale_down,
                                            fy=scale_down, interpolation=cv2.INTER_LINEAR)
                        cv2.imwrite(f'{outputdir}/1700dpi/{qr}.jpg', crpimg, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        cv2.imwrite(f'{outputdir}/1200dpi/{qr}.jpg', crpimg1200dpi, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        stctr += 1

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
