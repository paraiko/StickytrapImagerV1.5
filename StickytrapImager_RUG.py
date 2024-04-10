# -*- coding: utf-8 -*-
"""
Created on Sun Apr 16 2022
@author: Ate
@version: 1.0
"""
import webbrowser
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports
import os
from pathlib import Path
import time
import gphoto2 as gp
import cv2
import re
from datetime import date as date


class Main:

    def __init__(self, root):
        root.winfo_toplevel().title('Taskforce Kleine biodiversiteit - InsectImager -')
        mainframe = ttk.Frame(root, padding="3 3 3 3")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        tabcontrol = ttk.Notebook(mainframe)
        sett = ttk.Frame(tabcontrol)
        #wps = ttk.Frame(tabcontrol)
        st = ttk.Frame(tabcontrol)
        mvt = ttk.Frame(tabcontrol)
        hlp = ttk.Frame(tabcontrol)

        tabcontrol.add(sett, text='settings')
        #tabcontrol.add(wps, text='well-plates')
        tabcontrol.add(st, text='sticky-traps')
        tabcontrol.add(mvt, text='move xy-table')
        tabcontrol.add(hlp, text='help/about')
        def update_tabs():
            #self.Wellplate = Wellplate(wps, settings)
            self.Stickytrap = Stickytrap(st, settings)
        tabcontrol.bind('<<NotebookTabChanged>>', lambda e: update_tabs())
        tabcontrol.grid(column=0, row=0)

        settings = Settings()
        SettingsTab(sett, settings)
        Move(mvt, settings)
        Help(hlp)

        # add some padding to all widgets
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        root.mainloop()

class Settings:

    """Class to hold settings variables to be re-used at other parts of the app"""

    nr_wp = 1  # number of wellplates to scan
    wp_type = 6  # well plate type, number of wells per plate
    # the path were imaged wells can be saved
    safe_path = os.path.join(Path.home(), "InsectImager/data/")
    safe_temp_path = os.path.join(safe_path, ".tempfiles/")

    project_name = "0033_RUG_ML"   # project name
    sample_name = str(date.today())  # sample name
    sample_nr =""
    project_sample_path = ""

    prj_fn_add = True  # setting to add the project ande sample name to the filename (default = yes)
    append_files = True  # setting increment platenames when existing files are present in the folder

    #############################
    # camera details            #
    #############################
    # camera used is Nikon D800 interfaced via libgphoto2
    # variable for camera_object
    cam = None
    cam_connected = False

    ################################
    # y y table serial connection  #
    ################################
    comport_list = None
    comport = "/dev/ttyUSB0"
    # variable for serial object
    ser = None
    xy_connected = connected = False

    #############################
    #  y y table details        #
    #############################
    # xy-table is a modified laser engraver * (Atomstack A10)
    #
    # usb connection details (not currently used):
    # ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
    # xy_usb_vendor_ID = 0x1a86  #QinHeng Electronics
    # xy_usb_product_ID = 0x7523 #HL-340 USB-Serial adapter

    # xytable dimensions (mm)
    xy_x_max = 409.00
    xy_y_max = 759.00
    # speed setting, officially F = in mm/(or inch) per min
    # in practice, based on calibration it seems to be mm/min roughly divided by 1.4
    # ( max speed probably roughly 100 mm/sec = around F8300)
    xy_f_speed = 8300
    xy_f_corr_fact = 1.4
    cam_capture_delay = 3

    # default stickytraps no overlap
    caps_per_st = 4
    nr_crops_st = 1
    xy_st_coords = [[300, 40],[300, 85],[300, 130]]

    caps_per_big_st = 42
    #xy_big_st_coords = [[5, 0], [75, 0]]
    xy_big_st_coords = [[5, 0], [75, 0], [145, 0],
    			[5, 107], [75, 107], [145, 107],
     			[5, 209], [75, 209], [145, 209],
     			[5, 311], [75, 311], [145, 311],
     			[5, 413], [75, 413], [145, 413],
    			[5, 515], [75, 515], [145, 515],
     			[5, 618], [75, 618], [145, 618],
                [260, 618], [330, 618], [400, 618],
                [260, 515], [330, 515], [400, 515],
                [260, 413], [330, 413], [400, 413],
                [260, 311], [330, 311], [400, 311],
                [260, 209], [330, 209], [400, 209],
                [260, 107], [330, 107], [400, 107],
                [260, 0], [330, 0], [400, 0]]
    #st_posnames = ["A_01", "A_02"]
    st_posnames = ["A_01","A_02","A_03",
                   "A_04","A_05","A_06",
                   "A_07","A_08","A_09",
                   "A_10","A_11","A_12",
                   "A_13","A_14","A_15",
                   "A_16","A_17","A_18",
                   "A_19","A_20","A_21",
                   "B_19","B_20","B_21",
                   "B_16","B_17","B_18",
                   "B_13","B_14","B_15",
                   "B_10","B_11","B_12",
                   "B_07","B_08","B_09",
                   "B_04","B_05","B_06",
                   "B_01","B_02","B_03"]

    def __init__(self):
        self.comport_list = self.find_comports()
        # self.create_safe_path()

        # check if the sample folder (date of today) exists and create if not.
        subdirectories = []
        for dirpath, dirnames, filenames in os.walk(os.path.join(self.safe_path, self.project_name)):
            subdirectories.append(dirnames)

        print(subdirectories)

        if self.sample_name not in subdirectories:
            print ("do I get here")
            try:
                os.makedirs(os.path.join(self.safe_path, self.project_name, self.sample_name), exist_ok=True)
            except FileExistsError:
                # directory already exists
                pass

        # create autosamplename based on date and incremental nr.
        subdirectories = []
        for dirpath, dirnames, filenames in os.walk(os.path.join(self.safe_path, self.project_name, self.sample_name)):
            # Append the current subdirectory to the list
            subdirectories.append(dirnames)

        print(subdirectories)
        subdir_string = subdirectories[0]
        subdir_numbers = [int(num) for num in subdir_string if num.isdigit()]

        # check if numbered subdir exists, if not create 001, if yes increment and create
        if len(subdir_numbers) == 0:
            self.sample_nr = "001"

        else:
            s_nr = max(subdir_numbers) + 1
            self.sample_nr = str(s_nr).zfill(3)

        self.project_sample_path = os.path.join(self.safe_path, self.project_name, self.sample_name, self.sample_nr)
        print(self.project_sample_path)

    def create_safe_path(self):
        try:
            # also create a temp folder for downloaded camera images
            #os.makedirs(self.safe_path, exist_ok=True)
            os.makedirs(self.project_sample_path, exist_ok=True)
            os.makedirs(self.safe_temp_path, exist_ok=True)
        except FileExistsError:
            # directory already exists
            pass


    def create_project_sample_path(self):
        try:
            # also create a temp folder for downloaded camera images
            #self.project_sample_path = os.path.join(self.safe_path, self.project_name, self.sample_name)
            os.makedirs(os.path.join(self.project_sample_path), exist_ok=True)
        except FileExistsError:
            # directory already exists
            pass

    def find_comports(self):
        comports = list()
        for i in serial.tools.list_ports.comports():
            # print(type(serial.build_binary.list_ports.comports()))
            # d = serial.Serial(i[0])
            # print ('%s - ' % i[0] , d.isOpen())
            # print(i[0])
            # print(i[1])
            comports.append(i[0])
        return comports

    # port='/dev/ttyUSB0'
    def open_serial_connection(self, baudrate=115200):

        try:
            ser = serial.Serial(self.comport, baudrate)
            time.sleep(2)  # delay to allow for time to pass communication over the bus.
            self.xy_connected = True
            print("connection " + str(ser))
            return ser, True

        except:
            messagebox.showwarning("connection failure", "Could not connect to xy table")

    def close_serial_connection(self, ser):

        time.sleep(2)  # delay to allow for time to pass communication over the bus.
        ser.close()
        print("closed serial connection")

    def initialize_xy(self):
        # set gcode coordinate system to mm (not inch)
        self.ser.write(bytes("G21\n", 'utf-8'))
        # perform homing cycle

class SettingsTab:

    def __init__(self, parent, settings):

        # assign settings object to store variables in the app
        self.s = settings
        self.s.create_safe_path()

        # row 0
        frame = ttk.Frame(parent, padding="10 10 10 10")
        frame.grid(column=0, row=0, sticky=(N, W, E, S))

        # row 1
        dfframe = ttk.LabelFrame(frame, text="Data folder: ", padding="10 10 10 10")
        dfframe.grid(column=0, row=0, sticky=(N, W, E, S))

        # TODO fix error when empty string is returned on cancel
        # open button
        open_button = ttk.Button(
            dfframe,
            text='Select data folder',
            command=self.select_folder
        )
        # self.s.safe_path = "~/wellplate_scanner/samples"
        ttk.Label(dfframe, text="Current data folder: ").grid(row=0, column=0, pady=5, sticky=W)
        self.safe_path_lbl = ttk.Label(dfframe, text=self.s.safe_path)
        self.safe_path_lbl.grid(row=0, column=1)
        open_button.grid(row=1, column=0, pady=5, sticky=W)

        spframe = ttk.LabelFrame(frame, text="Sample name: ", padding="10 10 10 10")
        spframe.grid(row=1, column=0, sticky=(N, W, E, S))

        ttk.Label(spframe, text="Project name: ", padding="5 5 5 5").grid(row=0, column=0, sticky=W)
        ttk.Label(spframe, text="Date: ", padding="5 5 5 5").grid(row=1, column=0, sticky=W)
        ttk.Label(spframe, text="sample number: ", padding="5 5 5 5").grid(row=2, column=0, sticky=W)

        self.validate_entry_wrapper = (root.register(self.validate_entry), '%P')

        # project name
        self.prj_name = StringVar()
        self.prj_name_entry = ttk.Entry(spframe, textvariable=self.prj_name, validate='key',
                                        validatecommand=self.validate_entry_wrapper)
        self.prj_name_entry.grid(row=0, column=1)
        self.prj_name.set(self.s.project_name)

        def callback_upd_prj_name(var, index, mode):
            self.upd_prj_name()
        self.prj_name.trace_add("write", callback_upd_prj_name)

        #date
        self.sp_name = StringVar()
        self.sp_name_entry = ttk.Entry(spframe, textvariable=self.sp_name, validate='key',
                                       validatecommand=self.validate_entry_wrapper)
        self.sp_name_entry.grid(row=1, column=1)
        self.sp_name.set(self.s.sample_name)

        def callback_upd_sp_name(var, index, mode):
            self.upd_sp_name()

        self.sp_name.trace_add("write", callback_upd_sp_name)

        # number
        self.sp_nr = StringVar()
        self.sp_nr_entry = ttk.Entry(spframe, textvariable=self.sp_nr, validate='key',
                                        validatecommand=self.validate_entry_wrapper)
        self.sp_nr_entry.grid(row=2, column=1)
        self.sp_nr.set(self.s.sample_nr)

        def callback_upd_sp_nr(var, index, mode):
            self.upd_sp_nr()

        self.sp_nr.trace_add("write", callback_upd_sp_nr)




        self.prj_fn_add = BooleanVar()
        self.prj_fn_add_check = ttk.Checkbutton(spframe,
                                                text="Add sample and project name to the filename",
                                                variable=self.prj_fn_add,
                                                state="True",
                                                command=self.upd_prjfn_add_check)
        self.prj_fn_add_check.grid(row=3, column=0, columnspan=2, pady=5, sticky=W)
        self.prj_fn_add.set(True)



        ###################################################################################
        # Devices (2nd column in interface
        ###################################

        # XY table
        # row 0 --> ### column 1
        xytableframe = ttk.LabelFrame(frame, text="XY-table ", padding="10 10 10 10")
        xytableframe.grid(column=1, row=0, sticky=(N, W, E, S))

        self.xy_table = StringVar()
        self.xy_comports = ttk.Combobox(xytableframe,
                                        state="readonly",
                                        values=self.s.comport_list,
                                        textvariable=self.xy_table)
        self.xy_comports.grid(row=0, column=0)
        self.xy_comports.bind("<<ComboboxSelected>>", lambda e: self.xy_comports.selection_clear())
        if len(self.s.comport_list) > 0:
            # self.xy_comports['value'] = self.s.comport_list[0]
            self.xy_comports.set(self.s.comport_list[0])

        self.connect_xy_button = ttk.Button(xytableframe, text='Connect XY-table', command=self.open_xytable_window)
        self.connect_xy_button.grid(row=1, column=0, sticky=W, pady=5)
        if self.s.xy_connected:
            self.connect_xy_button['state'] = DISABLED

        # Camera
        # row 1 --> ### column 1
        cameraframe = ttk.LabelFrame(frame, text="Camera ", padding="10 10 10 10")
        cameraframe.grid(column=1, row=1, sticky=(N, W, E, S))

        self.connect_camera_button = ttk.Button(cameraframe, text='Connect camera', command=self.connect_camera)
        self.connect_camera_button.grid(row=0, column=0, sticky=W, pady=5)
        if self.s.cam_connected:
            self.connect_camera_button['state'] = DISABLED

        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def select_folder(self):
        self.s.safe_path = fd.askdirectory(title="Select data folder", mustexist=TRUE)
        self.safe_path_lbl['text'] = self.s.safe_path

    def upd_wp_nr(self):
        self.s.nr_wp = self.wpnr.get()
        # print(self.s.nr_wp)

    def upd_wp_type(self):
        self.s.wp_type = self.wptype.get()
        # print(self.s.wp_type)

    def upd_prj_name(self):
        self.s.project_name = str(self.prj_name.get())
        # print(self.s.project_name)

    def upd_sp_name(self):
        self.s.sample_name = str(self.sp_name.get())
        # print(self.s.sample_name)

    def upd_sp_nr(self):
        self.s.sample_nr = str(self.sp_nr.get())
        # print(self.s.sample_name)

    def upd_prjfn_add_check(self):
        self.s.prj_fn_add = self.prj_fn_add.get()
        print(self.prj_fn_add)
        print(self.s.prj_fn_add)

    def validate_entry(self, newval):
        # allow only alphanumeric character, _ and - and not empty
        return re.match("^[a-zA-Z0-9_-]*$", newval) is not None

    def connect_camera(self):
        self.s.cam = Camera(self.s)
        self.s.cam.initialize()
        print(self.s.cam.error)
        if self.s.cam.error == 0:
            self.s.cam_connected = True
            self.connect_camera_button['state'] = DISABLED
            self.connect_camera_button['text'] = "Camera connected"
        elif self.s.cam.error == -60:
            messagebox.showinfo("Communication failure", "Camera detected but cannot connect.\n\n"
                                                         "Is it in use by another program, or mounted?")
        else:
            messagebox.showerror("Connection failure", "Cannot connect to the camera.")

    def open_xytable_window(self):

        answer = messagebox.askyesno("Connect XY-table",
                                     "Home the holder\n(x=0mm and y=0mm) \n\n\n"
                                     "!! BEFORE !!  you connect.\n\n"
                                     "Incorrect homing will damage the table!\n\n"
                                     "Did you home the XY table?\n\n")
        if answer:
            self.s.ser, succes = self.s.open_serial_connection()
            self.s.ser.write(bytes('$H\n', 'utf-8'))
            if succes:
                self.connect_xy_button['state'] = DISABLED
                self.connect_xy_button['text'] = "XY-table connected"
                print(self.s.xy_connected)


class Camera():
    error = None
    cam = None
    def __init__(self,settings):
        self.s = settings

    def initialize(self):
        self.error, self.cam = gp.gp_camera_new()
        self.error = gp.gp_camera_init(self.cam)


    def event_text(self, event_type):

        if event_type == gp.GP_EVENT_CAPTURE_COMPLETE:
            return "Capture Complete"
        elif event_type == gp.GP_EVENT_FILE_ADDED:
            return "File Added"
        elif event_type == gp.GP_EVENT_FOLDER_ADDED:
            return "Folder Added"
        elif event_type == gp.GP_EVENT_TIMEOUT:
            return "Timeout"
        else:
            return "Unknown Event"

    # def empty_cam_cue(self, camera):
    def empty_cam_cue(self):

        # empty the camera event queue (necessary to prevent camera interface lockups)
        typ, data = self.cam.wait_for_event(200)
        # typ, data = camera.wait_for_event(200)
        while typ != gp.GP_EVENT_TIMEOUT:

            # print("Event: %s, data: %s" % (event_text(typ), data))

            if typ == gp.GP_EVENT_FILE_ADDED:
                fn = os.path.join(data.folder, data.name)
                print("New file: %s" % fn)
            # self.download_file(fn)

            # try to grab another event
            # typ, data = camera.wait_for_event(1)
            typ, data = self.cam.wait_for_event(1)

    def capture_and_get(self):
        pic = self.cam.capture(gp.GP_CAPTURE_IMAGE)
        file = self.cam.file_get(pic.folder, pic.name, gp.GP_FILE_TYPE_NORMAL)
        return file

    def file_get(self, pic):
        file = self.cam.file_get(pic.folder, pic.name, gp.GP_FILE_TYPE_NORMAL)
        return file

    def calc_movement_delay(self, x, y, f):
        """ based on calibration of actual movement time (see settings) xy in mm en speed(F) in mm/min/1.4 """
        if x > y:
            maxd = x
        else:
            maxd = y
        mm_sec = f / self.s.xy_f_corr_fact / 60

        mov_tm = maxd / mm_sec
        # add (2-3) seconds for shaking movement to stabilize, and round up to the nearest second
        mov_tm = mov_tm + self.s.cam_capture_delay
        return mov_tm

class Stickytrap:

    def __init__(self, parent, settings):
        #cv2.ocl.setUseOpenCL(False)  # disable opencl to prevent errors
        # reference the settings object
        self.s = settings
        # create the folderstructure if it does not yet exist
        #self.s.create_safe_path()
        self.pbval = 0

        self.st_coords = self.s.xy_big_st_coords
        self.maxcap = self.s.caps_per_big_st
        self.x = 0
        self.y = 0

        #self.overlap = 30  # (value in mm overlap of pictures)

        self.pbmax = self.maxcap

        self.stthumb_list = self.create_empty_st_list()
        self.stpic_list = []
        self.qr = ""

        self.frame = ttk.Frame(parent, padding="3 3 3 3")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        #ttk.Label(self.frame, text="blaat").grid(row=0, column=0)

        self.pb = ttk.Progressbar(self.frame, orient=HORIZONTAL, length=400, mode='determinate', maximum=self.pbmax)
        self.pb['value'] = 0
        self.pb.grid(row=2, column=0)

        self.strstp_button = Button(self.frame, text='Start imaging', command=self.start)
        self.strstp_button.grid(row=2, column=1, sticky=E)

        self.update_st_grid()
        self.ctr = 0

    def start(self):
        if not self.s.cam_connected or not self.s.xy_connected:
            messagebox.showerror("connection error", "XY-table and/or camera not connected\n"
                                                     "Cannot continue.")
        else:
            self.s.create_safe_path()
            self.pbval = 0
            self.pb['value'] = self.pbval
            self.pb['maximum'] = self.maxcap
            self.strstp_button.configure(text='Stop', command=self.stop)
            self.stpic_list.clear()
            self.stthumb_list.clear()

            global interrupt
            interrupt = False

            # create the folders
            self.s.create_project_sample_path()
            self.ctr = 0
            # invoke the capturenext function via root.after to allow the eventloop to update the interface
            self.toggle_tab_state("disabled")
            root.after(1, self.capture_next)


    def stop(self):

        self.strstp_button.configure(text='Start imaging', command=self.start)
        self.update_st_grid()
        global interrupt
        interrupt = True
        self.pb['value'] = 0
        self.home_xy()
        self.toggle_tab_state("normal")

    def capture_next(self, nextcap=0):

        if nextcap < self.maxcap:

            self.pbval += 1
            self.pb['value'] = self.pbval
            self.x = self.st_coords[nextcap][0]
            self.y = self.st_coords[nextcap][1]
            # root.after(1000)
            print("nextcap: " + str(nextcap) + " xy" + str(self.x) + " " + str(self.y))

            tempfn = "temp_st_pos_" + str(nextcap).zfill(2) + ".jpg"
            self.move_and_capture(self.x, self.y, self.s.xy_f_speed, tempfn)
            self.crop_save_temp_st(self.ctr, tempfn)
            self.ctr += 1

        else:
            #self.stitch_st()
            self.save_images()
            self.pb['value'] = self.pbmax
            print("nextcap: " + str(nextcap))
            self.strstp_button.configure(text='Start imaging', command=self.start)
            # home the xy table
            self.home_xy()
            self.update_st_grid()

            interrupt = True
            self.toggle_tab_state("normal")
            return

        root.after(1, lambda: self.capture_next(nextcap + 1))

    def home_xy(self):
        self.s.ser.write(bytes("G28\n", 'utf-8'))

    def move_and_capture(self, x, y, f, tempfn):
        self.goto_position(x, y, f)
        time.sleep(self.s.cam.calc_movement_delay(x, y, f))
        self.capture_image(tempfn)
        # self.crop_save_wells_old(1, 12)
        # take the pic

    def crop_save_temp_st(self, capnr, tempfn):

        pos_str = "st_pos_" + str(capnr).zfill(2) + ".jpg"
        temp_image = cv2.imread(os.path.join(self.s.safe_temp_path, tempfn))
        #temp_image = cv2.rotate(temp_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        qr = self.detect_qr(temp_image)
        if qr != "":
            self.qr = qr
            print("qr-code detected: " + self.qr)

        #crop = temp_image[2300:5200, 800:3700]
        crop = temp_image
        save_fn = pos_str + ".jpg"
            # add project en sample name to the filename if checked

        #cv2.imwrite(os.path.join(self.s.project_sample_path, save_fn), crop)
        self.stpic_list.append(os.path.join(self.s.safe_temp_path, tempfn))
        st_thumb = cv2.resize(crop, [100, 75], cv2.INTER_NEAREST)
        cv2.imwrite(os.path.join(self.s.safe_temp_path, "thumb_" + save_fn), st_thumb)
        self.stthumb_list.append(os.path.join(self.s.safe_temp_path, "thumb_" + save_fn))

    def save_images(self):

        save_fn = ""
        if self.s.prj_fn_add:
            save_fn = self.s.project_name + "_" + self.s.sample_name + "_" + self.s.sample_nr + "_"
        ## remove qr for now
        #if self.qr != "":
        #    save_fn = save_fn + self.qr + "_"

        for i in range(self.maxcap):
            pos_str = "st_pos_" + str(i).zfill(2)
            temp_fn = "temp_" + pos_str + ".jpg"
            save2_fn = save_fn + self.s.st_posnames[i] + ".jpg"
            os.rename(os.path.join(self.s.safe_temp_path, temp_fn),
                      os.path.join(self.s.project_sample_path, save2_fn))
            print(self.s.project_sample_path)

    def detect_qr(self, img):

        detect = cv2.QRCodeDetector()
        val, pts, st_code = detect.detectAndDecode(img)
        print(val)
        return val

    def stitch_st(self):

        stitcher = cv2.Stitcher.create(cv2.STITCHER_SCANS)
        images = []

        for each in self.stpic_list:
            image = cv2.imread(each)
            images.append(image)
        (status, stitched) = stitcher.stitch(images)

        # if the status is '0', then OpenCV successfully performed image
        # stitching
        if status == 0:
            # write the output stitched image to disk
            #cv2.imwrite("stitch.jpg", stitched)
            # display the output stitched image to our screen
            #stitched = cv2.resize(stitched, [375, 1000], cv2.INTER_NEAREST)
            cv2.imwrite(os.path.join(self.s.project_sample_path, "stitch.jpg"), stitched)
            #cv2.imshow("Stitched", stitched)
            #cv2.waitKey()
        # otherwise the stitching failed, likely due to not enough keypoints)
        # being detected
        else:
            print("[INFO] image stitching failed ({})".format(status))


    def create_empty_st_list(self):
        stthumb_list = list()
        #stthumb_list.append("assets/st/empty_1_h250px.png")
        #stthumb_list.append("assets/st/empty_2_h250px.png")
        #stthumb_list.append("assets/st/empty_3_h250px.png")
        #stthumb_list.append("assets/st/empty_4_h250px.png")

        return stthumb_list

    def update_st_grid(self):
        pic_ctr = 0
        st_layout = ttk.Frame(self.frame, padding="10 10 10 10")
        st_layout.grid(column=0, row=0, sticky=(N, W, E, S))
        root.update_idletasks()

        #rows = ["A", "B", "C", "D", "E"]
        #cols = ["1", "2", "3", " 4", "5"]
        rows = ["1", "2", "3", "4", "5", "6", "7"]
        cols = ["A", "B", "C"]
        nr_rows = 3
        nr_cols = 6

        r = 0
        c = 0

        c1 = 1
        for col in cols:
            ttk.Label(st_layout, text=col).grid(row=r, column=c1)
            c1 += 1
        r += 1
        for row in rows:
            # header
            ttk.Label(st_layout, text=row).grid(row=r, column=c)
            c += 1
            for col in cols:
                fname = self.stthumb_list[pic_ctr]
                pimg = ImageTk.PhotoImage(Image.open(fname))
                label = ttk.Label(st_layout, image=pimg)
                label.image = pimg
                label.grid(row=r, column=c)
                pic_ctr += 1
                # print("## pictr: " + str(pic_ctr) + " " + fname)
                c += 1
            c = 0
            r += 1


        pic_ctr = 0
        #
        #
        # r = 0
        # for pic in self.stthumb_list:
        #     # label plates
        #     #plate_string = "postion: " + str(i + 1)
        #     #ttk.Label(wp_layout, text=plate_string).grid(row=r, column=c, pady=10)
        #     # r += 1
        #     # row header with column titles
        #                 # header
        #     ttk.Label(st_layout, text=str(r)).grid(row=r, column=0)
        #     fname = self.stthumb_list[r]
        #     pimg = ImageTk.PhotoImage(Image.open(fname))
        #     label = ttk.Label(st_layout, image=pimg)
        #     label.image = pimg
        #     label.grid(row=r, column=1)
        #     r += 1

    def goto_position(self, x, y, f):

        x_coord = str(x)
        y_coord = str(y)
        f_val = str(f)
        gcode = 'G0 X' + x_coord + ' Y' + y_coord + ' F' + f_val + '\n'
        # write out gcode to xytabel serial connection
        # ser.write(bytes(gcode, 'utf-8'))
        self.s.ser.write(bytes(gcode, 'utf-8'))
        print(gcode)

    def capture_image(self, picname):
        # take te picture
        file = self.s.cam.capture_and_get()
        file.save(os.path.join(self.s.safe_temp_path, picname))

        ## rotate the file on the disk for correct orientation
        temp_image = cv2.imread(os.path.join(self.s.safe_temp_path, picname))
        temp_image = cv2.rotate(temp_image, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(os.path.join(self.s.safe_temp_path, picname), temp_image)

        # trick to empty the camera cue before nextaction (see github thread from entangle developer .....).
        # Prevents camera crashes.
        self.s.cam.empty_cam_cue()

    def set_overlap(self, overlap):
        self.overlap = overlap

    def toggle_tab_state(self, tabstate="normal"):
        tabs = self.frame.master.master.tabs()
        self.frame.master.master.tab(tabs[0], state=tabstate)
        #self.frame.master.master.tab(tabs[1], state=tabstate)
        # do not toggle well plate tab 2
        self.frame.master.master.tab(tabs[2], state=tabstate)
        self.frame.master.master.tab(tabs[3], state=tabstate)

class Move:

    def __init__(self, parent, settings):

        self.s = settings

        moveframe = ttk.Frame(parent, padding="3 3 3 3")
        moveframe.grid(column=0, row=0, sticky=(N, W, E, S))

        # Grid row 0
        self.num_x = StringVar()
        self.num_y = StringVar()
        self.scale_x_lbl = ttk.Label(moveframe)
        self.scale_y_lbl = ttk.Label(moveframe)
        self.scale_x_lbl.grid(column=0, row=0, sticky=W)
        self.scale_y_lbl.grid(column=1, row=0, sticky=W)
        self.scale_x_lbl['text'] = "x-axis (mm): "
        self.scale_y_lbl['text'] = "y-axis (mm): "

        # # Grid row 1

        ###### ---> dangerous fine grained control with spinbox for development, no boundary check
        # self.x = Spinbox(moveframe, from_=0.00, to=self.s.xy_x_max, increment=.01, textvariable=self.num_x)
        # self.y = Spinbox(moveframe, from_=0.00, to=self.s.xy_x_max, increment=.01, textvariable=self.num_y)
        # self.x.grid(column=0, row=1, sticky=W)
        # self.y.grid(column=1, row=1, sticky=W)
        ############################################

        self.x = ttk.Scale(
            moveframe, orient=HORIZONTAL, length=self.s.xy_x_max,
            from_=0.0, to=self.s.xy_x_max, variable=self.num_x,
            command=self.update_scale_x_lbl)
        self.y = ttk.Scale(
            moveframe, orient=VERTICAL, length=self.s.xy_y_max,
            from_=0.0, to=self.s.xy_y_max, variable=self.num_y,
            command=self.update_scale_y_lbl )
        self.y.grid(column=0, row=1)
        self.x.grid(column=1, row=1, sticky=NW)
        self.y.set(0)
        self.x.set(0)

        self.console = Text(moveframe, bg='black', fg='white', width=40)
        self.console.grid(row=1, column=3, rowspan=10)
        self.console.insert(0.0, '>>> G Code >')
        self.console_line = 1.0

        # Grid row 5
        # home button
        self.home_button = Button(moveframe, text='home', command=self.home_axis)
        self.home_button.grid(row=5, column=0, sticky=W)

        self.go_button = Button(moveframe, text='GO', command=self.goto_position)
        self.go_button.grid(row=5, column=2, sticky=E)

        # Grid row 6


        # Grid row 7
        for child in moveframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def update_scale_y_lbl(self, val):
        val = float(val)
        val = round(val, 1)
        val = str(val)
        self.scale_y_lbl['text'] = "y-axis: " + val + " mm"

    def update_scale_x_lbl(self, val):
        val = float(val)
        val = round(val, 1)
        val = str(val)
        self.scale_x_lbl['text'] = "x-axis at: " + val + " mm"

    def home_axis(self):
        if not self.s.xy_connected:
            messagebox.showerror("connection error", "XY-table not connected\n"
                                                     "Cannot continue.")
        else:
            self.print_gcode('G28\n')
            #self.print_gcode('$H\n')
            self.x.set(value=0.0)
            self.y.set(value=0.0)

    def goto_position(self):

        if not self.s.xy_connected:
            messagebox.showerror("connection error", "XY-table not connected\n"
                                                     "Cannot continue.")
        else:
            x_coord = str(round(float(self.num_x.get()), 2))
            y_coord = str(round(float(self.num_y.get()), 2))
            self.print_gcode('G1 X' + x_coord + ' Y' + y_coord + ' F' + str(self.s.xy_f_speed) + '\n')

    def print_gcode(self, gcode):
        self.console.insert(self.console_line, gcode)
        self.console.yview_pickplace("end")
        # ser.write(bytes(gcode, 'utf-8'))
        self.s.ser.write(bytes(gcode, 'utf-8'))
        print(gcode)
        print(bytes(gcode, 'utf-8'))
        self.console_line += 1

class Help:

    def __init__(self, parent):
        frame = ttk.Frame(parent, padding="20 20 20 20")
        frame.grid(column=0, row=0, sticky=(N, W, E, S))

        ttk.Label(frame, text="Taskforce Kleine Biodiversiteit\n\n"
                              "Lectorate Bees and Biodiversity\n"
                              "Van Hall Larenstein University of applied sciences\n\n"
                              "For now you are on your own ;-)\n"
                              "If you really need help try the readme").grid(row=0, column=0, sticky=NW)
        link1 = ttk.Label(frame, text="https://github.com/Taskforce-Biodiversity/InsectImager#readme ")
        link1.grid(row=1, column=0, sticky=NW)
        link1.bind("<Button-1>", lambda e: self.open_url("https://github.com/Taskforce-Biodiversity/InsectImager#readme"))
        link2 = ttk.Label(frame, text="https://github.com/Taskforce-Biodiversity/InsectImager/issues")
        link2.grid(row=2, column=0, sticky=(W, E))
        link2.bind("<Button-1>", lambda e: self.open_url("https://github.com/Taskforce-Biodiversity/InsectImager/issues "))

        fname = "assets/tf_kbd_gst.jpg"
        pimg = ImageTk.PhotoImage(Image.open(fname))
        imglabel = ttk.Label(frame, image=pimg)
        imglabel.image = pimg
        imglabel.grid(row=0, column=1, rowspan=3)

    def open_url(self, url):
        webbrowser.open_new_tab(url)


if __name__ == '__main__':
    try:
        root = Tk()
        Main(root)
        interrupt = False

    finally:
        print("bye")
