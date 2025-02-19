import pyautogui
import time

movement = {
    'click_layer': '-2341,760',
    'exprot': '-2075,1229',
    'save_feature': '-1966,1235',
    'file_name': '-935,301',
    'ok': '-1119,1993'
}

def perform_movement(action, click_type='click'):  # Added click_type parameter
    if action in movement:
        coords_str = movement[action]
        x_str, y_str = coords_str.split(',')
        try:
            x = int(x_str)
            y = int(y_str)
            print(f"Moving to X: {x}, Y: {y}")
            pyautogui.moveTo(x, y, duration=0.25)

            if click_type == 'click':
                pyautogui.click()
            elif click_type == 'right_click':
                pyautogui.rightClick()  # Perform right-click
            elif click_type == 'double_click':
                pyautogui.doubleClick()
            else:
                print(f"Invalid click type: {click_type}")

            time.sleep(1)
        except ValueError:
            print(f"Invalid coordinates for {action}: {coords_str}")
    else:
        print(f"Action '{action}' not found in movement dictionary.")

# Example usage:
perform_movement('click_layer', 'right_click')  # Right-click for 'click_layer'
perform_movement('exprot')  # Default click
perform_movement('save_feature')
perform_movement('file_name')
pyautogui.typewrite("my_shapefile.shp")  # Example filename
pyautogui.press('enter')
time.sleep(1)
perform_movement('ok')


# Example of how you could iterate through all actions:
# for action in movement:
#    perform_movement(action)