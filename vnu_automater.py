import os
import subprocess
import shlex
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import shutil

DEVELOPMENT_DIR = "/Users/Jamie/Google Drive/CS4/WebTech/development/html/"
PRODUCTION_DIR = "/Users/Jamie/Google Drive/CS4/WebTech/"

def errorBeep():
    # terminal alert
    print('\a')
    # audible alert
    duration = 0.2  # second
    freq = 440  # Hz
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))

def successBeep():
    # terminal alert
    print('\a')
    # audible alert
    duration = 0.05  # second
    freq0 = 600  # Hz
    freq1 = 650  # Hz
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq0))
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq1))


class vnuValidation(PatternMatchingEventHandler):

    def extractTargetPath(self, event):
        if event.event_type == 'moved':
            return event.dest_path
        else:
            return event.src_path

    def runValidation(self, event):
        target_file = os.path.split(self.extractTargetPath(event)) [1]


        # new stuff
        target_file_path = self.extractTargetPath(event)
        splits = target_file_path.split('/')
        mirror_file_path = '/'.join(splits[8:])
        # new stuff


        # run validation
        target_path = "/Users/Jamie/Google\ Drive/CS4/WebTech/development/html/" + mirror_file_path
        arg_str = "java -jar /Users/Jamie/Google\ Drive/CS4/WebTech/validation/dist/vnu.jar " + target_path
        args = shlex.split(arg_str)
        p_vnu = subprocess.run(args, stderr=subprocess.PIPE)
        console_output = p_vnu.stderr.decode('utf-8')

        if len(console_output) == 0:
            # HTML passed - copy to public dir
            source_path = DEVELOPMENT_DIR + mirror_file_path
            destination_path = PRODUCTION_DIR +mirror_file_path
            shutil.copyfile(source_path, destination_path)
            print("Pass: %s" %(target_file), '\n')
            successBeep()
        else:
            # HTML failed
            errorBeep()
            print("Error in: %s" %(target_file),'\n')
            print(console_output)


    def on_created(self, event):
        self.runValidation(event)


    def on_modified(self, event):
        self.runValidation(event)

    def on_moved(self, event):
        self.runValidation(event)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else DEVELOPMENT_DIR

    event_handler = vnuValidation(patterns=["*.html"], ignore_patterns=[], ignore_directories=False)

    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
