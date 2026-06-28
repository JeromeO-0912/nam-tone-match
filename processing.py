import time
import shutil

def run_tone_match(di_path, reference_path, output_path):
    # Simulate processing time
    time.sleep(5)
    # For demonstration, just copy the reference file to the output path
    shutil.copy(di_path, output_path)
    return output_path