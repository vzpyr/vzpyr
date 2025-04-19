import os
import datetime

def rename():
    try:
        modification_times = {}
        for filename in os.listdir():
            if os.path.isfile(filename) and filename != os.path.basename(__file__):
                try:
                    modification_time = os.path.getmtime(filename)
                    modification_date = datetime.datetime.fromtimestamp(modification_time)
                    base_new_filename = modification_date.strftime("%d.%m.%Y - %H-%M")
                    root, ext = os.path.splitext(filename)
                    if base_new_filename in modification_times:
                        modification_times[base_new_filename] += 1
                        new_filename = f"{base_new_filename} - {modification_times[base_new_filename]}"
                    else:
                        modification_times[base_new_filename] = 1
                        new_filename = base_new_filename
                    if new_filename + ext != filename:
                        os.rename(filename, new_filename + ext)
                        print(f"renamed '{filename}' to '{new_filename + ext}'")
                    else:
                        print(f"skipped '{filename}'")

                except OSError as file_error:
                    print(f"couldn't rename '{filename}': {file_error}")

    except FileNotFoundError:
        print("directory not found")
    except OSError as directory_error:
        print(f"directory error: {directory_error}")

if __name__ == "__main__":
    rename()